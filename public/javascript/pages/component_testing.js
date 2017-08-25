/**
 * Manages client side logic for the component testing page
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
    initTestForm();
}

// Initialize the test form, by populating all the input fields with appropriate options
function initTestForm() {
    //initializes the selectable options for the test type select dropdown
    _UTILS.initDropdownForEnum('select_TestType', _SETTINGS.TEST_TYPE_ENUM);

    // Request that a test be initiated when button is pressed
    $("#btn_PerformTest").click(function () {
        let options = readSpecifiedTestOptions();
        _REQUESTS.requestScriptExecution('test_request', options, onTestRequestResponse);
    });
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
    let update;
    for (let i = 0; i < numUpdates; i++) {
        update = updateArray[i];
        switch (update.status) {
            case 'failed':
                $('#span_TestStatus').html("Test Failed...");
                showFailure(update.msg);
                return;     // return early, DON'T REQUEST UPDATE
            case 'instruction':
                $('#span_TestStatus').html(update.msg);
                updateProgressReport(update.msg);
                break;
            case 'progress':
                updateProgressReport(update.msg);
                break;
            case 'setup':
                updateProgressReport(update.msg);
                break;
            case 'complete':
                $('#span_TestStatus').html(update.msg);
                showSuccess(update.msg);
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

// Request that a test be initiated
function onTestRequestResponse(data) {
    console.log(data);
    if (data.bSumittedRequest) {
        //let testDisplayName = _SETTINGS.TEST_TYPE_ENUM.properties[data.params.test].displayName;
        //showWarning(`Not yet implemented... but would be performing test: ${testDisplayName}`);
        showTestProgress();
        waitAndRequestUpdate(0);
    }
    else
        showFailure(data.errorMsg);
}

// Read the currently selected test options from the form
function readSpecifiedTestOptions() {
    let options = {};

    let selectedKey = $('#select_TestType').find(":selected").val();
    options.test = _SETTINGS.TEST_TYPE_ENUM[selectedKey];

    return options;
}

// Show the portion of the page that deals with test progress
function showTestProgress() {
    $("#div_TestForm").hide();
    $("#div_TestProgress").show();
}

function showWarning(msg) {
    $("#alert_Failure").html('');
    $("#alert_Failure").hide();
    $("#alert_Success").html('');
    $("#alert_Success").hide();

    $("#alert_Warning").html(msg);
    $("#alert_Warning").show();

    $("#btn_ReloadPage").show();
}

function showFailure(msg) {
    $("#alert_Success").html('');
    $("#alert_Success").hide();
    $("#alert_Warning").html('');
    $("#alert_Warning").hide();

    $("#alert_Failure").html(`<pre>${msg}</pre>`);
    $("#alert_Failure").show();

    $("#btn_ReloadPage").show();
}

function showSuccess(msg) {
    $("#alert_Warning").html('');
    $("#alert_Warning").hide();
    $("#alert_Failure").html('');
    $("#alert_Failure").hide();

    $("#alert_Success").html(msg);
    $("#alert_Success").show();

    $("#btn_ReloadPage").show();
}

function updateProgressReport(msg) {
    $("#pre_TestDetails").append(msg + "\n");
    $("#pre_TestDetails").scrollTop($("#pre_TestDetails")[0].scrollHeight);
}