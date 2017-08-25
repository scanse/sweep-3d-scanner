// create the root namespace and making sure we're not overwriting it
var ScannerLib = {};

/************************************************************************************//**
** General purpose namespace method.
** This will allow us to create namespace a bit easier.
****************************************************************************************/
ScannerLib.createNameSpace = function (namespace) {
    let nsparts = namespace.split(".");
    let parent = ScannerLib;

    // we want to be able to include or exclude the root namespace 
    // So we strip it if it's in the namespace
    if (nsparts[0] === "ScannerLib") {
        nsparts = nsparts.slice(1);
    }

    // loop through the parts and create 
    // a nested namespace if necessary
    for (let i = 0; i < nsparts.length; i++) {
        let partname = nsparts[i];
        // check if the current parent already has 
        // the namespace declared, if not create it
        if (typeof parent[partname] === "undefined") {
            parent[partname] = {};
        }
        // get a reference to the deepest element 
        // in the hierarchy so far
        parent = parent[partname];
    }
    // the parent is now completely constructed 
    // with empty namespaces and can be used.
    return parent;
};


/************************************************************************************//**
** Create various namespaces for the app
****************************************************************************************/
ScannerLib.createNameSpace("ScannerLib.Utils");
ScannerLib.createNameSpace("ScannerLib.Settings");
ScannerLib.createNameSpace("ScannerLib.Requests");