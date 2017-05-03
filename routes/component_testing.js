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

// Provide the path of the python executable, if python is available as environment variable then you can use only "python"
const pythonExecutable = "python";
// Python script paths
// ...

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

// Function to convert an Uint8Array to a string
function uint8arrayToString(data) {
    return String.fromCharCode.apply(null, data);
}

module.exports = app;