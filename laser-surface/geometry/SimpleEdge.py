'''
Created on Oct 16, 2012

@author: kinsp1
'''
import geometry.sdxf
import math

class SimpleEdge():
    def __init__(self, startPoint, endPoint, color=1, openEdge=None):
        self.color = color
        self.openEdge = openEdge
      
        self.startPoint = startPoint
        self.endPoint = endPoint
        
    @property
    def maxX(self):
        return max(self.startPoint.x, self.endPoint.x)
    
    @property
    def minX(self):
        return min(self.startPoint.x, self.endPoint.x)
                
        
    def shift(self, vector):
        self.startPoint = self.startPoint + vector
        self.endPoint = self.endPoint + vector

    def scale(self, scale_factor):
        self.startPoint = self.startPoint * scale_factor
        self.endPoint = self.endPoint * scale_factor

                
    def __str__(self):
        return "edge=>(" + str(self.startPoint) + ", " + str(self.endPoint) + ")"

        
    def draw(self, drawing, offset):
        drawing.append(geometry.sdxf.Line(color=self.color, points=[(self.startPoint.x + offset.x, self.startPoint.y + offset.y, 0), (self.endPoint.x + offset.x, self.endPoint.y + offset.y, 0)]))

    @property
    def magnitude(self):
        x = self.startPoint.x - self.endPoint.x
        y = self.startPoint.y - self.endPoint.y
        
        x = x * x
        y = y * y
        
        return math.sqrt(x + y)
        
        
class Circle():
    def __init__(self, center, radius, color):
        self.center = center
        self.radius = radius
        self.color = 2
        self.color=color
        

    def draw(self, drawing, offset):
        drawing.append(geometry.sdxf.Circle(color=self.color, center=(self.center.x + offset.x, self.center.y + offset.y, 0), radius=self.radius))


    @property
    def maxX(self):
        return self.center.x
    
    @property
    def minX(self):
        return self.center.x







