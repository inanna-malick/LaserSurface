'''
Created on Oct 29, 2012

@author: kinsp1
'''


from geometry.Plane import Plane


class SharedEdge(object):
    def __init__(self, vertA, vertB, face, edge):
        self.vertA = vertA
        self.vertB = vertB
        
        self.tabVertA = None
        self.tabVertB = None

        self.faces = [face]

        self.sharedEdgeNormal = face.normalV
        
        self.pointsCalculated = False
        
        self.reinforced = None
        
    @property
    def index(self):
        index = [self.vertA, self.vertB]
        index.sort(key=lambda vert: vert.index)
        return tuple(index)
        

    def __eq__(self, other):
        return self.index == other.index
    

    #build plane from point at end of edge vector and 2 points on edge
    @property
    def plane(self):
        v1 = self.sharedEdgeNormal
        p3 = v1 + self.vertA
        plane = Plane(self.vertA, self.vertB, p3)
        return plane
        

        

class Edge(object):
    def __init__(self, vertA, vertB, face, knownEdges): 
        self.faceId = face.id    
        self.face = face
        self.otherEdge = None
        
        # starts as false, set to true by findOrBuildSharedEdge if baseEdge is preexisting
        self.flipped = False
        
        #shared object for edges that share vertices
        self.baseEdge = self.findOrBuildSharedEdge(vertA, vertB, face, knownEdges)
        
        
    @property
    def maxX(self):
        return max(self.vertA.x, self.vertB.x)
        
    @property
    def minX(self):
        return min(self.vertA.x, self.vertB.x)

    @property
    def maxY(self):
        return max(self.vertA.y, self.vertB.y)
        
    @property
    def minY(self):
        return min(self.vertA.y, self.vertB.y)

    @property
    def maxZ(self):
        return max(self.vertA.z, self.vertB.z)
        
    @property
    def minZ(self):
        return min(self.vertA.z, self.vertB.z)


    @property
    def index(self):
        index = [self.vertA, self.vertB]
        index.sort(key=lambda vert: vert.index)
        return tuple(index)
        
    @property
    def calculated(self):
        return self.baseEdge.pointsCalculated
        
    @property
    def tabVertA(self):
        if self.flipped:
            return self.baseEdge.tabVertB
        else:
            return self.baseEdge.tabVertA
            
    @tabVertA.setter
    def tabVertA(self, value):
        if self.flipped:
            self.baseEdge.tabVertB = value
        else:
            self.baseEdge.tabVertA = value     
            
    @property
    def tabVertB(self):
        if self.flipped:
            return self.baseEdge.tabVertA
        else:
            return self.baseEdge.tabVertB
            
    @tabVertB.setter
    def tabVertB(self, value):
        if self.flipped:
            self.baseEdge.tabVertA = value
        else:
            self.baseEdge.tabVertB = value 
                                            
    @property
    def vertA(self):
        if self.flipped:
            return self.baseEdge.vertB
        else:
            return self.baseEdge.vertA

    @property
    def vertB(self):
        if self.flipped:
            return self.baseEdge.vertA
        else:
            return self.baseEdge.vertB    

        
    @vertA.setter
    def vertA(self, other):
        raise Exception()
    
    @vertB.setter
    def vertB(self, other):
        raise Exception()
    
    @property
    def connectedId(self):
        for f in self.baseEdge.faces:
            if f.id != self.face.id:
                return f.id
        return "n/a"
        
    @property
    def magnitude(self):
        return self.vertA.vectorToPoint(self.vertB).magnitude
    
    @property
    def tabMagnitude(self):
        return self.tabVertA.vectorToPoint(self.tabVertB).magnitude
    
    def findOrBuildSharedEdge(self, vertA, vertB, face, knownEdges):
        newSharedEdge = SharedEdge(vertA, vertB, face, self)
        for edge in knownEdges:
            if edge.baseEdge == newSharedEdge:
                self.linkEdge(edge)
                self.flipped = True
                return edge.baseEdge
        return newSharedEdge
        
    def calculatePlaneIntersect(self, other):
        if self.vertA == other.vertA or self.vertA == other.vertB:
            lineVector = self.plane.intersectionVector(other.plane, self.vertA)
            return self.baseEdge.sharedEdgeNormal.multiplyConst(-1).align(lineVector)
            
        if self.vertB == other.vertA or self.vertB == other.vertB:
            lineVector = self.plane.intersectionVector(other.plane, self.vertB)
            return self.baseEdge.sharedEdgeNormal.multiplyConst(-1).align(lineVector)
        
        raise Exception()
            
        
    def calculateEdgeIntersect(self, other):
        if self.vertA == other.vertA or self.vertA == other.vertB:
            return self.vertA
            
        if self.vertB == other.vertA or self.vertB == other.vertB:
            return self.vertB

    '''find vector from intersection vert to other end of this edge
    '''
    def calculateAlongEdgeVector(self, other):
        if self.vertA == other.vertA or self.vertA == other.vertB:
            return self.vertA.vectorToPoint(self.vertB)
            
        if self.vertB == other.vertA or self.vertB == other.vertB:
            return self.vertB.vectorToPoint(self.vertA)
        
        
        
    #build plane from point at end of edge vector and 2 points on edge
    @property
    def plane(self):
        v1 = self.baseEdge.sharedEdgeNormal
        p3 = v1 + self.vertA
        plane = Plane(self.vertA, self.vertB, p3)
        
        return plane
        
    
    
    def ensureConstraints(self):
        #check edge and tab lines are parallel
        edgeVector = self.vertA.vectorToPoint(self.vertB)
        tabVector = self.tabVertA.vectorToPoint(self.tabVertB)
        #tab and edge should always be parallel, and in the same direction
        assert round ( edgeVector.angle(tabVector), 4 ) == 0

    
    def linkEdge(self, edgeToLink):
        #we've linked these edges, so set their normal to the average of their face normals
        normal = self.face.normalV.normalizedAverage(edgeToLink.face.normalV).normalized()
        edgeToLink.baseEdge.sharedEdgeNormal = normal
        edgeToLink.baseEdge.faces.append(self.face)
        
        edgeToLink.otherEdge = self
        self.otherEdge = edgeToLink
        

        assert normal.angle(self.face.normalV) < 90
        assert normal.angle(edgeToLink.face.normalV) < 90
        

    
    def __str__(self):
        return "edge:(\n   "+ str(self.vertA.index) + ",\n   " + str(self.vertB.index) + "\n)"           
        
        
    def getNextCornerPoint(self):
        return self.next.tabVertA
        
    def getPreviousCornerPoint(self):
        return self.previous.tabVertB
    

    
    def getBothCornerPointsA(self):
        # other edge is in opposite direction, so if this one is next, other is previous
        if self.otherEdge != None:
            otherEdgeCornerLen = self.otherEdge.getNextCornerPoint()
            return (self.getPreviousCornerPoint(), otherEdgeCornerLen)

        return (self.getPreviousCornerPoint(), None)
    
    
    def getBothCornerPointsB(self):
        # other edge is in opposite direction, so if this one is next, other is previous
        if self.otherEdge != None:
            otherEdgeCorner = self.otherEdge.getPreviousCornerPoint()
            return (self.getNextCornerPoint(), otherEdgeCorner)

        return (self.getNextCornerPoint(), None)

    
    def __eq__(self, other):
        if other == None:
            return False
        return self.index == other.index        
        
    def __hash__(self):
        return self.index.__hash__()
        
        

        
        