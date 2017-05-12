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
const exec = require('child_process').exec;

// Util File Include (defines enums + helper methods)
eval.apply(global, [fs.readFileSync(path.join(__dirname, '../public/javascript/utils.js')).toString()]);

// Provide the path of the python executable, if python is available as environment variable then you can use only "python"
const PYTHON_EXECUTABLE = "python";
// Directory for python scanner scripts
const SCANNER_SCRIPT_DIR = path.join(__dirname, (GLOBAL_APPLICATION_VARIABLE_bUseDummy ? "../dummy_scanner" : "../scanner"));
// Python script path
const PY_SCAN_SCRIPT = path.join(SCANNER_SCRIPT_DIR, "scanner.py");
// Backend variables
var currentScannerStatus = null;

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
        res.render('scan');
    })

// request an update
router.route('/request_update')
    .get(function (req, res, next) {
        let statusObj = currentScannerStatus;
        res.send(statusObj);
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


// Start the scanner script
//TODO: convert over to using the settings enums from the utils file
function performScan(params) {
    currentScannerStatus = null;

    // strip away any directory or extension, then add .csv extension explicitly
    let filename = path.parse(params.file_name).name + '.csv';

    const scriptExecution = spawn(PYTHON_EXECUTABLE, [
        PY_SCAN_SCRIPT,
        `--motor_speed=${params.motor_speed}`,
        `--sample_rate=${params.sample_rate}`,
        `--angular_range=${params.angular_range}`,
        `--output=${filename}`
    ]);

    // Handle normal output
    scriptExecution.stdout.on('data', (data) => {
        let jsonObj = JSON.parse(uint8arrayToString(data));
        console.log(jsonObj);

        // Store the update as the current status
        currentScannerStatus = jsonObj;

        // If the update indicates a failure, terminate the child process in case it is hanging
        if (currentScannerStatus.status === 'failed') {
            let processId = scriptExecution.pid;
            setTimeout(() => {
                killChildProcess(processId);
            }, 500);
        }
    });

    // Handle error output
    scriptExecution.stderr.on('data', (data) => {
        // note the status as a failure, packaged with the error message
        currentScannerStatus = {
            'type': "update",
            'status': "failed",
            'msg': uint8arrayToString(data) //convert the Uint8Array to a readable string
        }
        // kill the child process in case it is hanging
        let processId = scriptExecution.pid;
        setTimeout(() => {
            killChildProcess(processId);
        }, 500);
        console.log(uint8arrayToString(data));
    });

    // Handle exit
    scriptExecution.on('exit', (code) => {
        console.log("Process quit with code : " + code);
        // Kill the process on abnormal exit, in case it is hanging
        if (Number(code) !== 0)
            killChildProcess(scriptExecution.pid);
    });

    // Handle close
    scriptExecution.on('close', (code) => {
        console.log("Process closed with code : " + code);
        // Kill the process on abnormal close, in case it is hanging
        if (Number(code) !== 0)
            killChildProcess(scriptExecution.pid);
    });
}

// kills a process by its process id
function killChildProcess(pid) {
    exec(`kill ${pid}`, (error, stdout, stderr) => {
        if (error)
            console.error(`Error killing child process: ${error}`);
    });
}

module.exports = app;