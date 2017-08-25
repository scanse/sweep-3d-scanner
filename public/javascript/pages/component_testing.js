/**
 * Manages client side logic for the component testing page
 */

let bExpectingFurtherUpdates = true;

$(document).ready(function () {
    init();
});

// initialize page elements
function init() {
    initTestForm();
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
        url: "/script_execution/request_update"
    }).done(function (data) {
        if (typeof data === 'undefined' || !data || data === null) {
            setTimeout(requestUpdate, 300);
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
        if (numUpdates <= 0) {
            if (bExpectingFurtherUpdates)
                setTimeout(requestUpdate, 300);
            return;
        }

        let update;
        for (let i = 0; i < numUpdates; i++) {
            update = updateArray[i];
            switch (update.status) {
                case 'failed':
                    $('#span_TestStatus').html("Test Failed...");
                    showFailure(update.msg);
                    break;
                case 'instruction':
                    $('#span_TestStatus').html(update.msg);
                    setTimeout(requestUpdate, 300);
                case 'progress':
                    updateProgressReport(update.msg);
                    setTimeout(requestUpdate, 300);
                    break;
                case 'setup':
                    updateProgressReport(update.msg);
                    setTimeout(requestUpdate, 300);
                    break;
                case 'complete':
                    bExpectingFurtherUpdates = false;
                    $('#span_TestStatus').html(update.msg);
                    showSuccess(update.msg);
                    break;
                default:
                    break;
            }
        }

    }).fail(function () {
        console.log("Ajax request failed");
    });
}

// Request that a test be initiated
function requestTest() {
    let options = readSpecifiedTestOptions();
    $.ajax({
        url: "/script_execution/request_script_execution",
        data: {
            type: 'test_request',
            params: options
        },
        dataType: "json"
    }).done(function (data) {
        console.log(data);
        if (data.bSumittedRequest) {
            //let testDisplayName = TestTypeEnum.properties[data.params.test].displayName;
            //showWarning(`Not yet implemented... but would be performing test: ${testDisplayName}`);
            bExpectingFurtherUpdates = true;
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