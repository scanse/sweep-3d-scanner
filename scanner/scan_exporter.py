"""Defines entites relevant to the exportation of scans"""
import argparse
import time
import datetime
import csv
import os.path
import scan_utils


class ScanExporter(object):
    """The scan exporter.
    Attributes:
        file_name: the name of the destination file for exported scans
        file: the destination file for exported scans
        field_names: the fields for storage
        writer: the csv file writer
    """
    # Output directory for the exported file
    output_dir = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), '../output_scans')
    # Field names for the CSV
    field_names = ['X', 'Y', 'Z', 'SIGNAL_STRENGTH']

    def __init__(self, file_name=None):
        """Return a ScanExporter object
        :param file_name: the name of the destination file, defaults to a timestamp name
        """
        # default to timestamp file name
        if file_name is None:
            file_name = "Scan " + datetime.datetime.fromtimestamp(
                time.time()).strftime('%Y-%m-%d %H-%M-%S') + '.csv'

        #self.output_dir = os.path.split(file_name)[0]
        self.file_name = os.path.split(file_name)[1]

        # Create an output directory for the scans if it doesn't exit
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # Create the file
        self.file = open(self.get_relative_file_path(), 'wb')
        # Create a writer to write to the CSV file
        self.writer = csv.DictWriter(self.file, fieldnames=self.field_names)
        # Write the header to the CSV
        self.writer.writeheader()

    def export_2D_scan(self, scan, scan_index, angle_between_sweeps, mount_angle, CCW):
        """Exports the scan to the file
        :param scan:
        :param scan_index:
        :param mount_angle:
        :param angle_between_sweeps
        :param CCW: True if base rotates CCW during scan
        """
        if not CCW:
            angle_between_sweeps = -angle_between_sweeps

        # Base angle before base rotation
        base_angle_1 = scan_index * angle_between_sweeps
        # Base angle after base rotation
        base_angle_2 = (scan_index + 1) * angle_between_sweeps

        converted_coords = scan_utils.transform_scan(
            scan, mount_angle, base_angle_1, base_angle_2)

        for n, sample in enumerate(scan.samples):
            self.writer.writerow({
                'X': int(round(converted_coords[n, 0])),
                'Y': int(round(converted_coords[n, 1])),
                'Z': int(round(converted_coords[n, 2])),
                'SIGNAL_STRENGTH': sample.signal_strength
            })

    def get_relative_file_path(self):
        """Returns the relative path of the destination file"""
        return os.path.join(self.output_dir, self.file_name)

    def get_file_name(self):
        """Returns the name of the destination file"""
        return self.file_name


def main(arg_dict):
    """Creates a ScanExporter and exports a dummy scan"""
    if arg_dict['use_dummy'] is True:
        import dummy_sweeppy as sweeppy
    else:
        import sweeppy

    exporter = ScanExporter()

    index = 0
    for base_angle_scalar in range(0, 13):
        dummy_samples = [sweeppy.Sample(angle=1000 * 30 * n, distance=1000, signal_strength=199)
                         for n in range(12)]
        dummy_scan = sweeppy.Scan(samples=dummy_samples)

        exporter.export_2D_scan(
            dummy_scan,
            index,
            30,
            90,
            False)
        index = index + 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Scan Exporter Testing')
    parser.add_argument('-d', '--use_dummy',
                        help='Use the dummy verison without hardware',
                        default=False,
                        action='store_true',
                        required=False)

    args = parser.parse_args()
    argsdict = vars(args)

    main(argsdict)
