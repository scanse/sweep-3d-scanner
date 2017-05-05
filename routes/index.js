/**
 * Index Route:
 * Contains all the route and backend logic for the index page.
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
    .all(function (req, res, next) {
        console.log('Someone made a request!');
        next();
    })
    .get(function (req, res, next) {
        res.render('index');
    })
    .post(function (req, res, next) {
        console.log('received post');
    })

// request a reboot
router.route('/request_reboot')
    .get(function (req, res, next) {
        reboot();
    })

// request a shutdown
router.route('/request_shutdown')
    .get(function (req, res, next) {
        shutdown();
    })

// reboot the raspberry pi
function reboot() {
    if (!GLOBAL_APPLICATION_VARIABLE_bUseDummy) {
        //TODO: add execution of reboot command
    }
    console.log("Restarting Raspberry Pi...");
    process.exit();
}

// shutdown the raspberry pi
function shutdown() {
    if (!GLOBAL_APPLICATION_VARIABLE_bUseDummy) {
        //TODO: add execution of shutdown command
    }
    console.log("Shutting down Raspberry Pi...");
    process.exit();
}

module.exports = app;