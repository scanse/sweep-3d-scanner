/**
 * Manages client side logic for the scan page
 */

// Module includes
const _UTILS = ScannerLib.Utils;
const _SETTINGS = ScannerLib.Settings;
const _REQUESTS = ScannerLib.Requests;

// Constants
const updateInterval_MS = 300;

$(document).ready(function () {
    init();
});

// initialize page elements
function init() {
    initScanForm();
}

// Initialize the scan form, by populating all the input fields with appropriate options
function initScanForm() {
    _UTILS.initDropdownForEnum('select_ScanType', _SETTINGS.SCAN_TYPE_ENUM);
    _UTILS.initDropdownForEnum('select_MotorSpeed', _SETTINGS.MOTOR_SPEED_ENUM);
    _UTILS.initDropdownForEnum('select_SampleRate', _SETTINGS.SAMPLE_RATE_ENUM);

    // Request that a scan be initiated when button is pressed
    $("#btn_PerformScan").click(function () {
        let options = readSpecifiedScanOptions();
        _REQUESTS.requestScriptExecution('scan_request', options, onScanRequestResponse);
    });

    // Cancel a scan when button is pressed
    $("#btn_CancelScan").click(function () {
        _REQUESTS.cancelScan(function (bSuccess) {
            console.log(bSuccess ? "Successfully canceled scan." : "Failed to cancel scan.");
        })
    });
}

// Update the progress bar for scan progress
function updateProgressBar(percentage) {
    $('#pb_Scan').css('width', percentage + '%').attr('aria-valuenow', percentage).html(`${percentage}%`);
}

function onReceivedUpdate(data) {
    if (typeof data === 'undefined' || !data || data === null) {
        waitAndRequestUpdate(updateInterval_MS);
        return;
    }

    let updateArray = null;
    try {
        updateArray = JSON.parse(data);
    }
    catch (e) {
        console.log(e);
        return;
    }

    let numUpdates = updateArray.length;
    for (let i = 0; i < numUpdates; i++) {
        let update = updateArray[i];
        switch (update.status) {
            case 'failed':
                $('#span_ScanResult').html("Scan Failed...");
                showScanFailure(update.msg);
                return;     // return early, DON'T REQUEST UPDATE
            case 'scan':
                $('#span_ScanStatus').html(update.msg);
                let percentage = _UTILS.calcPercentage(update.remaining, update.duration);
                updateProgressBar(percentage);
                break;
            case 'setup':
                $('#span_ScanStatus').html(update.msg);
                updateProgressBar(0);
                break;
            case 'complete':
                $('#span_ScanStatus').html(update.msg);
                $('#span_ScanResult').html("Scan Complete!");
                showScanSuccess(update.msg);
                return;     // return early, DON'T REQUEST UPDATE
            default:
                return;     // return early, DON'T REQUEST UPDATE
        }
    }

    waitAndRequestUpdate(updateInterval_MS);
}

function waitAndRequestUpdate(waitTime_MS) {
    setTimeout(function () {
        // Requests an update regarding scan progress
        _REQUESTS.requestUpdate(onReceivedUpdate);
    }, waitTime_MS);
}

// callback to be executed once the server registers a scan request
function onScanRequestResponse(data) {
    console.log(data);
    if (data.bSumittedRequest) {
        //FIXME: only show progress when the scanner actually returns an update
        showScanProgress(data.params);
        waitAndRequestUpdate(0);
    }
    else
        showScanFailure(data.errorMsg);
}

// Read the currently selected scan options from the form
function readSpecifiedScanOptions() {
    let options = {};

    let selectedKey = $('#select_ScanType').find(":selected").val();
    let properties = _UTILS.getEnumPropertiesForKey(_SETTINGS.SCAN_TYPE_ENUM, selectedKey);
    options.angular_range = properties.angular_range;

    selectedKey = $('#select_MotorSpeed').find(":selected").val();
    properties = _UTILS.getEnumPropertiesForKey(_SETTINGS.MOTOR_SPEED_ENUM, selectedKey);
    options.motor_speed = properties.motor_speed;

    selectedKey = $('#select_SampleRate').find(":selected").val();
    properties = _UTILS.getEnumPropertiesForKey(_SETTINGS.SAMPLE_RATE_ENUM, selectedKey);
    options.sample_rate = properties.sample_rate;

    let d = new Date();
    let alt_filename = "3D Scan - " + d.toDateString() + " " + d.toLocaleTimeString().replace(/:\s*/g, "-");
    options.file_name = _UTILS.textInputHasValue("#input_FileName") ? $("#input_FileName").val() : alt_filename;

    return options;
}

// Show the portion of the page that deals with scan progress
function showScanProgress(params) {
    $("#div_ScanResults").hide();
    $("#div_ScanForm").hide();
    $("#div_ScanProgress").show();

    // display the scan settings
    $("#span_ScanType").html(`${params.angular_range * 2} degree scan`);
    $("#span_MotorSpeed").html(params.motor_speed);
    $("#span_SampleRate").html(params.sample_rate);
    $("#span_FileName").html(params.file_name);
}

// Show the portion of the page that deals with scan failure
function showScanFailure(msg) {
    console.log(`Failure:  ${msg}`);
    $("#div_ScanForm").hide();
    $("#div_ScanProgress").hide();
    $("#div_ScanResults").show();

    $("#alert_Success").html('');
    $("#alert_Success").hide();
    $("#alert_Failure").html(`<pre>${msg}</pre>`);
    $("#alert_Failure").show();
}

// Show the portion of the page that deals with scan success
function showScanSuccess(msg) {
    console.log(`Success:  ${msg}`);
    $("#div_ScanForm").hide();
    $("#div_ScanProgress").hide();
    $("#div_ScanResults").show();

    $("#alert_Success").html(msg);
    $("#alert_Success").show();
    $("#alert_Failure").html('');
    $("#alert_Failure").hide();
}