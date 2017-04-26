# 3D Scanner Node Web Application

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

## Development:
- dummy python scripts are provided to make rapid development easier

## Alternatives:
Other branches provide some experimentation with more powerful and expandable solutions. See the ???? branch for a WIP using distributed zeromq patterns with a message schema like protobuff.