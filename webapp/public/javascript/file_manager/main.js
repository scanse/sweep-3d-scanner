$(document).ready(function () {
    init();
});


function init() {
    initButtons();
    refreshFiles();
}

function initButtons() {
    $("#btn_DownloadFile").click(downloadFile);
    $("#btn_DeleteFile").click(deleteFile);
}

function refreshFiles() {
    $.ajax({
        url: "/file_manager/request_scan_files"
    }).done(function (data) {
        populateFilesSelect(data.files);
    });
}

function populateFilesSelect(files) {
    $("#select_FileName").html('');

    if (files.length <= 0) {
        $("#btn_DeleteFile").hide();
        $("#btn_DownloadFile").hide();
        showWarning("There are currently no files available.");
        return;
    }

    /* loop through the available files programmatically create an option for each */
    let file, optionName, optionHTML;
    for (let i = 0; i < files.length; i++) {
        file = files[i];
        //create a new button, and insert it into the dropdown
        optionName = `option_File_${file}`;
        optionHTML = `  <option id="${optionName}" value="${file}"> 
                            ${file}
                        </option>`
        $("#select_FileName").append(optionHTML);
    }

    $("#btn_DeleteFile").show();
    $("#btn_DownloadFile").show();
}

function showWarning(msg) {
    $("#alert_Failure").html('');
    $("#alert_Failure").hide();
    $("#alert_Success").html('');
    $("#alert_Success").hide();

    $("#alert_Warning").html(msg);
    $("#alert_Warning").show();
}

function showFailure(msg) {
    $("#alert_Success").html('');
    $("#alert_Success").hide();
    $("#alert_Warning").html('');
    $("#alert_Warning").hide();

    $("#alert_Failure").html(msg);
    $("#alert_Failure").hide();
}

function showSuccess(msg) {
    $("#alert_Warning").html('');
    $("#alert_Warning").hide();
    $("#alert_Failure").html('');
    $("#alert_Failure").hide();

    $("#alert_Success").html(msg);
    $("#alert_Success").show();
}


function downloadFile() {
    // read the filename from the select dropdown
    let filename = $('#select_FileName').find(":selected").val();
    // download the file with a dialog by opening a separate window
    if (filename.length > 0) {
        window.open(`/file_manager/download_file/${filename}`);
    }
}

function deleteFile() {
    let file = $('#select_FileName').find(":selected").val();
    $.ajax({
        url: "/file_manager/delete_file",
        data: { file: file },
        dataType: "json"
    }).done(function (data) {
        if (data.bSuccessfullyDeletedFile) {
            showSuccess(`Successfully deleted file ${data.file}`);
            populateFilesSelect(data.updatedFileList);
        }
        else
            showFailure(`${data.errorMsg}`);
    });
}






