import numpy as np
import matplotlib.pyplot as plt

class Gear(object):
    """Simple Gear object in python."""
    addendum = 1.0
    dedendum = 1.25
    def __init__(self, modulo,teeth,pressure_angle=20.0):
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

    def make_involute(self,points=20):
        """Base involute"""
        t = np.linspace(0,np.pi/6,num=points)
        inv_x = self.base_radius * (np.cos(t)+(t)*np.sin(t))
        inv_y = self.base_radius * (np.sin(t)-(t)*np.cos(t))
        self.involute = np.stack((inv_x,inv_y),axis=1)
        return

    def make_tooth(self):
        """Create base all tooth"""
        ang_pitch = 2* np.pi / (self.teeth * 2 * 2) #Radians per teeth or valley
        low_tooth = self._rotate(ang_pitch,self.involute)
        high_tooth = np.copy(low_tooth)
        high_tooth[:,1] = -1 * low_tooth[:,1]
        self.base_tooth = np.concatenate((high_tooth,low_tooth))
        return

    def generate_gear(self):
        """Use base tooth to get full gear profile"""
        self.make_involute()
        self.make_tooth()
        self.gear_profile = np.copy(self.base_tooth)
        for t in np.linspace(0,2*np.pi,self.teeth):
            next_tooth = self._rotate(t,self.base_tooth)
            self.gear_profile = np.concatenate((next_tooth,self.gear_profile))

        return

    def _rotate(self,theta,v):
        """Rotate v arrary theta radians"""
        c,s =np.cos(theta),np.sin(theta)
        R = np.array( ( (c,-s) , (s,c) ) )
        rot = np.dot(v,R)
        return rot


def involute(r,a,points=100):
    t = np.linspace(0,np.pi/4,num=points)
    x = r *(np.cos(t)+(t-a)*np.sin(t))
    y = r *(np.sin(t)-(t-a)*np.cos(t))
    return x,y
    #return np.stack((x,y),axis=1)

def rotation(theta,v):
    c,s =np.cos(theta),np.sin(theta)
    R = np.array( ( (c,-s) , (s,c) ) )
    rot = np.dot(v,R)
    return rot

if __name__ == '__main__':
    radius = 2

    my_gear = Gear(10,25)
    my_gear.generate_gear()
    #print(my_gear.base_tooth)

    inv_x, inv_y = involute(radius,0,20)
    radial_step = 360/(20*2*2)
    xy = np.stack((inv_x,inv_y),axis=1)
    xy = rotation(np.radians(radial_step),xy)

    xy_mirror = np.copy(xy)
    xy_mirror[:,1] = xy[:,1] * -1

    xy = np.concatenate((xy, xy_mirror),axis=0)

    pitch_circle = plt.Circle((0, 0), my_gear.pitch_diameter /2 , color='r',fill=False)
    root_circle = plt.Circle((0, 0), my_gear.in_radius , color='b',fill=False)
    ext_circle = plt.Circle((0, 0), my_gear.out_radius , color='g',fill=False)
    base_circle = plt.Circle((0, 0), my_gear.base_radius , color='y',fill=False)
    fig, ax = plt.subplots()
    #plt.xlim(*my_gear.pitch_diameter /2,2*my_gear.pitch_diameter /2)
    #plt.ylim(-2*my_gear.pitch_diameter /2,2*my_gear.pitch_diameter /2)
    ax.set_aspect(1)
    ax.add_artist(pitch_circle)
    ax.add_artist(root_circle)
    ax.add_artist(ext_circle)
    ax.add_artist(base_circle)
    ax.plot(my_gear.gear_profile[:,0],my_gear.gear_profile[:,1])
    plt.show()
