/**
 * Manages client side logic for the component testing page
 */

$(document).ready(function () {
    init();
});

var updateCounter = null;

// initialize page elements
function init() {
    initTestForm();
    updateCounter = 0;
}

// Initialize the test form, by populating all the input fields with appropriate options
function initTestForm() {
    initTestTypeDropdown();
    $("#btn_PerformTest").click(requestTest);
}

//initializes the selectable options for the test type select dropdown
function initTestTypeDropdown() {
    /* loop through the available test types and programmatically create an option for each */
    let optionName, optionHTML;
    for (let key in TestTypeEnum) {
        //don't consider the properties key as a key
        if (key === 'properties')
            break;

        //create a new button, and insert it into the dropdown
        optionName = `option_ScanType_${key}`;
        optionHTML = `  <option id="${optionName}" value="${key}"> 
                            ${ TestTypeEnum.properties[TestTypeEnum[key]].displayName}
                        </option>`
        $("#select_TestType").append(optionHTML);
    }
}

// Requests an update regarding scan progress
function requestUpdate() {
    $.ajax({
        url: "/component_testing/request_update"
    }).done(function (data) {
        if (typeof data === 'undefined' || !data || data === null) {
            setTimeout(requestUpdate, 300);
            return;
        }

        if (data.counter === updateCounter) {
            setTimeout(requestUpdate, 300);
            return;
        }
        updateCounter = data.counter;

        switch (data.status) {
            case 'failed':
                $('#span_TestStatus').html(data.msg);
                showFailure(data.msg);
                break;
            case 'instruction':
                $('#span_TestStatus').html(data.msg);
                setTimeout(requestUpdate, 300);
            case 'progress':
                updateProgressReport(data.msg);
                setTimeout(requestUpdate, 300);
                break;
            case 'setup':
                updateProgressReport(data.msg);
                setTimeout(requestUpdate, 300);
                break;
            case 'complete':
                $('#span_TestStatus').html(data.msg);
                showSuccess(data.msg);
                break;
            default:
                break;
        }

    }).fail(function () {
        console.log("Ajax request failed");
    });
}

// Request that a test be initiated
function requestTest() {
    updateCounter = 0;

    let options = readSpecifiedTestOptions();
    $.ajax({
        url: "/component_testing/submit_test_request",
        data: options,
        dataType: "json"
    }).done(function (data) {
        console.log(data);
        if (data.bSumittedTestRequest) {
            let testDisplayName = TestTypeEnum.properties[data.testParams.test].displayName;
            //showWarning(`Not yet implemented... but would be performing test: ${testDisplayName}`);
            showTestProgress();
            requestUpdate();
        }
        else
            showFailure(data.errorMsg);
    }).fail(function () {
        console.log("Ajax request failed");
    });
}

// Read the currently selected test options from the form
function readSpecifiedTestOptions() {
    let options = {};

    let selectedKey = $('#select_TestType').find(":selected").val();
    options.test = TestTypeEnum[selectedKey];

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

    $("#alert_Failure").html(msg);
    $("#alert_Failure").hide();

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
}