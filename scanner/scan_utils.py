"""Defines utility methods related to 3D scans"""
import sweeppy
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


def transform_scan(scan, mount_angle, base_angle):
    """test"""
    rot_mat = get_scan_rotation_matrix(mount_angle, base_angle)

    array_size = (len(scan.samples), 4)
    coords = np.zeros(array_size)

    for n, sample in enumerate(scan.samples):
        cartesian_coord = polar_to_cartesian(sample.distance, sample.angle)
        homogeneous_coord = np.array(
            [cartesian_coord[0], cartesian_coord[1], 0, 1])
        coords[n] = homogeneous_coord

    return np.dot(coords, rot_mat.T)


def get_scan_rotation_matrix(mount_angle, base_angle):
    """Creates a rotation matrix from mount and base angles
    :param mount_angle:
    :param base_angle:
    """
    alpha = 0                       # rotation about y (roll)
    beta = np.deg2rad(mount_angle)  # rotation about x (pitch, mount_angle)
    gamma = np.deg2rad(base_angle)  # rotation about z (yaw, base_angle)
    return tf.euler_matrix(alpha, beta, gamma, 'rxyz')


def remove_angular_window(scan, low, high):
    """Removes samples from the scan whose angles are within the specified range"""
    scan.samples[:] = [sample for sample in scan.samples if (
        sample.angle < low or sample.angle > high)]


def main():
    """Main method"""

    dummy_samples = [sweeppy.Sample(angle=30 * n, distance=10, signal_strength=199)
                     for n in range(6)]
    dummy_scan = sweeppy.Scan(samples=dummy_samples)

    print len(dummy_scan.samples)
    print dummy_scan.samples
    remove_angular_window(dummy_scan, 31, 119)

    print len(dummy_scan.samples)
    print dummy_scan.samples


    mount_angle = 90
    base_angle = 90
    converted_coords = transform_scan(dummy_scan, mount_angle, base_angle)
    print converted_coords
    print converted_coords[4, 2]

if __name__ == '__main__':
    main()
