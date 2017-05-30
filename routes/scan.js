/**
 * Scan Route:
 * Contains all the route and backend logic for the scan page.
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
// Python script path
const PY_SCAN_SCRIPT = path.join(SCANNER_SCRIPT_DIR, "scanner.py");
const PY_CLEANUP_SCRIPT = path.join(SCANNER_SCRIPT_DIR, "cleanup.py");

// Backend variables
let scanScriptExecution = null;
let updateQueue = [];

// Setup express
let app = express();
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
let router = express.Router();
app.use(router);

// render the main scan page
router.route('/')
    .get(function (req, res) {
        res.render('scan');
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
router.route('/submit_scan_request')
    .get(function (req, res, next) {
        let data = req.query; // data carries the scan params
        performScan(data);

        res.send({
            bSumittedScanRequest: true,
            scanParams: data //FIXME: currently just sending the same data back
        });
    })

// request an update
router.route('/cancel_scan')
    .get(function (req, res, next) {
        console.log("Received request to cancel scan...");
        cancelScan();
    })

function cancelScan() {
    // clear the array of updates
    updateQueue = [];

    // Cancel the scan
    forcefullyKillChildProcess(scanScriptExecution);
    cleanupAfterUnexpectedShutdown();

    // clear the array of updates in case more made it in during shutdown
    updateQueue = [];

    // note the status as a failure, packaged with an error message
    updateQueue.push({
        'type': "update",
        'status': "failed",
        'msg': "Scan cancelled by user."
    });
}

// Start the scanner script
//TODO: convert over to using the settings enums from the utils file
function performScan(params) {
    updateQueue = [];

    // strip away any directory or extension, then add .csv extension explicitly
    let filename = path.parse(params.file_name).name + '.csv';

    scanScriptExecution = spawn(PYTHON_EXECUTABLE, [
        PY_SCAN_SCRIPT,
        `--motor_speed=${params.motor_speed}`,
        `--sample_rate=${params.sample_rate}`,
        `--angular_range=${params.angular_range}`,
        `--output=${filename}`
    ]);

    // Handle normal output
    scanScriptExecution.stdout.on('data', (data) => {
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
    scanScriptExecution.stderr.on('data', (data) => {
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
    scanScriptExecution.on('exit', (code) => {
        console.log("Scan process quit with code : " + code);
    });
}

function guaranteeShutdown() {
    // Allow time for script to try and shutdown
    // Then kill the process in case it is hanging
    setTimeout(() => {
        console.log("Doublechecking scan process is dead...");
        if (typeof scanScriptExecution !== 'undefined' && scanScriptExecution) {
            console.log("Scan process is still alive... attempting kill + cleanup again.");
            forcefullyKillChildProcess(scanScriptExecution);
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