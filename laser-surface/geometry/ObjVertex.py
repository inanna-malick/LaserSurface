      
'''
a 3d point combined with its index from the source file as an alternative to comparing floats
'''
from geometry import sdxf
from geometry.Point import Point
from geometry.TwoDeeFace import DrawnText, buildCornerSlit
from geometry.constants import dimensions, constraints
import functools
import os
import planar

# edge as viewed from vertex
# useA true if vertA is this vertex, false if vertB is this vertex
class EdgeView(object):
    def __init__(self, edge, useA):
        self.edge = edge
        self.useA = useA
        
    def getTabVert(self):
        if self.useA:
            return self.edge.tabVertA
        else:
            return self.edge.tabVertB
        
        
    def getCornerVert(self):
        if self.useA:
            return self.edge.getPreviousCornerPoint()
        else:
            return self.edge.getNextCornerPoint()
        
                
    def getVert(self):
        if self.useA:
            return self.edge.vertA
        else:
            return self.edge.vertB

    def getOppositeVert(self):
        if self.useA:
            return self.edge.vertB
        else:
            return self.edge.vertA
        
    def pushBack(self, offset):
        if self.useA:
            edgeVec = self.edge.vertA.vectorToPoint(self.edge.vertB)
            self.edge.tabVertA = edgeVec.getEndPoint(self.edge.tabVertA, offset)    
        else:
            edgeVec = self.edge.vertB.vectorToPoint(self.edge.vertA)
            self.edge.tabVertB = edgeVec.getEndPoint(self.edge.tabVertB, offset)       
            
    def getBothCornerPoints(self):
        if self.useA:
            return self.edge.getBothCornerPointsA() 
        else:
            return self.edge.getBothCornerPointsB()      
        
    def getCornerLens(self):
        p = self.getBothCornerPoints()
        
        p2 = None
        if(p[1] != None):
            r = (self.getTabVert().distance(p[0]), self.getTabVert().distance(p[1]))
        else:
            r = (self.getTabVert().distance(p[0]),)
            
        return r
    
    def __eq__(self, other):
        if other == None:
            return False
        return self.index == other.index       
     
    def __hash__(self):
        return self.index.__hash__()
                
    @property
    def index(self):
        return self.edge.index
    
    @property
    def connectedId(self):
        return self.edge.connectedId
        
    # check pushback preconditions, return appropriate boolean
    # possibly refactor to list of functions? Would be fun.
    def pushBackAllowed(self):
        '''
        # check length of tab against minimum
        if self.connectedId != "n/a":
            if self.edge.tabMagnitude < constraints.TAB_EDGE_MIN_LEN:
                return False
        else:
            if self.edge.tabMagnitude < dimensions.PUSH_BACK_INCREMENT:
                return False
        '''
        if self.edge.tabMagnitude < constraints.min_tab_edge_len:
            return False        
        # check angle between edge and tabedge against minimum
        tabedgeV = self.getVert().vectorToPoint(self.getTabVert())
        edgeV = self.getVert().vectorToPoint(self.getOppositeVert())
        if tabedgeV.angle(edgeV) < constraints.EDGE_TABEDGE_MIN_ANGLE:
            return False

        # we made it!
        return True
    
    
    # check pushback preconditions, return appropriate boolean
    # possibly refactor to list of functions? Would be fun.
    def pushBackAllowed_min(self):
        # check length of tab against minimum
        #if self.connectedId != "n/a":
        #    if self.edge.tabMagnitude < constraints.TAB_EDGE_MIN_LEN:
        #        return False
        #else:
        if self.edge.tabMagnitude < dimensions.pushback_increment:
            return False
        
        # check angle between edge and tabedge against minimum
        tabedgeV = self.getVert().vectorToPoint(self.getTabVert())
        edgeV = self.getVert().vectorToPoint(self.getOppositeVert())
        if tabedgeV.angle(edgeV) < constraints.EDGE_TABEDGE_MIN_ANGLE:
            return False

        # we made it!
        return True
    
    def getCornerPoints(self):
        v = self.getVert()
        a = self.getTabVert()
        b = self.getCornerVert()
        return (v, a, b)
        
        
        
        
global_it = 0
    
        
def getDist(pair):
    return pair[0].getTabVert().distance( pair[1].getTabVert())

class ObjVertex(Point):
    def __init__(self, x, y, z, index= -1):
        Point.__init__(self, x, y, z)
        self.faces = []
        self.index = index

    
    # Do all pushbacks. return true if any changes made
    def doPushBackRound(self):

        changeMade1 = self.pushback_tabEdgeAngle()
        changeMade2 = self.pushback_tabEdgesMinAngle()
        changeMade3 = self.pushBack_CornerLen()
        changeMade4 = self.pushBack_tabVertDist()
        return changeMade1 or changeMade2 or changeMade3 or changeMade4
    

    def doPriorityPushback(self):
        return self.pushBack_CornerLen_byPriority()
    
    # pushback round. looks for tabverts with angle with edge > ~80
    def pushback_tabEdgeAngle(self):
        changeMade = False
        
        for edge in self.edges:
            cornerVert = edge.getVert()
            edgeVert = edge.getOppositeVert()
            tabVert = edge.getTabVert()
            angle = cornerVert.angleThreePoints(edgeVert, tabVert)
            if (angle > constraints.TAB_EDGE_MAX_ANGLE):
                    if edge.pushBackAllowed():
                        edge.pushBack(dimensions.pushback_increment)
                        changeMade = True    
                        
        return changeMade
    
    # pushback round. looks for any 2 tab edges with angle under ~20 
    def pushback_tabEdgesMinAngle(self):
        changeMade = False
        
        pairs = []
        for edge1 in self.edges:
            for edge2 in self.edges:
                if edge1.getTabVert() != edge2.getTabVert():
                    corners = edge1.getBothCornerPoints()
                    if (edge2.getTabVert() != corners[0]) and (edge2.getTabVert() != corners[1]):
                        pairs.append( [edge1, edge2] )
        
        for pair in pairs:
            edge1 = pair[0]
            edge2 = pair[1]
            if edge1.getVert().angleThreePoints(edge1.getTabVert(), edge2.getTabVert()) < constraints.MIN_TAB_TAB_ANGLE:
                #print(edge1.getVert().angleThreePoints(edge1.getTabVert(), edge2.getTabVert()))

                if pair[0].pushBackAllowed():
                    pair[0].pushBack(dimensions.pushback_increment)       
                    changeMade = True
                if pair[1].pushBackAllowed():
                    pair[1].pushBack(dimensions.pushback_increment)
                    changeMade = True

        return changeMade
    
    
    
    # pushback round. will apply pushback to each tabVert that is part of a corner edge with length less than constraints.MIN_CORNER_EDGE_LEN
    # prioritized, find ~5 edgeviews that are smallest edgeviews and pushback. repeat until it can't
    def pushBack_CornerLen_byPriority(self):
        changeMade = False
        
        # tuples (minCornerLen, edgeView)
        candidates = []
        
        for edge in self.edges:
            cornerLen = edge.getCornerLens()
            if min(cornerLen) < constraints.min_corner_edge_length:
                if edge.pushBackAllowed_min():
                    candidates.append( (min(cornerLen), edge) )
                    #edge.pushBack(dimensions.PUSH_BACK_INCREMENT)
                    #changeMade = True
                #else:
                #    print(min(cornerLen))
      
        candidates.sort(key=lambda a: a[0])
      
        for i, c in zip(range(5), candidates):
            c[1].pushBack(dimensions.pushback_increment)
            changeMade = True
      
      
        return changeMade
    
    
        
    # pushback round. will apply pushback to each tabVert that is part of a corner edge with length less than constraints.MIN_CORNER_EDGE_LEN
    def pushBack_CornerLen(self):
        changeMade = False
        for edge in self.edges:
            cornerLen = edge.getCornerLens()
            if min(cornerLen) < constraints.min_corner_edge_length:
                if edge.pushBackAllowed():
                    edge.pushBack(dimensions.pushback_increment)
                    changeMade = True
                #else:
                    #print(min(cornerLen))
      
        return changeMade
        
    # pushback round. will apply pushback to each tabVert that is closer than X to another tabVert
    def pushBack_tabVertDist(self):
        changeMade = False
        pairs = []
        for edge1 in self.edges:
            for edge2 in self.edges:
                if edge1.getTabVert() != edge2.getTabVert():
                    corners = edge1.getBothCornerPoints()
                    if (edge2.getTabVert() != corners[0]) and (edge2.getTabVert() != corners[1]):
                        pairs.append( [edge1, edge2] )


        for pair in pairs:
            if getDist(pair) < constraints.MIN_AROUND_VERTEX_POINT_DIST:
                if pair[0].pushBackAllowed():
                    pair[0].pushBack(dimensions.pushback_increment)       
                    changeMade = True
                if pair[1].pushBackAllowed():
                    pair[1].pushBack(dimensions.pushback_increment)
                    changeMade = True
                    
        return changeMade
   



    
    def buildFaceList(self):
        
        faceList = []
        
        faceslocal = self.faces[:]
        
        face0 = faceslocal[0]
        for edge in face0.edges:
            if edge.vertB == self:
                faceList.append(faceListEntry(EdgeView(edge, False), face0, EdgeView(edge.next, True)))
                faceslocal.remove(face0)
                
        
        while len(faceslocal) > 0:
            for face in faceslocal:
                for edge in face.edges:
                    if edge.vertB == self:
                        if edge == faceList[-1].secondEdge:
                            faceList.append(faceListEntry(EdgeView(edge, False), face, EdgeView(edge.next,True)))
                            faceslocal.remove(face)

            for face in faceslocal:
                for edge in face.edges:
                    if edge.vertA == self:
                        if edge == faceList[0].firstEdge:
                            faceList.insert(0, faceListEntry(EdgeView(edge.previous, False), face, EdgeView(edge, True)))
                            faceslocal.remove(face)
                
                
                
        self.faceList = faceList
        
    
    
    # build a list of edges touching vertex
    def buildEdgeViews(self):
        edgeViews = set()
        self.buildFaceList()

        edges = set()
        for face in self.faces:
            for edge in face.edges:
                edges.add(edge)


        for edge in edges:
            if edge.vertA == self:
                ev = EdgeView(edge, True)
                edgeViews.add(ev)
                
            if edge.vertB == self:
                ev = EdgeView(edge, False)
                edgeViews.add(ev)
                    
        self.edges = edgeViews

    
    
    
    def buildVerts2D(self, faceList):
        
        #assert functools.reduce(lambda x, y: x+y.angle, faceList, 0) < 360
        
        vc = vertexCorners()
        vc.angle = 0
        
        vc.addAnnotation(self.index, planar.Point(0,0), 0)
        
        edge0 = faceList[0].firstEdge
        
        length = self.distance(edge0.getTabVert())
        
        endPoint = planar.Vec2.polar(vc.angle, length)
        vc.lastPoint = endPoint
        vc.addEdgeLine((0, 0), (endPoint.x, endPoint.y))

        #iterate over edges, keep going while other edge in contact with point has a connected edge
        for face in faceList:
            vc.consumeFace(face)

        #assert vc.angle < 360
            
        return vc


    def buildCornerPointSet(self):
        return map(lambda x: [x.getVert(), x.getTabVert(), x.getCornerVert()], self.edges)

                
    def __str__(self):
        return "point:(" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ")"        
    
    def __hash__(self):
        return hash(self.index)


def buildVerts(vertList, directory):    
    results = [] 
    for v in vertList:
        segments = partitionFaceList(v.faceList)
        for segment in segments:
            results.append(v.buildVerts2D(segment))
        
    d = sdxf.Drawing()
    
    offset = 0

    for result in results:
        result.draw(d, planar.Point(offset, 0))  
        offset = (offset - result.minX) + result.maxX + 5
            
    d.saveas(os.path.join(directory, "corners"))
        
    
class vertexCorners():
    def __init__(self):
        self.lines = []
        self.annotations = []
        self.triangles = []
        
        self.topLines = []
        self.edgeLines = []
    
    def draw(self, d, offset):
        
        maxX = 0
        minX = 999
        
        for line in self.topLines:
            maxX = max([line[0][0]+offset.x, line[1][0]+offset.x, maxX])
            minX = min([line[0][0]+offset.x, line[1][0]+offset.x, minX])
            d.append(sdxf.Line(color=1, points=[(line[0][0]+offset.x, line[0][1]+offset.y, 0), (line[1][0]+offset.x, line[1][1]+offset.y, 0)]))    
        
        line = self.edgeLines[0]
        maxX = max([line[0][0]+offset.x, line[1][0]+offset.x, maxX])
        minX = min([line[0][0]+offset.x, line[1][0]+offset.x, minX])
        d.append(sdxf.Line(color=1, points=[(line[0][0]+offset.x, line[0][1]+offset.y, 0), (line[1][0]+offset.x, line[1][1]+offset.y, 0)]))    
        
        for line in self.edgeLines[1:-1]:
            maxX = max([line[0][0]+offset.x, line[1][0]+offset.x, maxX])
            minX = min([line[0][0]+offset.x, line[1][0]+offset.x, minX])
            d.append(sdxf.Line(color=2, points=[(line[0][0]+offset.x, line[0][1]+offset.y, 0), (line[1][0]+offset.x, line[1][1]+offset.y, 0)]))    
            
        line = self.edgeLines[-1]
        maxX = max([line[0][0]+offset.x, line[1][0]+offset.x, maxX])
        minX = min([line[0][0]+offset.x, line[1][0]+offset.x, minX])
        d.append(sdxf.Line(color=1, points=[(line[0][0]+offset.x, line[0][1]+offset.y, 0), (line[1][0]+offset.x, line[1][1]+offset.y, 0)]))    
                    
        for annotation in self.annotations:
            annotation.draw(d, offset)
        for triangle in self.triangles:
            buildCornerSlit(triangle[0], triangle[1], triangle[2]).draw(d, offset)
        
        self.maxX = maxX
        self.minX = minX
         
        return d
    
    def addTriangle(self, points):
        self.triangles.append(points)

    
    def addAnnotation(self, text, startPoint, angle=0):
        self.annotations.append(DrawnText(text, dimensions.small_text_size, startPoint, angle))
        
    def addLine(self, start, end):
        self.lines.append((start, end))

    def addTopLine(self, start, end):
        self.topLines.append((start, end))
        
    def addEdgeLine(self, start, end):
        self.edgeLines.append((start, end))
        

    
    def consumeFace(self, face):
        deltaAngle = face.firstEdge.getVert().angleThreePoints(face.firstEdge.getTabVert(), face.secondEdge.getTabVert())
        assert deltaAngle == face.angle
        
        self.angle += deltaAngle
        length = face.firstEdge.getVert().distance(face.secondEdge.getTabVert())
        endPoint = planar.Vec2.polar(self.angle, length)
        
        
        offsetPoint = planar.Vec2.polar(self.angle, 0.05)
        
        self.addEdgeLine((offsetPoint.x, offsetPoint.y), (endPoint.x, endPoint.y))
        self.addTopLine((self.lastPoint.x, self.lastPoint.y), (endPoint.x, endPoint.y))
        self.addAnnotation(face.face.id, endPoint, (self.lastPoint-endPoint).angle)
        
        self.addTriangle((planar.Point(0, 0), self.lastPoint, endPoint))
  
        self.lastPoint = endPoint

class faceListEntry():
    def __init__(self, firstEdge, face, secondEdge):
        self.firstEdge = firstEdge
        self.face = face
        self.secondEdge = secondEdge

    @property
    def angle(self):  
        return self.firstEdge.getVert().angleThreePoints(self.firstEdge.getTabVert(), self.secondEdge.getTabVert())
    
    def __str__(self):
        return "face:"+self.face.id      
    
    def __repr__(self):
        return '{id}:{number:.{digits}f}'.format(number=self.angle, digits=0, id=self.face.id)
            

def partitionFaceList(faceList):
    list_len = len(faceList) 

    results = []

    group = []
    angleSum = 0
    
    for i in range(list_len):
        # check if previously added + current + next is under limit
        if ( angleSum + faceList[i].angle ) > 360: #can't add the current triangle
            #done with this group, add it to result list and init new group with this edge for overlap
            results.append(group)
            group = []
            group.append(faceList[i - 1]) # intentional overlap by 1 triangle
            group.append(faceList[i])
            angleSum = faceList[i].angle + faceList[i-1].angle
        else:
            group.append(faceList[i])
            angleSum += faceList[i].angle

    
    if len(group) > 0:
        if faceList[0].firstEdge == faceList[-1].secondEdge:
            group.append(faceList[0])
        results.append(group)
    
    '''
    print(results)
    for result in results:
        assert functools.reduce(lambda x, y: x+y.angle, result, 0) < 360
    '''
        
    return results

    
    
    
    
    
