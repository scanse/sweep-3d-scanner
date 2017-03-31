/**
 * Scan Route:
 * This contains all the route and backend logic for the scan page.
 */

// Module Includes
const path = require('path');
const fs = require('fs');
const express = require('express');
const bodyParser = require('body-parser');
const zmq = require('zeromq');

// backend variables
var currentScannerStatus = null;
var cmd_socket = null;
var update_socket = null;

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


// initialize the sockets on startup
initSockets();

// setup both the command and update sockets
function initSockets() {
    // publish comands on port 3000
    cmd_socket = zmq.socket('pub');
    cmd_socket.bindSync('tcp://*:3000');
    console.log('Publisher bound to port 3000');

    // subscribe to updates on port 5000
    update_socket = zmq.socket('sub');
    update_socket.connect('tcp://localhost:5000');
    update_socket.subscribe('scan_update');
    update_socket.on('message', function (topic, message) {
        //console.log("Received a message of topic: " + topic.toString());
        currentScannerStatus = JSON.parse(message);
        //console.log(currentScannerStatus.status);
    })
    console.log('Subscriber connected to port 5000');
}

// Send a command to the scanner to start scanning
function performScan(params) {
    currentScannerStatus = null;
    console.log('sending a multipart message envelope');
    //console.log(JSON.stringify(params));
    cmd_socket.send(['cmd_msg', 'perform_scan', JSON.stringify(params)]);
}

// close the sockets on exit
process.on('SIGINT', function () {
    if (cmd_socket)
        cmd_socket.close();
    if (update_socket)
        update_socket.close();
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