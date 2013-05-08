'''
Created on Aug 15, 2012

@author: kinsp1
'''

from geometry.constants import dimensions
from geometry import pyeuclid, constants
from geometry.ObjEdge import Edge
from geometry.Point import Point
import math


def normalFromPoints(vertA, vertB, vertC):
    vAB = vertA.vectorToPoint(vertB)
    vAC = vertA.vectorToPoint(vertC)
    vAB = pyeuclid.Vector3(vAB.x, vAB.y, vAB.z)
    vAC = pyeuclid.Vector3(vAC.x, vAC.y, vAC.z)
    calculatedNormal = vAB.cross(vAC)
    calculatedNormal = Point(calculatedNormal.x, calculatedNormal.y, calculatedNormal.z).normalized()
    return calculatedNormal.multiplyConst(-1.0)

class Face(object):
    def __init__(self, vertA, vertB, vertC, knownEdges, myid):
        self.id = myid
        
        self.calculateNormal(vertA, vertB, vertC)

        edges = []
        edges.append(Edge(vertA, vertB, self, knownEdges))
        edges.append(Edge(vertB, vertC, self, knownEdges))
        edges.append(Edge(vertC, vertA, self, knownEdges))
        
        #edges are a linked list, with previous and next linked
        for i in range(len(edges)):
            previousIndex = (i - 1) % 3
            nextIndex = (i + 1) % 3
            edge = edges[i]
            edge.previous = edges[previousIndex]
            edge.next = edges[nextIndex]
        
        
        knownEdges.extend(edges)
        self.edges = edges



    # calculate normal from vertex order
    def calculateNormal(self, vertA, vertB, vertC):
        self.normalV = normalFromPoints(vertA, vertB, vertC)#.multiplyConst(-1.0)
        
        assert round(self.normalV.angle(vertA.vectorToPoint(vertB))) == 90


    def buildObj(self, o):
        # build face
        if not constants.output_skeleton_only:
            o.buildFace((self.edges[0].vertA, self.edges[1].vertA, self.edges[2].vertA))
        
        # build tabs
        o.buildFace((self.edges[1].vertA, self.edges[1].tabVertA, self.edges[1].tabVertB, self.edges[1].vertB))
        o.buildFace((self.edges[2].vertA, self.edges[2].tabVertA, self.edges[2].tabVertB, self.edges[2].vertB))
        o.buildFace((self.edges[0].vertA, self.edges[0].tabVertA, self.edges[0].tabVertB, self.edges[0].vertB))
        
        # build corners
        o.buildFace((self.edges[0].vertB, self.edges[0].tabVertB, self.edges[1].tabVertA))
        o.buildFace((self.edges[1].vertB, self.edges[1].tabVertB, self.edges[2].tabVertA))
        o.buildFace((self.edges[2].vertB, self.edges[2].tabVertB, self.edges[0].tabVertA))

        
    def calculatePlanes(self):
        
        '''intersection lines between edge pairs
        ''' 
        self.vi01 = self.normalV.align(self.edges[0].calculatePlaneIntersect(self.edges[1]).multiplyConst(-1.0))
        self.vi12 = self.normalV.align(self.edges[1].calculatePlaneIntersect(self.edges[2]).multiplyConst(-1.0))
        self.vi20 = self.normalV.align(self.edges[2].calculatePlaneIntersect(self.edges[0]).multiplyConst(-1.0))
        
    @property
    def maxX(self):
        maxX = 0
        for edge in self.edges:
            maxX = max(maxX, edge.maxX)
        return maxX
        
    @property
    def minX(self):
        minX = 0
        for edge in self.edges:
            minX = min(minX, edge.minX)
        return minX
    
    @property
    def maxY(self):
        maxY = 0
        for edge in self.edges:
            maxY = max(maxY, edge.maxY)
        return maxY
        
    @property
    def minY(self):
        minY = 0
        for edge in self.edges:
            minY = min(minY, edge.minY)
        return minY
    
    @property
    def maxZ(self):
        maxZ = 0
        for edge in self.edges:
            maxZ = max(maxZ, edge.maxZ)
        return maxZ
        
    @property
    def minZ(self):
        minZ = 0
        for edge in self.edges:
            minZ = min(minZ, edge.minZ)
        return minZ        
        
    def findEdgeLen(self, vi):
        angle = vi.angle(self.normalV.multiplyConst(-1.0))
        l = abs(dimensions.tab_width / math.cos(math.radians(angle)))
        return l
    
    def shiftEdgeOrder(self):
        edgesNew = [self.edges[2], self.edges[0], self.edges[1]]
        self.edges = edgesNew
    


    def ensureEdgeConstraints(self):
        for edge in self.edges:
            edge.ensureConstraints()


    def calculatePoints3D(self):
        
        self.p01 = self.edges[0].calculateEdgeIntersect(self.edges[1])
        self.p12 = self.edges[1].calculateEdgeIntersect(self.edges[2])
        self.p20 = self.edges[2].calculateEdgeIntersect(self.edges[0])
        

        
        if not self.edges[0].calculated:
            self.edges[0].tabVertA = self.edges[0].baseEdge.sharedEdgeNormal.getEndPoint(self.p20, dimensions.tab_width)
            self.edges[0].tabVertB = self.edges[0].baseEdge.sharedEdgeNormal.getEndPoint(self.p01, dimensions.tab_width)
        
        if not self.edges[1].calculated:
            self.edges[1].tabVertA = self.edges[1].baseEdge.sharedEdgeNormal.getEndPoint(self.p01, dimensions.tab_width)
            self.edges[1].tabVertB = self.edges[1].baseEdge.sharedEdgeNormal.getEndPoint(self.p12, dimensions.tab_width)
        
        if not self.edges[2].calculated:
            self.edges[2].tabVertA = self.edges[2].baseEdge.sharedEdgeNormal.getEndPoint(self.p12, dimensions.tab_width)
            self.edges[2].tabVertB = self.edges[2].baseEdge.sharedEdgeNormal.getEndPoint(self.p20, dimensions.tab_width)        


        
        
    def ensureNoCrossingEdges(self):
        
        for edge in self.edges:
            
            edgeVector = edge.vertA.vectorToPoint(edge.vertB)
            tabVector = edge.tabVertA.vectorToPoint(edge.tabVertB)
            
            if round( edgeVector.angle(tabVector) ) == 180:
                
                # use line intersection instead
                edge.tabVertA = edge.tabVertA.midPoint(edge.tabVertB)
                edge.tabVertB = edge.tabVertA
                
                

    def __eq__(self, other):
        return self.id == other.id
    

    def __str__(self):
        return "face:(\n   " + str(self.vertA) + ",\n   " + str(self.vertB) + ",\n   " + str(self.vertC) + "\n)"           



