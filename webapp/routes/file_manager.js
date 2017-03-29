/**
 * File Manager Route:
 * This contains all the route and backend logic for the file manager page.
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
        res.render('file_manager', {
            bShowMsg: false,
            files: getScanFiles()
        });
    })
    .post(function (req, res, next) {
        console.log('received post');
        let actionType = req.body.submit;
        let filename = req.body.input_FileName;
        switch (actionType) {
            case 'download':
                console.log(`Downloading... ${filename}`);
                if (checkFile(filename))
                    res.download(path.join('./output_scans/', filename));
                else
                    res.render('file_manager', {
                        bShowMsg: true,
                        msg: `File (${filename}) does not exist...`,
                        files: getScanFiles()
                    });
                break;
            case 'delete':
                console.log(`Deleting...${filename}`);
                deleteFile(filename);
                res.render('file_manager', {
                    bShowMsg: true,
                    msg: `Successfully deleted ${filename}`,
                    files: getScanFiles()
                });
                break;
        }
    })

function getScanFiles() {
    let scan_dir = './output_scans/';
    let file_names = fs.readdirSync(scan_dir);
    return file_names;
}

function deleteFile(filename) {
    let file = path.join('./output_scans/', filename);
    fs.unlinkSync(file);
}

function checkFile(filename) {
    //FIXME: add real check
    return true;
}

module.exports = app;