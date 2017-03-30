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
    .get(function (req, res) {
        res.render('scan');
    })

router.route('/request_update')
    .get(function (req, res, next) {
        let statusObj = getScannerStatus();
        res.send(statusObj);
    })

router.route('/submit_scan_request')
    .get(function (req, res, next) {
        var data = req.query;
        //console.log(data);
        performScan(data);

        res.send({
            bSuccessfullyStartedScan: true,
            //errorMsg: "testing error msg...",
            scanParams: data //FIXME: currently just sending the same data back
        });
    })


let progress = 0;
function getScannerStatus() {
    let obj = {
        scanStatus: null,
        percentage: null
    }

    if (true) {
        obj.scanStatus = "in-progress"
        obj.percentage = progress++;
    }
    else {
        //obj.scanStatus = "setup"
        //obj.scanStatus = "finished"
    }

    return obj;
}

var zmq = require('zeromq');

var cmd_socket = zmq.socket('pub');

// publish on port 3000
cmd_socket.bindSync('tcp://*:3000');
console.log('Publisher bound to port 3000');

function performScan(params) {
    console.log('sending a multipart message envelope');
    //console.log(JSON.stringify(params));
    cmd_socket.send(['cmd_msg', 'perform_scan', JSON.stringify(params)]);
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