/**
 * Manages client side logic for the scan page
 */

$(document).ready(function () {
    initScanForm();
});


function requestUpdate() {
    $.ajax({
        url: "/scan/request_update"
    }).done(function (data) {
        switch (data.scanStatus) {
            case 'in-progress':
                $('#span_ScanStatus').html('In Progress...');
                updateProgressBar(data.percentage);
                if (data.percentage < 100)
                    setTimeout(requestUpdate, 300);
                break;
            case 'setup':
                console.log("Scanner is setting up...");
                $('#span_ScanStatus').html('Running Setup Routine...');
                break;
            case 'finished':
                $('#span_ScanStatus').html('Scan Complete!');
                showScanSuccess("Finished Scan!");
                break;
            default:
                break;
        }

    });
}

function updateProgressBar(percentage) {
    $('#pb_Scan').css('width', percentage + '%').attr('aria-valuenow', percentage).html(`${percentage}%`);
}


function initScanForm() {
    initScanTypeDropdown();
    initMotorSpeedDropdown();
    initSampleRateDropdown();
    $("#btn_PerformScan").click(requestScan);
}

//initializes the selectable options for the scan type select dropdown
function initScanTypeDropdown() {
    /* loop through the available scan types and programmatically create an option for each */
    let optionName, optionHTML;
    for (let key in ScanTypeEnum) {
        //don't consider the properties key as a key
        if (key === 'properties')
            break;

        //create a new button, and insert it into the dropdown
        optionName = `option_ScanType_${key}`;
        optionHTML = `  <option id="${optionName}" value="${key}"> 
                            ${ ScanTypeEnum.properties[ScanTypeEnum[key]].displayName}
                        </option>`
        $("#select_ScanType").append(optionHTML);
    }
}

//initializes the selectable options for the motor speed select dropdown
function initMotorSpeedDropdown() {
    /* loop through the available motor speeds and programmatically create an option for each */
    let optionName, optionHTML;
    for (let key in MotorSpeedEnum) {
        //don't consider the properties key as a key
        if (key === 'properties')
            break;

        //create a new button, and insert it into the select dropdown
        optionName = `option_MotorSpeed_${key}`;
        optionHTML = `  <option id="${optionName}" value="${key}"> 
                            ${ MotorSpeedEnum.properties[MotorSpeedEnum[key]].displayName}
                        </option>`
        $("#select_MotorSpeed").append(optionHTML);
    }
}

//initializes the selectable options for the sample rate select dropdown
function initSampleRateDropdown() {
    /* loop through the available sample rates and programmatically create an option for each */
    let optionName, optionHTML;
    for (let key in SampleRateEnum) {
        //don't consider the properties key as a key
        if (key === 'properties')
            break;

        //create a new button, and insert it into the dropdown
        optionName = `option_SampleRate_${key}`;
        optionHTML = `  <option id="${optionName}" value="${key}"> 
                            ${ SampleRateEnum.properties[SampleRateEnum[key]].displayName}
                        </option>`
        $("#select_SampleRate").append(optionHTML);
    }
}

function requestScan() {
    let options = readSpecifiedScanOptions();

    $.ajax({
        url: "/scan/submit_scan_request",
        data: options,
        dataType: "json"
    }).done(function (data) {
        console.log(data);
        if (data.bSuccessfullyStartedScan) {
            showScanProgress(data.scanParams);
            requestUpdate();
        }
        else
            showScanFailure(data.errorMsg);
    });
}

function readSpecifiedScanOptions() {
    let options = {};

    let selectedKey = $('#select_ScanType').find(":selected").val();
    options.angular_range = ScanTypeEnum.properties[ScanTypeEnum[selectedKey]].angular_range;

    selectedKey = $('#select_MotorSpeed').find(":selected").val();
    options.motor_speed = MotorSpeedEnum.properties[MotorSpeedEnum[selectedKey]].motor_speed;

    selectedKey = $('#select_SampleRate').find(":selected").val();
    options.sample_rate = SampleRateEnum.properties[SampleRateEnum[selectedKey]].sample_rate;

    options.file_name = textInputHasValue("#input_FileName") ? $("#input_FileName").val() : `Scan ${Date.now()}`;

    return options;
}

function showScanProgress(params) {
    console.log("Showing scan progress");
    $("#div_ScanResults").hide();
    $("#div_ScanForm").hide();
    $("#div_ScanProgress").show();

    console.log(params);
    // display the scan settings
    $("#span_ScanType").html(`${params.angular_range * 2} degree scan`);
    $("#span_MotorSpeed").html(params.motor_speed);
    $("#span_SampleRate").html(params.sample_rate);
    $("#span_FileName").html(params.file_name);
}

function showScanFailure(msg) {
    console.log(`Scan Failed:  ${msg}`);
    $("#div_ScanForm").hide();
    $("#div_ScanProgress").hide();
    $("#div_ScanResults").show();

    $("#alert_Success").html('');
    $("#alert_Success").hide();
    $("#alert_Failure").html(msg);
    $("#alert_Failure").show();
}

function showScanSuccess(msg) {
    console.log(`Scan Failed:  ${msg}`);
    $("#div_ScanForm").hide();
    $("#div_ScanProgress").hide();
    $("#div_ScanResults").show();

    $("#alert_Failure").html('');
    $("#alert_Failure").hide();
    $("#alert_Success").html(msg);
    $("#alert_Success").show();
}