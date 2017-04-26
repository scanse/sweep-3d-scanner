/**
 * Index Route:
 * This contains all the route and backend logic for the index page.
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


module.exports = app;