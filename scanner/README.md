# sweep-3d-scanner

# Use
```bash
python scanner.py
```


# Modules

## scanner

`Scanner` class defines a 3D scanner.

```python
"""Creates a 3D scanner and perform a 3D scan"""
with Sweep('/dev/ttyUSB0') as sweep:
    # Create a default scan settings obj
    settings = scan_settings.ScanSettings()
    # Create a default base obj
    base = scanner_base.ScannerBase()
    # Create a scanner object
    scanner = Scanner(device=sweep, base=base, settings=settings)

    # Setup the scanner
    scanner.setup()

    # Perform the scan
    scanner.perform_scan()
```

## scan_settings
`ScanSettings` class contains parameters and settings for a 3D scan.

```python
# Create a ScanSettings obj with default settings
default_params = ScanSettings()
# Create a ScanSettings obj with specific settings
custom_params = ScanSettings(
    sweep_helpers.MOTOR_SPEED_2_HZ,       # desired motor speed setting
    sweep_helpers.SAMPLE_RATE_750_HZ,     # desired sample rate setting
    120,                                    # desired deadzone angle threshold
    180,                                    # desired range of movement
    90                                      # mount angle of device relative to horizontal plane
)
```

## scanner_base

`ScannerBase` class defines the rotating base of the scanner.

```python
# create a base
base = ScannerBase()
# reset base to home position
base.reset()
# move base 90 degrees
for _ in itertools.repeat(None, 90):
    base.move_degrees(1)
    time.sleep(.1)  # sleep for 100 ms
```

## scan_utils

`scan_utils` module defines utility methods related to 3D scans.

## scan_exporter

`ScanExporter` class exports scan data to a point cloud csv file.

```python
exporter = ScanExporter()

index = 0
for base_angle in range(0, 11):
    dummy_samples = [sweeppy.Sample(angle=1000 * 30 * n, distance=1000, signal_strength=199)
                        for n in range(11)]
    dummy_scan = sweeppy.Scan(samples=dummy_samples)

    exporter.export_2D_scan(dummy_scan, index, 30, 90, False)
    index = index + 1
```

## sweep_helpers

`sweep_helpers` module defines constants for the sweep device.

## cleanup
`cleanup.py` is a simple script to cleanup any residual issues when testing scripts that fail. You can call with individual flags, or with multiple:
```bash
# stop any active data stream and set the sweep motor speed to idle (0Hz)
# release motors, in case the motor hat did not shutdown properly
python cleanup.py --idle_sweep --release_motor --use_dummy
```


# Dummy Version
The scripts `dummy_sweeppy.py`, `dummy_Adafruit_MotorHAT.py` and `dummy_GPIO` simulate the interface and behavior of the normal `sweeppy`, `Adafruit_MotorHAT` and `Rpi.GPIO` modules respectively. These scripts are imported if the dummy flag is passed to any script like so: 
```bash
python scanner.py --use_dummy
```

This allows the node application to develop on a local machine with fewer dependencies. When passed the `--use_dummy` flag, the `scanner.py` script only requires:
- python + numpy module

The following are NOT required:
- any physical hardware (sweep sensor or raspberry pi)
- installation of `libsweep` or `sweeppy`
- installation or even system compatibility with `Adafruit_MotorHAT` and `RPi.GPIO`