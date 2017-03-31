"""Defines entites relevant to the exportation of scans"""
import sweeppy
import time
import datetime
import csv
import os.path
import scan_utils
import numpy as np


class ScanExporter(object):
    """The scan exporter.
    Attributes:
        file_name: the name of the destination file for exported scans
        file: the destination file for exported scans
        field_names: the fields for storage
        writer: the csv file writer
    """
    # Output directory for the exported file
    output_dir = 'output_scans'
    # Field names for the CSV
    # field_names = ['SCAN_INDEX', 'BASE_ANGLE',
    #              'ANGLE', 'DISTANCE', 'SIGNAL STRENGTH']
    field_names = ['SCAN_INDEX', 'X', 'Y', 'Z',
                   'SIGNAL_STRENGTH']

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

        print self.output_dir
        print self.file_name

        # Create an output directory for the scans if it doesn't exit
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # Create the file
        self.file = open(self.get_relative_file_path(), 'wb')
        # Create a writer to write to the CSV file
        self.writer = csv.DictWriter(self.file, fieldnames=self.field_names)
        # Write the header to the CSV
        self.writer.writeheader()

    def export_2D_scan(self, scan, scan_index, mount_angle, base_angle, CCW):
        """Exports the scan to the file
        :param scan:
        :param scan_index:
        :param mount_angle:
        :param base_angle:
        :param CCW: True if base rotates CCW during scan
        """
        print "Scan #{},\tcontains {} samples,\tangle: {} deg".format(
            scan_index, len(scan.samples), base_angle)

        converted_coords = scan_utils.transform_scan(
            scan, mount_angle, base_angle if CCW else -base_angle)

        for n, sample in enumerate(scan.samples):
            self.writer.writerow({
                'SCAN_INDEX': scan_index,
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


def main():
    """Creates a ScanExporter and exports a dummy scan"""

    exporter = ScanExporter()
    print exporter.get_relative_file_path()

    for base_angle in range(0, 11):
        dummy_samples = [sweeppy.Sample(angle=30 * n, distance=1000, signal_strength=199)
                         for n in range(11)]
        dummy_scan = sweeppy.Scan(samples=dummy_samples)

        exporter.export_2D_scan(dummy_scan, 0, 90, base_angle * 30, False)

if __name__ == '__main__':
    main()
