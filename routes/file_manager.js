/**
 * File Manager Route:
 * Contains all the route and backend logic for the file manager page.
 */

// Module Includes
const path = require('path');
const fs = require('fs');
const express = require('express');
const bodyParser = require('body-parser');
const csv_parse = require('csv-parse/lib/sync');
const replaceExt = require('replace-ext');

// backend variables
const scan_file_dir = path.join(__dirname, "../output_scans/");
// create directory if it doesn't yet exist
if (!fs.existsSync(scan_file_dir)) {
    fs.mkdirSync(scan_file_dir);
}

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
            files: getScanFiles()
        });
    })

// handle request to delete a specific file
router.route('/delete_file')
    .get(function (req, res, next) {
        let filename = req.query.file;
        console.log(`Deleting...${filename}`);
        deleteFile(filename);
        res.send({
            bSuccessfullyDeletedFile: true,
            file: filename,
            updatedFileList: getScanFiles()
            //errorMsg: ""
        });
    })

// handle request to download a specific file
router.route('/download_file/:format/:file(*)')
    .get(function (req, res, next) {
        let filename = req.params.file;
        let format = req.params.format;
        let filePath = null;
        switch (format) {
            case 'csv':
                filePath = path.join(scan_file_dir, filename);
                break;
            case 'ply':
                filePath = generatePLYFile(filename, false);
                break;
            case 'ply_binary':
                filePath = generatePLYFile(filename, true);
                break;
            case 'xyz':
                filePath = generateXYZFile(filename);
                break;
            default:
                break;
        }

        if (filePath && fs.existsSync(filePath))
            res.download(filePath, function (err) {
                // delete any generated files
                if (format !== 'csv')
                    fs.unlinkSync(filePath);
            });
    })

// returns a list of available scan files
function getScanFiles() {
    // retrieve and chronolgically sort the file names
    let file_names = fs.readdirSync(scan_file_dir);
    file_names.sort(compareFileTimestampDescending);
    return file_names;
}

// compare function used to sort a list of filenames in descending chronological order 
// (ie: most recent first)
function compareFileTimestampDescending(file_a, file_b) {
    return fs.statSync(path.join(scan_file_dir, file_b)).mtime.getTime() -
        fs.statSync(path.join(scan_file_dir, file_a)).mtime.getTime();
}

// deletes a specific scan file
function deleteFile(filename) {
    //let file = path.join('./output_scans/', filename);
    let file = path.join(scan_file_dir, filename);
    fs.unlinkSync(file);
}

// generate XYZ file from the specified CSV file
// return the filepath if successfull, null otherwise
function generateXYZFile(csvFile) {
    let csvPath = path.join(scan_file_dir, csvFile);
    let records = getRecords(csvPath);

    if (typeof records === 'undefined' || typeof records[0] === 'undefined')
        return null;

    let buffer = convertRecordsToXYZBuffer(records);

    if (!buffer)
        return null;

    let xyzPath = replaceExt(csvPath, '.xyz');
    fs.writeFileSync(xyzPath, buffer);
    return xyzPath;
}

// generate PLY file from the specified CSV file
// return the filepath if successfull, null otherwise
function generatePLYFile(csvFile, bCompressToBinary) {
    let csvPath = path.join(scan_file_dir, csvFile);
    let records = getRecords(csvPath);

    if (typeof records === 'undefined' || typeof records[0] === 'undefined')
        return null;

    let buffer = convertRecordsToPLYBuffer(records, bCompressToBinary);

    if (!buffer)
        return null;

    let plyPath = replaceExt(csvPath, '.ply');
    fs.writeFileSync(plyPath, buffer);
    return plyPath;
}

function getRecords(csvPath) {
    let data = null;
    try {
        data = fs.readFileSync(csvPath);
    }
    catch (err) {
        console.log(`Failed to read file ${csvPath}. Error: ${err.message}`);
        return null;
    }

    // parse the records from the csv
    let records = null;

    // csv parse options
    let options = { columns: true, skip_empty_lines: true, trim: true, auto_parse: true };
    try {
        records = csv_parse(data, options);
    }
    catch (err) {
        console.log(`Failed to parse CSV file. Error: ${err.message}`);
        return null;
    }
    return records;
}

// converts a set of csv records to a buffer of xyz data (cartesian point cloud)
function convertRecordsToXYZBuffer(records) {
    let numDataPoints = records.length;
    if (numDataPoints <= 0)
        return null;

    let dataString = '';
    for (let i = 0; i < numDataPoints; i++) {
        dataString += `${
            Math.round(records[i].X * 100) / 100
            } ${
            Math.round(records[i].Y * 100) / 100
            } ${
            Math.round(records[i].Z * 100) / 100
            } ${
            records[i].SIGNAL_STRENGTH
            }`;
        if (i < numDataPoints - 1)
            dataString += '\n';
    }
    return new Buffer.from(dataString);
}

// converts a set of csv records to a buffer of ply data (cartesian point cloud)
function convertRecordsToPLYBuffer(records, bCompressToBinary) {
    let numDataPoints = records.length;
    if (numDataPoints <= 0)
        return null;

    let header = generatePLYHeader(numDataPoints, bCompressToBinary);

    if (bCompressToBinary) {
        let numBytesPerPoint = 13;
        let numHeaderBytes = header.length;
        let buffSizeInBytes = numHeaderBytes + (numDataPoints * numBytesPerPoint);

        // prepare the length of the buffer to the correct number of bytes
        buffer = new Buffer(buffSizeInBytes);

        // write the header to the buffer
        buffer.write(header);

        // write the points to the buffer
        let byteOffset = 0;
        for (let i = 0; i < numDataPoints; i++) {
            if ((typeof records[i] === 'undefined') || (typeof records[i].X === 'undefined') ||
                (typeof records[i].Y === 'undefined') || (typeof records[i].Z === 'undefined') ||
                (typeof records[i].SIGNAL_STRENGTH === 'undefined')) {
                return null;
            }

            byteOffset = numHeaderBytes + i * numBytesPerPoint;
            // write the coordinates as floats in Little-Endian format
            buffer.writeFloatLE(Math.round(records[i].X * 100) / 100, byteOffset);
            buffer.writeFloatLE(Math.round(records[i].Y * 100) / 100, byteOffset + 4);
            buffer.writeFloatLE(Math.round(records[i].Z * 100) / 100, byteOffset + 8);
            // write the signal strength as a uint8
            buffer.writeUInt8(records[i].SIGNAL_STRENGTH, byteOffset + 12)
        }
    }
    else {
        let dataString = header;
        for (let i = 0; i < numDataPoints; i++) {
            dataString += `\n${
                Math.round(records[i].X * 100) / 100
                } ${
                Math.round(records[i].Y * 100) / 100
                } ${
                Math.round(records[i].Z * 100) / 100
                } ${
                records[i].SIGNAL_STRENGTH
                }`;
        }
        buffer = new Buffer.from(dataString);
    }

    return buffer;
}

// creates a ply file header
function generatePLYHeader(numPoints, bCompressToBinary) {
    let header = "ply\n";
    header += `format ${bCompressToBinary ? 'binary_little_endian' : 'ascii'} 1.0\n`;
    header += `element vertex ${numPoints}\n`;
    header += "property float x\n";
    header += "property float y\n";
    header += "property float z\n";
    header += "property uchar signal_strength\n";
    header += `end_header${bCompressToBinary ? "\n" : ''}`;
    return header;
};


module.exports = app;