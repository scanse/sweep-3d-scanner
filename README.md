# 3D Scanner Node Web Application 

## Dependencies
- nodejs 
- python + numpy module
- [libsweep](https://github.com/scanse/sweep-sdk/tree/master/libsweep)
- [sweeppy](https://github.com/scanse/sweep-sdk/tree/master/sweeppy)

**Note:** if you're only using the dummy scripts via the `-d` flag, then you DO NOT need `libsweep` or `sweeppy` installed.

## Quickstart (RaspberryPi)
- SSH into the RaspberryPi
- Install the dependencies from above on the the RaspberryPi

Then, to install the webapp:
```bash
# Clone the repo
git clone https://github.com/scanse/sweep-3d-scanner
# Install app dependencies
npm install
```

Once installed...
```bash
# Launch the app
node ./app.js
```

Then, use a web-browser (such as google chrome) to navigate to the Pi's address on the hosted port. For example, if the Pi creates an access point with IP address `172.24.1.1`, then navigate to  [`http://172.24.1.1:8080`](http://172.24.1.1:8080).

## Quickstart (Local Development using Dummy)
The `dummy` option replaces the normal python scripts (from the `scanner/` directory) with heavily modified dummy versions. These dummy scripts simulate the behavior of the scanning hardware. This enables rapid development of the webapp from a normal computer over localhost without requiring any scanner hardware or the installation of [libsweep](https://github.com/scanse/sweep-sdk/tree/master/libsweep) & [sweeppy](https://github.com/scanse/sweep-sdk/tree/master/sweeppy).

Install the webapp on your local machine:
```bash
# Clone the repo
git clone https://github.com/scanse/sweep-3d-scanner
# Install app dependencies
npm install
```

Once installed, execute the webapp with the dummy flag:
```bash
# Launch the dummy app
node ./app.js -d
```

Then, use a web-browser on same computer (such as google chrome) to navigate to [`http://127.0.0.1:8080`](http://127.0.0.1:8080) to use the webapp over local host with a simulated scanner.


## Design Goals:
- Simple dependencies or platform requirements
- Simple messaging (ie: printing stringied JSON)
- Simple languages (Javascript + python)
- Familiar/standard environments (Node + express)

## Concept:
- RaspberryPi creates a local access point/ hotspot and runs a small webserver so users can connect to the app from any device (phone or computer) without internet access.
- User connects to the RaspberryPi's access point
- User navigates to the hosted webpage using a browser
- User interacts with scanner via webpage GUI
  - Specify scan parameters
  - Submit scan requests
  - View list of recorded scan files
  - Download a specific file
  - Delete a specific file
  - Trigger small troubleshooting scripts that test various components. To be used during device assembly.
  - Shutdown RaspberryPi

## Design:
- node webserver (app)
  - express routing
  - jade templating for frontend
  - standard view + route directory structure
- simple client side javascript for user interaction
- app uses node's `child_process` module to spawn child processes that execute simple compartmentalized python scripts which interact with the sweep device (ie: perform scan)
- stdin of the main process (node) and the stdout of the child process (python) are piped together, such that print statements in python code are essentially messages received as JS events
- python code provides updates about the scan progress using a simple message format encoded as stringified JSON, which the backend JS can easily decode and feed right off to the client side JS at the client’s request

## directory structure
- `dummy_scanner/`: contains dummy versions of the scripts from the `scanner/` directory
- `output_scans/`: where .csv output scan files are stored
- `public/`: contains static files (express will look here)
  - `javascript/`: client-side javascript (includes sub-directory for every page)
  - `lib/`: libraries like jquery
  - `stylesheets/`: style related stuff
- `routes/`: contains scripts (1 per page) which handle routing + backend logic
- `scanner/`: contains python scripts for the actual scanner
- `views/`: contains jade templates (1 per page) which handle the front end view
- `app.js`: the main entry point to the app


## Alternatives:
Other branches provide some experimentation with more powerful and expandable solutions. See the outdated [zmq-ipc](https://github.com/scanse/sweep-3d-scanner/tree/zmq-ipc) branch for a WIP using distributed zeromq patterns with a message schema like protobuff. This could extend the capabilities beyond IPC, to messaging external applications.

## Contributing:
...