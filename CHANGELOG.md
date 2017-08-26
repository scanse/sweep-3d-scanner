# Changelog

## v0.4.2
This is an early pre release of the `sweep-3d-scanner` software package. The attached binary is a complete RaspberryPi image which can be unzipped and flashed to an SD card using etcher. Please see [instructions](https://github.com/scanse/sweep-3d-scanner/wiki/Setup).

**NOTE:** The software is still under heavy development, and should not be considered stable. This release has many known issues and bugs. Please read about them. Familiarize yourself with the known issues and then keep an eye out for odd behavior when using the scanner.

### Features
- RaspberryPi Host name changed from default `raspberrypi` to `sweep-3d-scanner`

### Improvements
- Improved front-end layout on mobile devices
- Refactor scanner scripts for readability
- Refactor front-end code

### Bugfixes
- Community forum navbar now points to forum page

### Known Issues
- Motor control in CCW direction is noisy, erratic and choppy. See #14 
- Occasionally, stepper motor is not released (base does not spin freely after scan is complete). Try releasing the motor using the `Release Motor` script from the `Component Testing` page before performing another scan. See #10 
- Occasionally scan does not start from the base home angle, resulting in the base hitting the end-stop before completing a 180 degree scan. See #11 
- Scanner script will hang if the Motor Hat is disconnected before performing the scan. See #5 

## v0.4.1
This is an early pre release of the `sweep-3d-scanner` software package. The attached binary is a complete RaspberryPi image which can be unzipped and flashed to an SD card using etcher. Please see [instructions](https://github.com/scanse/sweep-3d-scanner/wiki/Setup).

**NOTE:** The software is still under heavy development, and should not be considered stable. This release has many known issues and bugs. Please read about them. Familiarize yourself with the known issues and then keep an eye out for odd behavior when using the scanner.

### Features
- None

### Improvements
- Updated sweep-sdk to latest v1.2.3 at the time of release
- Simplified dummy. See #39 #1 #2
- Dummy now mimics selected settings. See #39 #1 #2
- Updated docs

### Bugfixes
- Fill gap in data resulting from split transform of each 2D scan. See #38


### Known Issues
- Motor control in CCW direction is noisy, erratic and choppy. See #14 
- Occasionally, stepper motor is not released (base does not spin freely after scan is complete). Try releasing the motor using the `Release Motor` script from the `Component Testing` page before performing another scan. See #10 
- Occasionally scan does not start from the base home angle, resulting in the base hitting the end-stop before completing a 180 degree scan. See #11 
- Scanner script will hang if the Motor Hat is disconnected before performing the scan. See #5 

## v0.4.0
This is an early pre release of the `sweep-3d-scanner` software package. The attached binary is a complete RaspberryPi image which can be unzipped and flashed to an SD card using etcher. Please see [instructions](https://github.com/scanse/sweep-3d-scanner/wiki/Setup).

**NOTE:** The software is still under heavy development, and should not be considered stable. This release has many known issues and bugs. Please read about them. Familiarize yourself with the known issues and then keep an eye out for odd behavior when using the scanner.

### Features
- None

### Improvements
- Fresh rebuilt image
- Updated version of Raspbian Jessie Lite
  - Releae date: 2017-07-05
  - Kernel Version 4.9
- Updated sweep-sdk to latest v1.2.2 at the time of release
- Consolidated routes
- Added release instructions
- Use POST when cancelling scan

### Bugfixes
- Version indicator in front-end navbar now shows current version.


### Known Issues
- Motor control in CCW direction is noisy, erratic and choppy. See #14 
- Occasionally, stepper motor is not released (base does not spin freely after scan is complete). Try releasing the motor using the `Release Motor` script from the `Component Testing` page before performing another scan. See #10 
- Occasionally scan does not start from the base home angle, resulting in the base hitting the end-stop before completing a 180 degree scan. See #11 
- Scanner script will hang if the Motor Hat is disconnected before performing the scan. See #5 
- Dummy scanner does not mimic selected settings. See #1  

## v0.3.0
This is an early pre release of the `sweep-3d-scanner` software package. The attached binary is a complete RaspberryPi image which can be unzipped and flashed to an SD card using etcher. Please see [instructions](https://github.com/scanse/sweep-3d-scanner/wiki/Setup).

**NOTE:** The software is still under heavy development, and should not be considered stable. This release has many known issues and bugs. Please read about them. Familiarize yourself with the known issues and then keep an eye out for odd behavior when using the scanner.

### Features
- Cancel a scan in progress

### Improvements
- Redirect to the 3D scanner home page before shutting down or rebooting Pi. Avoids accidentally repeating the action from a stored route left in the url field. Thanks to @drcpattison 
- Improved logging info when killing scans
- Avoids trying to kill a process that has already exited
- Reduces angular distortions resulting from 2D scans failing to validate

### Bugfixes
- Releasing the motor now works, both when running from component_testing page or when cleaning up after a failed scan
- Scan index is properly incremented. Relates to many issues including distorted scans, infinite scan phase and progress bar exceeding 100%. See #31 
- Scans are discarded on the basis of un-ordered samples instead of sample quantity. See #30 


### Known Issues
- Motor control in CCW direction is noisy, erratic and choppy. See #14 
- Occasionally, stepper motor is not released (base does not spin freely after scan is complete). Try releasing the motor using the `Release Motor` script from the `Component Testing` page before performing another scan. See #10 
- Occasionally scan does not start from the base home angle, resulting in the base hitting the end-stop before completing a 180 degree scan. See #11 
- Scanner script will hang if the Motor Hat is disconnected before performing the scan. See #5 
- Dummy scanner does not mimic selected settings. See #1  
- Front-end navbar indicates outdated version (v0.1). See #33 

## v0.2.2
This is an early pre release of the `sweep-3d-scanner` software package. The attached binary is a complete RaspberryPi image which can be unzipped and flashed to an SD card using etcher. Please see [instructions](https://github.com/scanse/sweep-3d-scanner/wiki/Setup).

**NOTE:** The software is still under heavy development, and should not be considered stable. This release has many known issues and bugs. Please read about them. Familiarize yourself with the known issues and then keep an eye out for odd behavior when using the scanner.

### Features
- Background process (node webserver) now logs stdout + stderr to file (`/home/pi/scanner_output.log`). File is overwritten on boot.

### Improvements
- Updated to use sweep-sdk-v1.1.2
- Easier to login with monitor + keyboard connected to the pi (less console clutter from webserver output)
- Relocated dummy scanner code to `scanner/dummy/` directory.
- Removed duplicate console logs from the webserver
- Webserver now outputs to stderr in the event of an error message over ipc

### Bugfixes
- None
 

### Known Issues
- Can miss scan indices resulting in distorted scan. See #31 
- Can discard valid scan. See #30 
- Release motors does not not work from the component testing page or when shutting down a failed scan.
- Motor control in CCW direction is noisy, erratic and choppy. See #14 
- Occasionally, stepper motor is not released (base does not spin freely after scan is complete). Try releasing the motor using the `Release Motor` script from the `Component Testing` page before performing another scan. See #10 
- Occasionally scan does not start from the base home angle, resulting in the base hitting the end-stop before completing a 180 degree scan. See #11 
- Scanner script will hang if the Motor Hat is disconnected before performing the scan. See #5 
- No ability to cancel or stop a scan in progress other than to restart/shutdown the pi from the homepage. See #3 
- Dummy scanner does not mimic selected settings. See #1  

## v0.2.1
This is an early pre release of the `sweep-3d-scanner` software package. The attached binary is a complete RaspberryPi image which can be unzipped and flashed to an SD card using etcher. Please see [instructions](https://github.com/scanse/sweep-3d-scanner/wiki/Setup).

**NOTE:** The software is still under heavy development, and should not be considered stable. This release has many known issues and bugs. Please read about them. Familiarize yourself with the known issues and then keep an eye out for odd behavior when using the scanner.

### Features
- None

### Improvements
- Base now resets more reliably

### Bugfixes
- Fixed a bug where the base would get stuck on the limit switch during reset. See #26 
 

### Known Issues
- Motor control in CCW direction is noisy, erratic and choppy. See #14 
- Occasionally, stepper motor is not released (base does not spin freely after scan is complete). Try releasing the motor using the `Release Motor` script from the `Component Testing` page before performing another scan. See #10 
- Occasionally scan does not start from the base home angle, resulting in the base hitting the end-stop before completing a 180 degree scan. See #11 
- Scanner script will hang if the Motor Hat is disconnected before performing the scan. See #5 
- No ability to cancel or stop a scan in progress other than to restart/shutdown the pi from the homepage. See #3 
- Dummy scanner does not mimic selected settings. See #1  

## v0.2.0
This is an early pre release of the `sweep-3d-scanner` software package. The attached binary is a complete RaspberryPi image which can be unzipped and flashed to an SD card using etcher. Please see [instructions](https://github.com/scanse/sweep-3d-scanner/wiki/Setup).

**NOTE:** The software is still under heavy development, and should not be considered stable. This release has many known issues and bugs. Please read about them. Familiarize yourself with the known issues and then keep an eye out for odd behavior when using the scanner.

### Features
- Increase FOV of scan (deadzone now starts at 135&deg; instead of 120&deg;

### Improvements
- Buffer status updates, such that the front-end (browser) feedback on the `Component Testing` page does not miss updates. See #15 
- Order scans chronologically in the file manager dropdown
- Improve front-end visibility of failed executions
- Adds automatic cleanup routine (set sweep to idle and release motors) after forceful shutdown

### Bugfixes
- Sweep Firmware `v1.4` fixes a bug where performing a scan would fail during the `Initiating scan...` phase on every other scan attempt. See #9 
- Fixed bug where both halves of each 2D scan were transformed using the same base angle, instead of half of the scan being transformed using the incremented angle (after base movement). See issue #19  
 

### Known Issues
- Motor control in CCW direction is noisy, erratic and choppy. See #14 
- Occasionally, stepper motor is not released (base does not spin freely after scan is complete). Try releasing the motor using the `Release Motor` script from the `Component Testing` page before performing another scan. See #10 
- Occasionally scan does not start from the base home angle, resulting in the base hitting the end-stop before completing a 180 degree scan. See #11 
- Scanner script will hang if the Motor Hat is disconnected before performing the scan. See #5 
- No ability to cancel or stop a scan in progress other than to restart/shutdown the pi from the homepage. See #3 
- Dummy scanner does not mimic selected settings. See #1  

## v0.1.1
This is an early pre release of the `sweep-3d-scanner` software package. The attached binary is a complete RaspberryPi image which can be unzipped and flashed to an SD card using etcher. Please see [instructions](https://github.com/scanse/sweep-3d-scanner/wiki/Setup).

**NOTE:** The software is still under heavy development, and should not be considered stable. This release has many known issues and bugs. Please read about them. Familiarize yourself with the known issues and then keep an eye out for odd behavior when using the scanner.

### Features
- Front-end (broswer) receives updates on the "component_testing" page

### Improvements
- Uses child_process module's built in kill rather than another exec module

### Bugfixes
- check for corrupted json messages
- increase delay between printing and flushing subsequent messages

### Known Issues
- Performing a scan will fail during the `Initiating scan...` phase on every other scan attempt. Delete the file produced by the failed scan and try again. The cause has been identified and a firmware update is in the works. See #9 
- Both halves of each 2D scan are transformed using the same base angle, instead of half of the scan being transformed using the incremented angle (after base movement). See issue #19  
- Front-end (browser) status updates/visual feedback on the `Component Testing` page are subject to missing updates. See #15 
- Motor control in CCW direction is noisy, erratic and choppy. See #14 
- Occasionally, stepper motor is not released (base does not spin freely after scan is complete). Try releasing the motor using the `Release Motor` script from the `Component Testing` page before performing another scan. See #10 
- Occasionally scan does not start from the base home angle, resulting in the base hitting the end-stop before completing a 180 degree scan. See #11 
- Scanner script will hang if the Motor Hat is disconnected before performing the scan. See #5 
- No ability to cancel or stop a scan in progress other than to restart/shutdown the pi from the homepage. See #3 
- Dummy scanner does not mimic selected settings. See #1  

## v0.1.0
This is an early pre release of the `sweep-3d-scanner` software package. The attached binary is a complete RaspberryPi image which can be unzipped and flashed to an SD card using etcher. Please see [instructions](https://github.com/scanse/sweep-3d-scanner/wiki/Setup).

**NOTE:** The software is still under heavy development, and should not be considered stable. This release has many known issues and bugs. Please read about them. Familiarize yourself with the known issues and then keep an eye out for odd behavior when using the scanner.

### Features
- initial release
### Improvements
- initial release
### Bugfixes
- initial release

### Known Issues
- Performing a scan will fail during the `Initiating scan...` phase on every other scan attempt. Delete the file produced by the failed scan and try again.
- `Component Testing` page does not provide status updates/visual feedback to the user via front-end (browser).
- Motor control in CCW direction is noisy, erratic and choppy.
- Occasionally, stepper motor is not released (base does not spin freely after scan is complete). Try releasing the motor using the `Release Motor` script from the `Component Testing` page before performing another scan.
- Occasionally scan does not start from the base home angle, resulting in the base hitting the end-stop before completing a 180 degree scan
- Scanner script will hang if the Motor Hat is disconnected before performing the scan
- No ability to cancel or stop a scan in progress other than to restart/shutdown the pi from the homepage
- Dummy scanner does not mimic selected settings