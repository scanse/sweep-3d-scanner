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

// Provide the path of the python executable, if python is available as environment variable then you can use only "python"
const pythonExecutable = "python";
// Directory for python scanner scripts
const scanner_script_dir = GLOBAL_APPLICATION_VARIABLE_bUseDummy ? "./dummy_scanner" : "./scanner";
// Python script path
const PY_scan_script = path.join(scanner_script_dir, "scanner.py");
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
        var data = req.query;
        performScan(data);

        res.send({
            bSumittedScanRequest: true,
            //errorMsg: "testing error msg...",
            scanParams: data //FIXME: currently just sending the same data back
        });
    })


// Start the scanner script
function performScan(params) {
    currentScannerStatus = null;

    // strip away any directory or extension, then add .csv extension explicitly
    let filename = path.parse(params.file_name).name + '.csv';

    const scriptExecution = spawn(pythonExecutable, [
        PY_scan_script,
        `--motor_speed=${params.motor_speed}`,
        `--sample_rate=${params.sample_rate}`,
        `--angular_range=${params.angular_range}`,
        `--output=${filename}`
    ]);

    // Handle normal output
    scriptExecution.stdout.on('data', (data) => {
        let jsonObj = JSON.parse(uint8arrayToString(data));
        console.log(jsonObj);
        currentScannerStatus = jsonObj;
    });

    // Handle error output
    scriptExecution.stderr.on('data', (data) => {
        // As said before, convert the Uint8Array to a readable string.
        console.log(uint8arrayToString(data));
    });

    // Handle exit
    scriptExecution.on('exit', (code) => {
        console.log("Process quit with code : " + code);
    });

    // Handle close
    scriptExecution.on('close', (code) => {
        console.log("Process closed with code : " + code);
    });
}

// Function to convert an Uint8Array to a string
function uint8arrayToString(data) {
    return String.fromCharCode.apply(null, data);
}

module.exports = app;