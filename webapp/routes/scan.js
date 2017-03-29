/**
 * Scan Route:
 * This contains all the route and backend logic for the scan page.
 */
// Module Includes
const path = require('path');
const fs = require('fs');
const express = require('express');
const bodyParser = require('body-parser');


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

var router = express.Router();
app.use(router);

router.route('/')
    .post(function (req, res) {
        // submitted scan form, now initiating a scan
        var scan_params = {};

        // read the scan parameters from the posted form
        scan_params.motor_speed = Number(req.body.input_MotorSpeed);
        scan_params.sample_rate = Number(req.body.input_SampleRate);
        scan_params.angular_range = Number(req.body.input_ScanType);
        scan_params.file_name = req.body.input_FileName;
        scan_params.bIsScanning = true;

        // command the scanner to perform a scan
        performScan(scan_params);

        // inform the user that a scan is in progress
        res.render('scan', scan_params);
    })
    .get(function (req, res) {
        // navigated to this page, want to present the scan form
        let page_params = {
            bIsScanning : false,
            form_options : ScanFormOptions
        };
        res.render('scan', page_params);
    })

const ScanFormOptions = {
    'AvailableScanTypes' : {
        'Full Scan (360 deg)': 180,
        'Half Scan (180 deg)': 90,
        'Partial Scan (90 deg)': 45,
        'Partial Scan (30 deg)': 15
    },
    'AvailableMotorSpeeds' : {
        '1 Hz': 1,
        '2 Hz': 2,
        '3 Hz': 3
    },
    'AvailableSampleRates' : {
        '500 Hz': 500,
        '750 Hz': 750,
        '1000 Hz': 1000
    }
};


var zmq = require('zeromq');

var cmd_socket = zmq.socket('pub');

// publish on port 3000
cmd_socket.bindSync('tcp://*:3000');
console.log('Publisher bound to port 3000');

function performScan(params) {
  console.log('sending a multipart message envelope');
  console.log(JSON.stringify(params));
  cmd_socket.send(['perform_scan', JSON.stringify(params)]);
}

process.on('SIGINT', function () {
  cmd_socket.close();
  process.exit();
});


/*
var zmq = require('zeromq');
var protobuf = require('protobufjs');
var cmd_socket = zmq.socket('pub');

// publish on port 3000
cmd_socket.bindSync('tcp://*:3000');
console.log('Publisher bound to port 3000');

var CommandMessage;
protobuf.load("./communication/scanner.proto", function (err, root) {
    if (err)
        throw err;

    // Obtain a message type
    CommandMessage = root.lookup("scannerpackage.CommandMessage");
});

process.on('SIGINT', function () {
    cmd_socket.close();
    process.exit();
});

function performScan(params) {
    console.log('sending a multipart message envelope');
    console.log(params);
    // Create a new message
    var message = CommandMessage.create({ 
        cmdType : "start_scan",
        angularRange : params.angular_range,
        motorSpeed : params.motor_speed,
        sampleRate : params.sample_rate,
        fileName : params.file_name
    });

    // Verify the message if necessary (i.e. when possibly incomplete or invalid)
    var errMsg = CommandMessage.verify(message);
    if (errMsg)
        throw Error(errMsg);

    // Encode a message to an Uint8Array (browser) or Buffer (node)
    var buffer = CommandMessage.encode(message).finish();

    console.log(buffer);
    console.log(`Buffer: ${buffer}`);

    // Send the buffer over the wire
    cmd_socket.send(['CmdMsg', buffer]);
};
*/
module.exports = app;