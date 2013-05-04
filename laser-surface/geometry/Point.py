'''
Created on Oct 15, 2012

@author: kinsp1
'''
import math

class Point(object):
    '''
    point as x, y, z
    '''
    
    def distance(self, other):
        return math.sqrt(math.pow((self.x - other.x), 2) + math.pow((self.y - other.y), 2) + math.pow((self.z - other.z), 2))

    def __init__(self, x, y, z):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
    
    '''returns a vector based on v guaranteed to be more or less aligned with this (a < 180)
        this method is ugly, ugly, ugly
    '''
    def align(self, v):
        _s = Point(self.x, self.y, self.z)
        _v = Point(v.x, v.y, v.z)
        
        angle = _s.angle(_v)
        if (angle < 180):
            return _v.copy
        else:
            return _v.multiplyConst(-1.0)
        
        
    def normalized(self):
        d = self.magnitude
        if d == 0:
            return Point(0,0,0)
        
        return Point(self.x / d, 
                       self.y / d, 
                       self.z / d)
    


    def compare(self, other):
        if round(self.x, 3) != round(other.x, 3):
            return False
        if round(self.y, 3) != round(other.y, 3):
            return False
        if round(self.z, 3) != round(other.z, 3):
            return False
        return True

    @property
    def copy(self):
        return Point(self.x, self.y, self.z)
    
    def __str__(self, *args, **kwargs):
        return "Point(" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ")"

    @property
    def magnitude(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def multiplyConst(self, c):
        return Point(self.x * c, self.y * c, self.z * c)


    def midPoint(self, other):
        return ( self + other ) / 2


    def vectorToPoint(self, to):
        dX = to.x - self.x
        dY = to.y - self.y
        dZ = to.z - self.z
        return Point(dX, dY, dZ)
    
    def dotProduct(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def angle(self, other):
        o = other.normalized()
        s = self.normalized()
        
        assert round(s.magnitude, 5) == 1.0, s.magnitude
        assert round(o.magnitude, 5) == 1.0, o.magnitude # because we just normalized. Will fail if magnitude starts as 0
        a = s.dotProduct(o) #/ (s.magnitude * o.magnitude) should always = 1
       
        if (a > 1):
            a = 1.0
          
        if (a < -1):
            a = -1.0
            
        b = math.acos(a)
        return math.degrees(b)
    
    def __div__(self, value):
        return Point(self.x / value, self.y / value, self.z / value)
    
    def __truediv__(self, other):
        return Point(self.x / other, self.y / other, self.z / other)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y, self.z - other.z)
        
    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __iadd__(self, other):
        return Point(self.x + other.x, self.y + other.y, self.z + other.z)
    
    
    #using 6 as an arbitrary rounding point
    def __eq__(self, other):
        if other == None:
            return False
        
        if round(self.x, 6) != round(other.x, 6):
            return False
        if round(self.y, 6) != round(other.y, 6):
            return False
        if round(self.z, 6) != round(other.z, 6):
            return False
        
        return True
    
    def __ne__(self, other):
        return not self.__eq__(other)

    def scale(self, scale):
        self.x = self.x * scale
        self.y = self.y * scale
        self.z = self.z * scale
    
    def __mul__(self, other):
        return Point(self.x * other.x, self.y * other.y, self.z * other.z)
    
    def normalizedAverage(self, other):
        _s = self.normalized()
        _o = other.normalized()
        return (_s + _o) / 2
    
    def average(self, other):
        return (self + other) / 2
    
    '''this is a vector, start is a point. currently uses vector len
    '''
    def getEndPoint(self, start, magnitude):
        
        v = self.normalized()
        v = v.multiplyConst(magnitude)
        
        return Point(start.x + v.x, start.y + v.y, start.z + v.z)
    
    '''angle where this is center, other points are a, b
    '''
    def angleThreePoints(self, a, b):
        vSA = self.vectorToPoint(a)
        vSB = self.vectorToPoint(b)
        return vSA.angle(vSB)
    
 
    
    
    
