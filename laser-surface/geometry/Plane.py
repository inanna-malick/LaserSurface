'''
Created on Oct 15, 2012

@author: kinsp1
'''

from numpy import array, cross
import math
from geometry.Point import Point

def length(v):
    return math.sqrt(v[0] * v[0]) + math.sqrt(v[1] * v[1]) + math.sqrt(v[2] * v[2])

class Plane(object):
    '''
    a plane represented by ax + by + cz + d = 0
    '''

    def __init__(self, a, b, c):
        '''
        3 points. go the point vector vector route
        from http://www.jtaylor1142001.net/calcjat/Solutions/VPlanes/VP3Pts.htm
        '''
        
        ab = array([b.x - a.x, b.y - a.y, b.z - a.z])
        ac = array([c.x - a.x, c.y - a.y, c.z - a.z])
        crossProduct = cross(ab, ac)
        assert length(crossProduct) != 0.0
        crossProduct /= length(crossProduct)
        
        self.normalV = crossProduct
        #self.a = a
        #self.b = b
        #self.c = c


    def intersectionVector(self, other, point):
        lineVector = cross(self.normalV, other.normalV)
        lineVector /= length(lineVector)
        return Point(lineVector[0], lineVector[1], lineVector[2])

    """ 
    def intersection(self, other, point):
        lineVector = cross(self.normalV, other.normalV)
        
        lineVector /= length(lineVector)
        
        return Line(point, lineVector)
    """
    
    
    def angle(self, other):
        return math.degrees(math.acos(self.normalV.dot(other.normalV)))
    
    
    def __eq__(self, other):
        if self.a != other.a:
            return False
        if self.b != other.b:
            return False
        if self.c != other.c:
            return False

        return True
    
    
    def __ne__(self, other):
        return not self.__eq__(other)