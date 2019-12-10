__author__      = "Sven Hecht"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Sven Hecht"
__email__ = "info@shdev.de"
__status__ = "Production"

from random import *
from math import *

class Vector:
    def __init__(self, x=0, y=0):
        self.x = 0
        self.y = 0
        if isinstance(x, tuple) or isinstance(x, list):
            y = x[1]
            x = x[0]
        elif isinstance(x, Vector):
            y = x.y
            x = x.x
        
        self.set(x,y)

    @staticmethod
    def random(size=1):
        sizex = size
        sizey = size
        if isinstance(size, tuple) or isinstance(size, list):
            sizex = size[0]
            sizey = size[1]
        elif isinstance(size, Vector):
            sizex = size.x
            sizey = size.y
        return Vector(random() * sizex, random() * sizey)

    @staticmethod
    def distance(a, b):
        return (a - b).get_length()

    @staticmethod
    def angle(v1, v2):
      return acos(v1.dotproduct(v2) / (v1.get_length() * v2.get_length()))

    @staticmethod
    def angle_deg(v1, v2):
      return Vector.angle(v1,v2) * 180.0 / pi

    @staticmethod
    def from_circular(theta, radius):
        return Vector(
            cos(theta) * radius,
            -sin(theta) * radius
        )

    def get_circular(self):
        return (atan2(-self.y, self.x), self.get_length())
    
    def set(self, x,y):
        self.x = x
        self.y = y
    
    def get_array(self): return [self.x, self.y]
    def get_integer(self): return Vector(int(self.x), int(self.y))

    def get_normalized(self): 
        l = self.get_length()
        if l != 0:
            return Vector(self.x / l, self.y / l)
        else: return Vector(0,0)
    
    def dot_product(self, other):
        if isinstance(other, Vector):
            return self.x * other.x + self.y * other.y
        elif  isinstance(other, tuple) or isinstance(other, list):
            return self.x * other[0] + self.y * other[1]
        else:
            return NotImplemented
    def __add__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y)
        elif  isinstance(other, tuple) or isinstance(other, list):
            return Vector(self.x + other[0], self.y + other[1])
        elif isinstance(other, int) or isinstance(other, float):
            return Vector(self.x + other, self.y + other)
        else:
            return NotImplemented
    def __sub__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x - other.x, self.y - other.y)
        if  isinstance(other, tuple) or isinstance(other, list):
            return Vector(self.x - other[0], self.y - other[1])
        elif isinstance(other, int) or isinstance(other, float):
            return Vector(self.x - other, self.y - other)
        else:
            return NotImplemented
    def __rsub__(self, other):
        if isinstance(other, Vector):
            return Vector(other.x - self.x, other.y - self.y)
        elif  isinstance(other, tuple) or isinstance(other, list):
            return Vector(other[0] - self.x, other[1] - self.y)
        elif isinstance(other, int) or isinstance(other, float):
            return Vector(other - self.x, other - self.y)
        else:
            return NotImplemented
    def __mul__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x * other.x, self.y * other.y)
        elif  isinstance(other, tuple) or isinstance(other, list):
            return Vector(self.x * other[0], self.y * other[1])
        elif isinstance(other, int) or isinstance(other, float):
            return Vector(self.x * other, self.y * other)
        else:
            return NotImplemented
    def __div__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x / other.x, self.y / other.y)
        elif  isinstance(other, tuple) or isinstance(other, list):
            return Vector(self.x / other[0], self.y / other[1])
        elif isinstance(other, int) or isinstance(other, float):
            return Vector(self.x / other, self.y / other)
        else:
            return NotImplemented
    def __rdiv__(self, other):
        if isinstance(other, Vector):
            return Vector(other.x / self.x, other.y / self.y)
        elif  isinstance(other, tuple) or isinstance(other, list):
            return Vector(other[0] / self.x, other[1] / self.y)
        elif isinstance(other, int) or isinstance(other, float):
            return Vector(other / self.x, other / self.y)
        else:
            return NotImplemented
    def __pow__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return Vector(self.x ** other, self.y ** other)
        else:
            return NotImplemented
    
    def __iadd__(self, other):
        if isinstance(other, Vector):
            self.x += other.x
            self.y += other.y
            return self
        elif  isinstance(other, tuple) or isinstance(other, list):
            self.x += other[0]
            self.y += other[1]
            return self
        elif isinstance(other, int) or isinstance(other, float):
            self.x += other
            self.y += other
            return self
        else:
            return NotImplemented
    def __isub__(self, other):
        if isinstance(other, Vector):
            self.x -= other.x
            self.y -= other.y
            return self
        elif  isinstance(other, tuple) or isinstance(other, list):
            self.x -= other[0]
            self.y -= other[1]
            return self
        elif isinstance(other, int) or isinstance(other, float):
            self.x -= other
            self.y -= other
            return self
        else:
            return NotImplemented
    def __imul__(self, other):
        if isinstance(other, Vector):
            self.x *= other.x
            self.y *= other.y
            return self
        elif  isinstance(other, tuple) or isinstance(other, list):
            self.x *= other[0]
            self.y *= other[1]
            return self
        elif isinstance(other, int) or isinstance(other, float):
            self.x *= other
            self.y *= other
            return self
        else:
            return NotImplemented
    def __idiv__(self, other):
        if isinstance(other, Vector):
            self.x /= other.x
            self.y /= other.y
            return self
        elif  isinstance(other, tuple) or isinstance(other, list):
            self.x /= other[0]
            self.y /= other[1]
            return self
        elif isinstance(other, int) or isinstance(other, float):
            self.x /= other
            self.y /= other
            return self
        else:
            return NotImplemented
    def __ipow__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            self.x **= other
            self.y **= other
            return self
        else:
            return NotImplemented
    
    def __eq__(self, other):
        if isinstance(other, Vector):
            return self.x == other.x and self.y == other.y
        else:
            return NotImplemented
    def __ne__(self, other):
        if isinstance(other, Vector):
            return self.x != other.x or self.y != other.y
        else:
            return NotImplemented
    def __gt__(self, other):
        if isinstance(other, Vector):
            return self.get_length() > other.get_length()
        else:
            return NotImplemented
    def __ge__(self, other):
        if isinstance(other, Vector):
            return self.get_length() >= other.get_length()
        else:
            return NotImplemented
    def __lt__(self, other):
        if isinstance(other, Vector):
            return self.get_length() < other.get_length()
        else:
            return NotImplemented
    def __le__(self, other):
        if isinstance(other, Vector):
            return self.get_length() <= other.get_length()
        else:
            return NotImplemented
    
    def __eq__(self, other):
        if isinstance(other, Vector):
            return self.x == other.x and self.y == other.y
        else:
            return NotImplemented
    
    #def __len__(self):
    #	return int(sqrt(self.x**2 + self.y**2))

    def get_length(self):
        return sqrt(self.x**2 + self.y**2)

    def get_sq_length(self):
        return (self.x**2 + self.y**2)
        
    def __getitem__(self, key):
        if key == "x" or key == "X" or key == 0 or key == "0":
            return self.x
        elif key == "y" or key == "Y" or key == 1 or key == "1":
            return self.y
    
    def __str__(self): return "[x: %(x)f, y: %(y)f]" % self
    def __repr__(self): return "{'x': %(x)f, 'y': %(y)f}" % self

    def __neg__(self): return Vector(-self.x, -self.y)