const MotorSpeedEnum = {
    MS_1_HZ : 1,
    MS_2_HZ: 2,
    MS_3_HZ: 3,
    
    properties: {
        1: {value: 1,   name: "MS_1_HZ", displayName: "1 Hz",   bIsDefault: true,   motor_speed: 1 },
        2: {value: 2,   name: "MS_2_HZ", displayName: "2 Hz",   bIsDefault: false,  motor_speed: 2 },
        3: {value: 3,   name: "MS_3_HZ", displayName: "3 Hz",   bIsDefault: false,  motor_speed: 3 }
    }
};

const SampleRateEnum = {
    SR_500_HZ : 1,
    SR_750_HZ: 2,
    SR_1000_HZ: 3,
    
    properties: {
        1: {value: 1,   name: "SR_500_HZ", displayName: "500 Hz",   bIsDefault: true,   sample_rate: 500 },
        2: {value: 2,   name: "SR_750_HZ", displayName: "750 Hz",   bIsDefault: false,  sample_rate: 750 },
        3: {value: 3,   name: "SR_1000_HZ", displayName: "1000 Hz",   bIsDefault: false,  sample_rate: 1000 }
    }
};

const ScanTypeEnum = {
    FULL_360_DEG : 1,
    HALF_180_DEG: 2,
    PARTIAL_90_DEG: 3,
    PARTIAL_30_DEG: 4,
    
    properties: {
        1: {value: 1,   name: "FULL_360_DEG", displayName: "Full Scan (360 deg)",   bIsDefault: true,   angular_range: 180 },
        2: {value: 2,   name: "HALF_180_DEG", displayName: "Half Scan (180 deg)",   bIsDefault: false,  angular_range: 90 },
        3: {value: 3,   name: "PARTIAL_90_DEG", displayName: "Partial Scan (90 deg)",   bIsDefault: false,  angular_range: 45 },
        4: {value: 3,   name: "PARTIAL_30_DEG", displayName: "Partial Scan (30 deg)",   bIsDefault: false,  angular_range: 15 }
    }
};


//Returns the default value of any enum with a properties list containing a default parameter
let getEnumDefault = ( theEnum ) => {
    for (let key in theEnum ) {
        //don't consider the properties key
        if ( key === 'properties')
            break;
        if ( theEnum.properties[ theEnum[key] ].bIsDefault ){
            return theEnum[key];
        }
    }
    return null;
};

function textInputHasValue(elem) {
    return $(elem).filter(function() { return $(this).val(); }).length > 0;
}