"""Defines utility methods related to 3D scans"""
import argparse
import numpy as np
import transformations as tf


def polar_to_cartesian(radius, angle_deg):
    """Converts polar coordinate sample to cartesian coordinates
    :param radius:
    :param angle_deg:
    """

    theta = np.deg2rad(angle_deg)
    x = radius * np.cos(theta)
    y = radius * np.sin(theta)
    return(x, y)


def transform_scan(scan, mount_angle, base_angle_1, base_angle_2):
    """test
    :param mount_angle: the mount angle of the scanner relative to the horizontal
    :param base_angle_1: the angle of the base before moving
    :param base_angle_2: the angle of the base after moving
    """

    rot_mat_1 = get_scan_rotation_matrix(mount_angle, base_angle_1)
    rot_mat_2 = get_scan_rotation_matrix(mount_angle, base_angle_2)

    num_samples = len(scan.samples)

    # determine the index of the first reading past the 180 degree mark
    start_index_2 = num_samples
    for index, sample in enumerate(scan.samples):
        # Find first reading of the 2nd half of the scan
        # (180 deg = 180000 milli-deg)
        if sample.angle >= 180000:
            start_index_2 = index
            break

    # Divide the samples about the 180 deg mark
    num_samples_1 = start_index_2
    num_samples_2 = len(scan.samples) - start_index_2

    array_size = (num_samples, 4)
    array_size_1 = (num_samples_1, 4)
    array_size_2 = (num_samples_2, 4)

    coords = np.zeros(array_size)
    coords_1 = np.zeros(array_size_1)
    coords_2 = np.zeros(array_size_2)

    for index, sample in enumerate(scan.samples):
        # sample.angle is in milli-degrees, and must be converted to degrees
        cartesian_coord = polar_to_cartesian(
            sample.distance, 0.001 * sample.angle)
        homogeneous_coord = np.array(
            [cartesian_coord[0], cartesian_coord[1], 0, 1])

        if sample.angle < 180000:
            coords_1[index] = homogeneous_coord
        else:
            coords_2[index - num_samples_1] = homogeneous_coord

    # transform each half of the scan with the appropriate base angle
    coords_1 = np.dot(coords_1, rot_mat_1.T)
    coords_2 = np.dot(coords_2, rot_mat_2.T)

    # combine the transformed halves into a single array of coordinates
    for i in range(0, num_samples_1):
        coords[i] = coords_1[i]
    for i in range(num_samples_1, num_samples):
        coords[i] = coords_2[i - num_samples_1]

    return coords


def get_scan_rotation_matrix(mount_angle, base_angle):
    """Creates a rotation matrix from mount and base angles
    :param mount_angle:
    :param base_angle:
    """
    alpha = 0                       # rotation about y (roll)
    # negate mount_angle
    beta = np.deg2rad(-mount_angle)  # rotation about x (pitch, mount_angle)
    gamma = np.deg2rad(base_angle)  # rotation about z (yaw, base_angle)
    return tf.euler_matrix(alpha, beta, gamma, 'sxyz')


def remove_distance_extremes(scan, low, high):
    """Removes samples from the scan whose ranges are outside the specified range"""
    scan.samples[:] = [sample for sample in scan.samples if (
        sample.distance >= low and sample.distance <= high)]


def remove_angular_window(scan, low, high):
    """Removes samples from the scan whose angles are within the specified range"""
    # angle of samples is encoded in millidegrees
    scan.samples[:] = [sample for sample in scan.samples if (
        0.001 * sample.angle < low or 0.001 * sample.angle > high)]


def contains_unordered_samples(scan):
    """Returns true if the scan contains unordered samples
        (ie: no sample in the scan has an azimuth less than or equal to the preceding sample.)
    """
    previous_angle = -1
    for index, sample in enumerate(scan.samples):
        if sample.angle <= previous_angle:
            return True
        previous_angle = sample.angle
    return False


def main(arg_dict):
    """Main method"""
    if arg_dict['use_dummy'] is True:
        import dummy_sweeppy as sweeppy
    else:
        import sweeppy

    dummy_samples = [sweeppy.Sample(angle=1000 * 30 * n, distance=10, signal_strength=199)
                     for n in range(6)]
    dummy_scan = sweeppy.Scan(samples=dummy_samples)

    print len(dummy_scan.samples)
    print dummy_scan.samples
    remove_angular_window(dummy_scan, 31, 119)

    print len(dummy_scan.samples)
    print dummy_scan.samples

    mount_angle = 90
    base_angle = 90
    converted_coords = transform_scan(
        dummy_scan, mount_angle, base_angle - 1, base_angle)
    print converted_coords
    print converted_coords[2, 3]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Scan Utils Testing')
    parser.add_argument('-d', '--use_dummy',
                        help='Use the dummy verison without hardware',
                        default=False,
                        action='store_true',
                        required=False)

    args = parser.parse_args()
    argsdict = vars(args)

    main(argsdict)
