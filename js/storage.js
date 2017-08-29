/**
 * Storage: 
 * Contains classes and methods useful for interacting with scan files
 * (downloading, deleting, converting etc.)
 */
var exports = module.exports = {};

/****************************************************************************************
* Module Includes:
****************************************************************************************/
const path = require('path');
const fs = require('fs');
const csv_parse = require('csv-parse/lib/sync');
const replaceExt = require('replace-ext');



/****************************************************************************************
* ScanFileManager (Class):
****************************************************************************************/
exports.ScanFileManager = function (rootScanFileDirectory) {
    // the main scan file directory
    this.rootDir = rootScanFileDirectory;
    _self = this;
    // create the main scan file directory if it doesn't yet exist
    if (!fs.existsSync(this.rootDir)) {
        fs.mkdirSync(this.rootDir);
    }

    // deletes the specified file
    this.deleteFile = function (filename) {
        let filePath = path.join(this.rootDir, filename);
        exports.deleteFile(filePath);
    };

    // returns a list of available scan files
    this.getScanFiles = function () {
        // retrieve scan files
        let fileNames = fs.readdirSync(this.rootDir);
        // only use CSV files
        fileNames.filter(function (file) { return file.substr(-4) === '.csv'; });
        // sort chronologically
        fileNames.sort(this._compareFileTimestampDescending);
        return fileNames;
    };

    // returns a filepath to the appropriate format file, generating the new format if necessary
    this.getFormattedFile = function (filename, format) {
        let csvPath = path.join(this.rootDir, filename);
        let filePath = null;
        switch (format) {
            case 'csv':
                filePath = csvPath;
                break;
            case 'ply':
                filePath = _generatePLYFile(csvPath, false);
                break;
            case 'ply_binary':
                filePath = _generatePLYFile(csvPath, true);
                break;
            case 'xyz':
                filePath = _generateXYZFile(csvPath);
                break;
            default:
                break;
        }
        return filePath;
    };

    this.deleteMostRecentFile = function () {
        // retrieve chronologically sorted scan files
        let fileNames = this.getScanFiles();
        if (fileNames.length <= 0)
            return;
        // delete the most recent file
        this.deleteFile(fileNames[0]);
    };

    // compare function used to sort a list of filenames in descending chronological order 
    // (ie: most recent first)
    this._compareFileTimestampDescending = function (file_a, file_b) {
        let path_a = path.join(_self.rootDir, file_a);
        let path_b = path.join(_self.rootDir, file_b);
        return fs.statSync(path_b).mtime.getTime() -
            fs.statSync(path_a).mtime.getTime();
    };
};

/****************************************************************************************
* Public Methods
****************************************************************************************/
// return true if file exists
exports.checkFileExists = function (filePath) {
    if (typeof filePath === 'undefined' || !filePath)
        return false;
    return fs.existsSync(filePath);
};

// delete file if it exists
exports.deleteFile = function (filePath) {
    if (fs.existsSync(filePath))
        fs.unlinkSync(filePath);
};


/****************************************************************************************
* Private Methods
****************************************************************************************/
// generate XYZ file from the specified CSV filepath
// return the filepath if successfull, null otherwise
let _generateXYZFile = function (csvPath) {
    let records = _getRecords(csvPath);

    if (typeof records === 'undefined' || typeof records[0] === 'undefined')
        return null;

    let buffer = _convertRecordsToXYZBuffer(records);

    if (!buffer)
        return null;

    let xyzPath = replaceExt(csvPath, '.xyz');
    fs.writeFileSync(xyzPath, buffer);
    return xyzPath;
}

// generate PLY file from the specified CSV filepath
// return the filepath if successfull, null otherwise
let _generatePLYFile = function (csvPath, bCompressToBinary) {
    let records = _getRecords(csvPath);

    if (typeof records === 'undefined' || typeof records[0] === 'undefined')
        return null;

    let buffer = _convertRecordsToPLYBuffer(records, bCompressToBinary);

    if (!buffer)
        return null;

    let plyPath = replaceExt(csvPath, '.ply');
    fs.writeFileSync(plyPath, buffer);
    return plyPath;
}

let _getRecords = function (csvPath) {
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
let _convertRecordsToXYZBuffer = function (records) {
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
let _convertRecordsToPLYBuffer = function (records, bCompressToBinary) {
    let numDataPoints = records.length;
    if (numDataPoints <= 0)
        return null;

    let header = _generatePLYHeader(numDataPoints, bCompressToBinary);

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
let _generatePLYHeader = function (numPoints, bCompressToBinary) {
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