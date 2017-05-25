/**
 * Component Testing Route:
 * Contains all the route and backend logic for the component testing page.
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

// Backend variables
var updateQueue = [];

// Setup express
var app = express();
//gives your app the ability to parse JSON
app.use(bodyParser.json());
//allows app to read data from URLs (GET requests)
app.use(bodyParser.urlencoded({ extended: false }));

//set the views folder and the view engine
app.set('views', path.join(__dirname, '../views'));
app.set('view engine', 'jade');

//tells app to use the /public directory where stylesheets and scripts are stored
app.use(express.static(path.join(__dirname, '../public')));

// create a router to handle any routing
var router = express.Router();
app.use(router);

// render the main scan page
router.route('/')
    .get(function (req, res) {
        res.render('component_testing');
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
router.route('/submit_test_request')
    .get(function (req, res, next) {
        let data = req.query; // data carries the test params
        performTest(data);

        res.send({
            bSumittedTestRequest: true,
            testParams: data //FIXME: currently just sending the same data back
        });
    })

// Start the appropriate scanner script
function performTest(params) {
    updateQueue = [];

    let pyScriptToExecute = getChildProcessArgs(Number(params.test));

    if (!pyScriptToExecute || pyScriptToExecute.length === 0) {
        updateQueue.push({
            'type': "update",
            'status': "failed",
            'msg': `Failed to determine test type, or test type does not exist.`
        });
        console.log("Unknown test");
        return;
    }

    const scriptExecution = spawn(PYTHON_EXECUTABLE, pyScriptToExecute);

    // Handle normal output
    scriptExecution.stdout.on('data', (data) => {
        console.log(uint8arrayToString(data));
        let jsonObj = null;
        try {
            jsonObj = JSON.parse(uint8arrayToString(data));
        }
        catch (e) {
            console.log(e);
            return;
        }
        console.log(jsonObj);

        // Store the update as the current status
        updateQueue.push(jsonObj);

        // If the update indicates a failure
        if (jsonObj.status === 'failed')
            guaranteeShutdown(scriptExecution);
    });

    // Handle error output
    scriptExecution.stderr.on('data', (data) => {
        // note the status as a failure, packaged with the error message
        updateQueue.push({
            'type': "update",
            'status': "failed",
            'msg': uint8arrayToString(data) //convert the Uint8Array to a readable string
        });
        guaranteeShutdown(scriptExecution);
        console.log(uint8arrayToString(data));
    });

    // Handle exit... 
    // When process could not be spawned, could not be killed or sending a message to child process failed
    // Note: the 'exit' event may or may not fire after an error has occurred.
    scriptExecution.on('exit', (code) => {
        console.log("Process quit with code : " + code);
        // Kill the process on abnormal exit, in case it is hanging
        if (Number(code) !== 0)
            guaranteeShutdown(scriptExecution);
    });
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
            pyScriptToExecute = [PY_CLEANUP_SCRIPT, "--release_motor=True"];
            break;
        default:
            break;
    }
    return pyScriptToExecute;
}

function guaranteeShutdown(scriptExecution) {
    // Allow time for script to try and shutdown
    // Then kill the process in case it is hanging
    setTimeout(() => {
        forcefullyKillChildProcess(scriptExecution);
        cleanupAfterUnexpectedShutdown();
    }, 500);
}

// if process is still alive, try to kill it
function forcefullyKillChildProcess(scriptExecution) {
    //FIXME this might have to be a more forceful kill using exec module and the PID
    if (typeof scriptExecution !== 'undefined' && scriptExecution)
        scriptExecution.kill();
}

function cleanupAfterUnexpectedShutdown() {

    const scriptExecution = spawn(PYTHON_EXECUTABLE, [
        PY_CLEANUP_SCRIPT,
        "--release_motor=True",
        "--idle_sweep=True"
    ]);

    // Handle normal output
    scriptExecution.stdout.on('data', (data) => {
        let jsonObj = null;
        try {
            jsonObj = JSON.parse(uint8arrayToString(data));
        }
        catch (e) {
            console.log(e);
            return;
        }
        console.log(jsonObj);
    });

    // Handle error output
    scriptExecution.stderr.on('data', (data) => {
        console.log(uint8arrayToString(data)); //convert the Uint8Array to a readable string

        // Allow time for script to try and shutdown
        // Then kill the child process in case it is hanging
        setTimeout(() => {
            forcefullyKillChildProcess(scriptExecution);
        }, 500);
        console.log(uint8arrayToString(data));
    });

    // Handle exit
    scriptExecution.on('exit', (code) => {
        console.log("Process quit with code : " + code);
        // Kill the process on abnormal exit, in case it is hanging
        //FIXME this might have to be a more forceful kill using exec module and the PID
        if (Number(code) !== 0)
            forcefullyKillChildProcess(scriptExecution);
    });
}

module.exports = app;