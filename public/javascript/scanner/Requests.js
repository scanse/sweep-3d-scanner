/************************************************************************************//**
** Requests (Module): ScannerLib module.
*   Contains helpful constants, classes or methods related to remote requests.
****************************************************************************************/
ScannerLib.Requests = function () {
    /****************************************************************************************
    * Includes
    ****************************************************************************************/
    // ScannerLib module includes
    const _UTILS = ScannerLib.Utils;

    /****************************************************************************************
    * Methods
    ****************************************************************************************/
    let requestUpdate = (callback) => {
        $.ajax({
            url: "/script_execution/request_update"
        }).done(callback).fail(function () {
            console.log("Ajax request failed");
        });
    };

    let requestScriptExecution = (type, params, callback) => {
        $.ajax({
            url: "/script_execution/request_script_execution",
            data: {
                type: type,
                params: params
            },
            dataType: "json"
        }).done(callback).fail(function () {
            console.log("Ajax request failed");
        });
    };

    let cancelScan = (callback) => {
        $.ajax({
            url: "/script_execution/cancel_scan",
            type: 'post'
        }).done(function (data) {
            callback(data == "success");
        }).fail(function () {
            console.log("Ajax request failed");
        });
    };



    /************************************************************************************//**
    ** Public API
    *  Return all the methods/variables that should be public.
    ****************************************************************************************/
    return {
        // public methods
        requestUpdate: requestUpdate,
        requestScriptExecution: requestScriptExecution,
        cancelScan: cancelScan
    };
}();