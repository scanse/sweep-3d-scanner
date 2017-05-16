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
const SCANNER_SCRIPT_DIR = path.join(__dirname, (GLOBAL_APPLICATION_VARIABLE_bUseDummy ? "../dummy_scanner" : "../scanner"));
// Python script paths
const PY_SCANNER_LIMIT_SWITCH_SCRIPT = path.join(SCANNER_SCRIPT_DIR, "scanner_limit_switch.py");
const PY_SCANNER_BASE_SCRIPT = path.join(SCANNER_SCRIPT_DIR, "scanner_base.py");
const PY_SWEEP_TEST_SCRIPT = path.join(SCANNER_SCRIPT_DIR, "sweep_test.py");
const PY_RELEASE_MOTOR_SCRIPT = path.join(SCANNER_SCRIPT_DIR, "release_motors.py");

// Backend variables
var currentTestStatus = null;
var currentTestStatusUpdateCounter = 0;

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
        let statusObj = currentTestStatus;
        if (!statusObj)
            statusObj = {};
        statusObj.counter = currentTestStatusUpdateCounter;
        res.send(statusObj);
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
    currentTestStatus = null;
    currentTestStatusUpdateCounter = 0;

    let pyScriptToExecute = null;
    switch (Number(params.test)) {
        case TestTypeEnum.SCANNER_LIMIT_SWITCH:
            console.log("Running scanner limit switch test");
            pyScriptToExecute = PY_SCANNER_LIMIT_SWITCH_SCRIPT;
            break;
        case TestTypeEnum.SCANNER_BASE:
            console.log("Running scanner base test");
            pyScriptToExecute = PY_SCANNER_BASE_SCRIPT;
            break;
        case TestTypeEnum.SWEEP_TEST:
            console.log("Running sweep test");
            pyScriptToExecute = PY_SWEEP_TEST_SCRIPT;
            break;
        case TestTypeEnum.RELEASE_MOTOR:
            console.log("Running release motor");
            pyScriptToExecute = PY_RELEASE_MOTOR_SCRIPT;
            break;
        default:
            currentTestStatus = {
                'type': "update",
                'status': "failed",
                'msg': `Failed to determine test type, or test type does not exist.`
            }
            console.log("Unknown test");
            return;
            break;
    }

    const scriptExecution = spawn(PYTHON_EXECUTABLE, [pyScriptToExecute]);

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
        currentTestStatus = jsonObj;
        currentTestStatusUpdateCounter++;

        // If the update indicates a failure, terminate the child process in case it is hanging
        if (currentTestStatus.status === 'failed') {
            setTimeout(() => {
                scriptExecution.kill();
            }, 500);
        }
    });

    // Handle error output
    scriptExecution.stderr.on('data', (data) => {
        // note the status as a failure, packaged with the error message
        currentTestStatus = {
            'type': "update",
            'status': "failed",
            'msg': uint8arrayToString(data) //convert the Uint8Array to a readable string
        }
        // kill the child process in case it is hanging
        setTimeout(() => {
            scriptExecution.kill();
        }, 500);
        console.log(uint8arrayToString(data));
    });

    // Handle exit
    scriptExecution.on('exit', (code) => {
        console.log("Process quit with code : " + code);
        // Kill the process on abnormal exit, in case it is hanging
        if (Number(code) !== 0)
            scriptExecution.kill();
    });

    // Handle close
    scriptExecution.on('close', (code) => {
        console.log("Process closed with code : " + code);
        // Kill the process on abnormal close, in case it is hanging
        if (Number(code) !== 0)
            scriptExecution.kill();
    });
}

module.exports = app;