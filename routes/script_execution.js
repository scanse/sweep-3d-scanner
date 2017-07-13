/**
 * Script Execution Route:
 * Contains all the route and backend logic for running python scripts.
 */

// Module Includes
const path = require('path');
const fs = require('fs');
const express = require('express');
const bodyParser = require('body-parser');
const spawn = require('child_process').spawn;

// Util File Include (defines enums + helper methods)
eval.apply(global, [fs.readFileSync(path.join(__dirname, '../public/javascript/utils.js')).toString()]);

// Provide the path of the python executable, if python is available as environment variable then you can use only "python"
const PYTHON_EXECUTABLE = "python";
// Directory for python scanner scripts
const SCANNER_SCRIPT_DIR = path.join(__dirname, (GLOBAL_APPLICATION_VARIABLE_bUseDummy ? "../scanner/dummy" : "../scanner"));
// Python script paths
const PY_SCANNER_LIMIT_SWITCH_SCRIPT = path.join(SCANNER_SCRIPT_DIR, "scanner_limit_switch.py");
const PY_SCANNER_BASE_SCRIPT = path.join(SCANNER_SCRIPT_DIR, "scanner_base.py");
const PY_SWEEP_TEST_SCRIPT = path.join(SCANNER_SCRIPT_DIR, "sweep_test.py");
const PY_CLEANUP_SCRIPT = path.join(SCANNER_SCRIPT_DIR, "cleanup.py");
const PY_SCAN_SCRIPT = path.join(SCANNER_SCRIPT_DIR, "scanner.py");

// Backend variables
let CURRENT_SCRIPT_EXECUTION = null;
var updateQueue = [];

// Setup express
var app = express();
//gives your app the ability to parse JSON
app.use(bodyParser.json());
//allows app to read data from URLs (GET requests)
app.use(bodyParser.urlencoded({ extended: false }));

// create a router to handle any routing
var router = express.Router();
app.use(router);

// this route doesn't have a front end or a main page
router.route('/')
    .all(function (req, res, next) {
        console.log('Someone made a request!');
        next();
    })
    .get(function (req, res, next) {
        console.log('received get');
    })
    .post(function (req, res, next) {
        console.log('received post');
    })

// request an update
router.route('/request_update')
    .get(function (req, res, next) {
        // stringify the array of updates
        let updatesSinceLastRequest = JSON.stringify(updateQueue);
        // clear the array of updates
        updateQueue = [];
        // send the stringified version
        res.send(updatesSinceLastRequest);
    })

// submit a scan request
router.route('/request_script_execution')
    // FIXME: this should be a POST
    .get(function (req, res, next) {
        let data = req.query; // data carries the scan params
        switch (data.type) {
            case 'scan_request':
                performScan(data.params);
                break;
            case 'test_request':
                performTest(data.params);
                break;
            default:
                res.send({
                    bSumittedRequest: false,
                    errorMsg: `Unknown request type: ${data.type}.` //FIXME: currently just sending the same data back
                });
                return;
        }

        res.send({
            bSumittedRequest: true,
            params: data.params //FIXME: currently just sending the same data back
        });
    })

// request an update 
router.route('/cancel_scan')
    .post(function (req, res, next) {
        cancelScript("Scan cancelled by user.");
        res.send("success");
    })

// submit a scan request
router.route('/submit_test_request')
    .get(function (req, res, next) {
        let data = req.query; // data carries the test params
        performTest(data);

        res.send({
            bSumittedTestRequest: true,
            testParams: data //FIXME: currently just sending the same data back
        });
    })


function cancelScript(msg) {
    // clear the array of updates
    updateQueue = [];

    // Cancel the scan
    forcefullyKillChildProcess(CURRENT_SCRIPT_EXECUTION);
    cleanupAfterUnexpectedShutdown();

    // clear the array of updates in case more made it in during shutdown
    updateQueue = [];

    // note the status as a failure, packaged with an error message
    updateQueue.push({
        'type': "update",
        'status': "failed",
        'msg': msg
    });
}

// Start the scanner script
//TODO: convert over to using the settings enums from the utils file
function performScan(params) {
    // strip away any directory or extension, then add .csv extension explicitly
    let filename = path.parse(params.file_name).name + '.csv';
    let argArray = [
        PY_SCAN_SCRIPT,
        `--motor_speed=${params.motor_speed}`,
        `--sample_rate=${params.sample_rate}`,
        `--angular_range=${params.angular_range}`,
        `--output=${filename}`
    ];
    executeScript(argArray);
}

function executeScript(args) {
    // reset the update queue
    updateQueue = [];

    // launch the script
    CURRENT_SCRIPT_EXECUTION = spawn(PYTHON_EXECUTABLE, args);

    // Handle normal output
    CURRENT_SCRIPT_EXECUTION.stdout.on('data', (data) => {
        let jsonObj = null;
        try {
            jsonObj = JSON.parse(uint8arrayToString(data));
        }
        catch (e) {
            console.error(e);
            return;
        }
        console.log(jsonObj);

        // Store the update as the current status
        updateQueue.push(jsonObj);

        // If the update indicates a failure
        if (jsonObj.status === 'failed')
            guaranteeShutdown();
    });

    // Handle error output
    CURRENT_SCRIPT_EXECUTION.stderr.on('data', (data) => {
        // note the status as a failure, packaged with the error message
        updateQueue.push({
            'type': "update",
            'status': "failed",
            'msg': uint8arrayToString(data) //convert the Uint8Array to a readable string
        });

        console.error(uint8arrayToString(data));
        guaranteeShutdown();
    });

    // Handle exit... 
    // When process could not be spawned, could not be killed or sending a message to child process failed
    // Note: the 'exit' event may or may not fire after an error has occurred.
    CURRENT_SCRIPT_EXECUTION.on('exit', (code) => {
        console.log("Child process quit with code : " + code);
    });
}

// Start the appropriate scanner script
function performTest(params) {

    let args = getChildProcessArgs(Number(params.test));

    if (!args || args.length === 0) {
        updateQueue = [];
        updateQueue.push({
            'type': "update",
            'status': "failed",
            'msg': `Failed to determine test type, or test type does not exist.`
        });
        console.error("Unknown test");
        return;
    }

    executeScript(args);
}

// returns an array with the appropriate test script and any arguments
function getChildProcessArgs(testType) {
    let pyScriptToExecute = null;
    switch (testType) {
        case TestTypeEnum.SCANNER_LIMIT_SWITCH:
            console.log("Running scanner limit switch test");
            pyScriptToExecute = [PY_SCANNER_LIMIT_SWITCH_SCRIPT];
            break;
        case TestTypeEnum.SCANNER_BASE:
            console.log("Running scanner base test");
            pyScriptToExecute = [PY_SCANNER_BASE_SCRIPT];
            break;
        case TestTypeEnum.SWEEP_TEST:
            console.log("Running sweep test");
            pyScriptToExecute = [PY_SWEEP_TEST_SCRIPT];
            break;
        case TestTypeEnum.RELEASE_MOTOR:
            console.log("Running release motor");
            pyScriptToExecute = [PY_CLEANUP_SCRIPT, "--release_motor"];
            break;
        default:
            break;
    }
    return pyScriptToExecute;
}

function guaranteeShutdown() {
    // Allow time for script to try and shutdown
    // Then kill the process in case it is hanging
    setTimeout(() => {
        console.log("Doublechecking child process is dead...");
        if (typeof CURRENT_SCRIPT_EXECUTION !== 'undefined' && CURRENT_SCRIPT_EXECUTION) {
            console.log("Scan process is still alive... attempting kill + cleanup again.");
            forcefullyKillChildProcess(CURRENT_SCRIPT_EXECUTION);
            cleanupAfterUnexpectedShutdown();
        }
    }, 500);
}

// if process is still alive, try to kill it
function forcefullyKillChildProcess(scriptExecution) {
    //FIXME this might have to be a more forceful kill using exec module and the PID
    if (typeof scriptExecution !== 'undefined' && scriptExecution) {
        console.log("Attempting to forcefully kill child process...");
        scriptExecution.kill();
    }
    else {
        console.log("Cannot forcefully kill child process as it does not exist, or has already been already killed.")
    }
}

function cleanupAfterUnexpectedShutdown() {
    console.log("Spawning cleanup process...");
    const scriptExecution = spawn(PYTHON_EXECUTABLE, [
        PY_CLEANUP_SCRIPT,
        "--release_motor",
        "--idle_sweep"
    ]);

    // Handle normal output
    scriptExecution.stdout.on('data', (data) => {
        let jsonObj = null;
        try {
            jsonObj = JSON.parse(uint8arrayToString(data));
        }
        catch (e) {
            console.error(e);
            return;
        }
        console.log(jsonObj);
    });

    // Handle error output
    scriptExecution.stderr.on('data', (data) => {
        console.error(uint8arrayToString(data)); //convert the Uint8Array to a readable string

        // Allow time for script to try and shutdown
        // Then kill the child process in case it is hanging
        setTimeout(() => {
            forcefullyKillChildProcess(scriptExecution);
        }, 500);
    });

    // Handle exit
    scriptExecution.on('exit', (code) => {
        console.log("Cleanup process quit with code : " + code);
        // Kill the process on abnormal exit, in case it is hanging
        //FIXME this might have to be a more forceful kill using exec module and the PID
        if (code !== null && Number(code) !== 0)
            forcefullyKillChildProcess(scriptExecution);
    });
}

module.exports = app;