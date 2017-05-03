// Check for dummy flag passed as command line argument (ie: "node .\app.js -d")
// note it as a global variable, so all routes can access
let optionFlag = process.argv[2];
GLOBAL_APPLICATION_VARIABLE_bUseDummy = (optionFlag == '-d' || optionFlag == '-D');

const express = require('express');
var app = express();

// Import various routes
let route_INDEX = require('./routes/index.js');
let route_SCAN = require('./routes/scan.js');
let route_FILE_MANAGER = require('./routes/file_manager.js');
let route_DEVICE = require('./routes/device.js');
let route_COMPONENT_TESTING = require('./routes/component_testing.js');

// Handle each page within a separate route file (imported at top)
app.use('/', route_INDEX);
app.use('/scan', route_SCAN);
app.use('/file_manager', route_FILE_MANAGER);
app.use('/device', route_DEVICE);
app.use('/component_testing', route_COMPONENT_TESTING);

var server;
if (GLOBAL_APPLICATION_VARIABLE_bUseDummy) {
    // local host for easy development
    server = app.listen(8080, 'localhost', function () {
        var host = server.address().address;
        var port = server.address().port;

        console.log('LOCAL HOST');
        console.log('Scanner app listening at http://%s:%s', host, port);
        console.log('Use a local browser to navigate to http://%s:%s', host, port);
    });
}
else {
    server = app.listen(8080, 'localhost', function () {
        var host = server.address().address;
        var port = server.address().port;

        console.log('Scanner app listening at http://%s:%s', host, port);
        console.log('Use a browser on another device to navigate to http://%s:%s', host, port);
    });
}

module.exports = app;