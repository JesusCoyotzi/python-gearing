import numpy as np
import matplotlib.pyplot as plt
import argparse


class Gear(object):
    """Simple Gear object in python."""
    addendum = 1.0
    dedendum = 1.25

    def __init__(self, modulo, teeth, pressure_angle=20.0):
        self.modulo = modulo
        self.teeth = teeth
        self.pressure_angle = 20.0
        self.pitch_diameter = self.teeth * self.modulo
        self.diametral_pitch = self.teeth / self.pitch_diameter
        self.addendum = 1 / self.diametral_pitch
        self.dedendum = 1.25 / self.diametral_pitch

        pressure_radians = np.radians(pressure_angle)
        self.base_radius = self.pitch_diameter*np.cos(pressure_radians) / 2
        self.out_radius = self.pitch_diameter/2 + self.addendum
        self.in_radius = self.pitch_diameter/2 - self.dedendum

    def make_involute(self, points=20):
        """Base involute"""
        t_last = np.sqrt(np.square(self.out_radius) /
                         np.square(self.base_radius) - 1)
        t = np.linspace(0, t_last, num=points)
        inv_x = self.base_radius * (np.cos(t)+(t)*np.sin(t))
        inv_y = self.base_radius * (np.sin(t)-(t)*np.cos(t))
        self.involute = np.stack((inv_x, inv_y), axis=1)
        return

    def make_tooth(self):
        """Create base all tooth"""
        # There are 2pi radians in a circle, a gear with n teeth will need
        # One teeth-valley every 2pi/teeth radians
        # We offset the first tooth half that angular distance to center the involute with
        # respect the x-axis
        # Radians per teeth or valley
        ang_pitch = 2 * np.pi / (self.teeth * 2 * 2)
        # add dedendum
        full_depth = np.insert(self.involute, 0, [self.in_radius, 0], axis=0)
        low_tooth = self._rotate(ang_pitch, full_depth)
        high_tooth = np.copy(low_tooth)
        high_tooth[:, 1] = -1 * low_tooth[:, 1]
        high_tooth = high_tooth[::-1]
        self.base_tooth = np.concatenate((low_tooth, high_tooth))
        return

    def generate_gear(self):
        """Use base tooth to get full gear profile"""
        self.make_involute()
        self.make_tooth()
        start_angle = 2 * np.pi / (self.teeth)
        self.gear_profile = np.copy(self.base_tooth)
        for t in np.linspace(start_angle, 2*np.pi, self.teeth, endpoint=False):
            next_tooth = self._rotate(t, self.base_tooth)
            self.gear_profile = np.concatenate((next_tooth, self.gear_profile))

        return

    def _rotate(self, theta, v):
        """Rotate v arrary theta radians"""
        c, s = np.cos(theta), np.sin(theta)
        R = np.array(((c, -s), (s, c)))
        rot = np.dot(v, R)
        return rot


def draw_gear(gear):
    pitch_circle = plt.Circle(
        (0, 0), gear.pitch_diameter / 2, color='r', fill=False)
    root_circle = plt.Circle((0, 0), gear.in_radius, color='b', fill=False)
    ext_circle = plt.Circle((0, 0), gear.out_radius, color='g', fill=False)
    base_circle = plt.Circle((0, 0), gear.base_radius, color='y', fill=False)
    fig, ax = plt.subplots()
    # plt.xlim(*my_gear.pitch_diameter /2,2*my_gear.pitch_diameter /2)
    #plt.ylim(-2*my_gear.pitch_diameter /2,2*my_gear.pitch_diameter /2)
    ax.set_aspect(1)
    ax.add_artist(pitch_circle)
    ax.add_artist(root_circle)
    ax.add_artist(ext_circle)
    ax.add_artist(base_circle)
    ax.plot(gear.gear_profile[:, 0], gear.gear_profile[:, 1])
    plt.show()


# Test functions
def involute(r, a, points=100):
    t = np.linspace(0, np.pi/4, num=points)
    x = r * (np.cos(t)+(t-a)*np.sin(t))
    y = r * (np.sin(t)-(t-a)*np.cos(t))
    return x, y
    # return np.stack((x,y),axis=1)


def rotation(theta, v):
    c, s = np.cos(theta), np.sin(theta)
    R = np.array(((c, -s), (s, c)))
    rot = np.dot(v, R)
    return rot


def make_profile(radius, teeth):
    inv_x, inv_y = involute(radius, 0, 20)
    radial_step = 360/(teeth*2*2)
    xy = np.stack((inv_x, inv_y), axis=1)
    xy = rotation(np.radians(radial_step), xy)

    w_x, w_y = involute(radius, 0, 20)
    wxy = np.stack((inv_x, -inv_y), axis=1)
    xy = np.concatenate((xy, wxy), axis=0)
    return xy


def make_profile_rot(radius, teeth):
    inv_x, inv_y = involute(radius, 0, 20)
    radial_step = 360/(teeth*2*2)
    xy = np.stack((inv_x, inv_y), axis=1)
    xy = rotation(np.radians(radial_step), xy)

    wxy = np.copy(xy)
    wxy[:, 1] = -1 * wxy[:, 1]
    xy = np.concatenate((xy, wxy), axis=0)
    return xy


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Python involute gear generation')
    parser.add_argument('--module', action='store', type=float,
                        help='Gear module, only gears with the same module can mesh',
                        required=True)
    parser.add_argument('--n', action='store', type=int,
                        help='Number of teeth',
                        required=True)
    parser.add_argument('--store', action='store_true', default=False,
                        help='Store gear as plain text')
    parser.add_argument('--noplot', action='store_true', default=False,
                        help='Plot Gear')
    args = parser.parse_args()

    inv_gear = Gear(args.module, args.n)
    inv_gear.generate_gear()

    if not args.noplot:
        draw_gear(inv_gear)
    elif args.store:
        np.savetxt("gear-{}-{}.gear".format(args.module, args.n),
                   inv_gear.gear_profile)
