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
        let statusObj = currentScannerStatus;
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
            console.log("Unknown test");
            return;
            break;
    }

    const scriptExecution = spawn(PYTHON_EXECUTABLE, [pyScriptToExecute]);

    // Handle normal output
    scriptExecution.stdout.on('data', (data) => {
        console.log(uint8arrayToString(data));
        // let jsonObj = JSON.parse(uint8arrayToString(data));
        // console.log(jsonObj);
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

module.exports = app;