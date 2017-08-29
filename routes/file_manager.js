/**
 * File Manager Route:
 * Contains all the route and backend logic for the file manager page.
 */

// Module Includes
const path = require('path');
const fs = require('fs');
const express = require('express');
const bodyParser = require('body-parser');
const _STORAGE = require('../js/storage.js');

// Backend consts + variables
const SCAN_FILE_DIR = path.join(__dirname, "../output_scans/");
const FILE_MANAGER = new _STORAGE.ScanFileManager(SCAN_FILE_DIR);

// Setup express
var app = express();
//gives your app the ability to parse JSON
app.use(bodyParser.json());
//allows app to read data from URLs (GET requests)
app.use(bodyParser.urlencoded({ extended: false }));

// create a router to handle any routing
var router = express.Router();
app.use(router);

// handle requests for the scan files
router.route('/request_scan_files')
    .get(function (req, res, next) {
        res.send({
            files: FILE_MANAGER.getScanFiles()
        });
    })

// handle request to delete a specific file
router.route('/delete_file')
    .get(function (req, res, next) {
        let filename = req.query.file;
        console.log(`Deleting...${filename}`);
        FILE_MANAGER.deleteFile(filename);
        res.send({
            bSuccessfullyDeletedFile: true,
            file: filename,
            updatedFileList: FILE_MANAGER.getScanFiles()
            //errorMsg: ""
        });
    })

// handle request to download a specific file
router.route('/download_file/:format/:file(*)')
    .get(function (req, res, next) {
        let filename = req.params.file;
        let format = req.params.format;
        let downloadPath = FILE_MANAGER.getFormattedFile(filename, format);

        if (_STORAGE.checkFileExists(downloadPath))
            res.download(downloadPath, function (err) {
                // delete any generated files after sending them
                if (format !== 'csv')
                    _STORAGE.deleteFile(downloadPath);
            });
    })

module.exports = app;