// Import various routes
let route_INDEX = require('./routes/index.js');
let route_FILE_MANAGER = require('./routes/file_manager.js');
let route_SCAN = require('./routes/scan.js');

const express = require('express');
var app = express();

// Handle each page within a separate route file (imported at top)
app.use('/', route_INDEX);
app.use('/scan', route_SCAN);
app.use('/file_manager', route_FILE_MANAGER);

var server = app.listen(8080, function () {
    var host = server.address().address;
    var port = server.address().port;

    console.log('Example app listening at http://%s:%s', host, port);
});

module.exports = app;