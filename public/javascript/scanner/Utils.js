/************************************************************************************//**
** Utils (Module): ScannerLib module.
*   Contains helpful classes and methods
****************************************************************************************/
ScannerLib.Utils = function () {

    /****************************************************************************************
    * Methods
    ****************************************************************************************/

    // Converts a Uint8Array to a string
    let uint8arrayToString = (data) => {
        return String.fromCharCode.apply(null, data);
    };

    //Returns the default value of any enum with a properties list containing a default parameter
    let getEnumDefault = (theEnum) => {
        for (let key in theEnum) {
            //don't consider the properties key
            if (key === 'properties')
                break;
            if (theEnum.properties[theEnum[key]].bIsDefault) {
                return theEnum[key];
            }
        }
        return null;
    };

    // Returns the keys of an enum without including the properties key
    let getEnumKeys = function (theEnum) {
        let keys = [];
        for (let key in theEnum) {
            //don't consider the properties key as a key
            if (key === 'properties')
                break;
            keys.push(key);
        }
        return keys;
    };

    // Returns the properties associated with a specified key in the provided enum
    let getEnumPropertiesForKey = (theEnum, theKey) => {
        return theEnum.properties[theEnum[theKey]];
    };

    // Initializes the entries of the specified enum as options in a specified select dropdown
    let initDropdownForEnum = (selectElemID, theEnum) => {
        /* loop through the available enum entries and programmatically create an option for each */
        let optionName, optionHTML;
        for (let key in theEnum) {
            // don't consider the properties key as a key
            if (key === 'properties')
                break;

            // human readable name
            displayName = theEnum.properties[theEnum[key]].displayName;

            // create a new button, and insert it into the dropdown
            optionName = `option_${displayName}_${key}`;
            optionHTML = `  <option id="${optionName}" value="${key}"> 
                                ${displayName}
                            </option>`
            $(`#${selectElemID}`).append(optionHTML);
        }
    };

    // Checks if an element contains any value
    let textInputHasValue = (elem) => {
        return $(elem).filter(function () { return $(this).val(); }).length > 0;
    };

    // Returns the nearest integer percentage between 0:100
    let calcPercentage = (remaining, total) => {
        return Math.round(100 * ((total - remaining) / total));
    };


    /************************************************************************************//**
    ** Public API
    *  Return all the methods/variables that should be public.
    ****************************************************************************************/
    return {
        // public methods
        uint8arrayToString: uint8arrayToString,
        getEnumDefault: getEnumDefault,
        getEnumKeys: getEnumKeys,
        getEnumPropertiesForKey: getEnumPropertiesForKey,
        initDropdownForEnum: initDropdownForEnum,
        textInputHasValue: textInputHasValue,
        calcPercentage: calcPercentage
    };
}();