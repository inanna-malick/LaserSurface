      
'''
a 3d point combined with its index from the source file as an alternative to comparing floats
'''
from geometry.Point import Point
from geometry import  constants, sdxf
import planar
import math
from geometry.TwoDeeFace import DrawnText, buildCornerSlit
import os
import functools

# edge as viewed from vertex
# useA true if vertA is this vertex, false if vertB is this vertex
# advantage over meta-programming: edges can have N views, not just 1
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
            if self.edge.tabMagnitude < constants.TAB_EDGE_MIN_LEN:
                return False
        else:
            if self.edge.tabMagnitude < constants.PUSH_BACK_INCREMENT:
                return False
        '''
        if self.edge.tabMagnitude < constants.TAB_EDGE_MIN_LEN:
            return False        
        # check angle between edge and tabedge against minimum
        tabedgeV = self.getVert().vectorToPoint(self.getTabVert())
        edgeV = self.getVert().vectorToPoint(self.getOppositeVert())
        if tabedgeV.angle(edgeV) < constants.EDGE_TABEDGE_MIN_ANGLE:
            return False

        # we made it!
        return True
    
    
    # check pushback preconditions, return appropriate boolean
    # possibly refactor to list of functions? Would be fun.
    def pushBackAllowed_min(self):
        # check length of tab against minimum
        #if self.connectedId != "n/a":
        #    if self.edge.tabMagnitude < constants.TAB_EDGE_MIN_LEN:
        #        return False
        #else:
        if self.edge.tabMagnitude < constants.PUSH_BACK_INCREMENT:
            return False
        
        # check angle between edge and tabedge against minimum
        tabedgeV = self.getVert().vectorToPoint(self.getTabVert())
        edgeV = self.getVert().vectorToPoint(self.getOppositeVert())
        if tabedgeV.angle(edgeV) < constants.EDGE_TABEDGE_MIN_ANGLE:
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
        #print(changeMade1 or changeMade2 or changeMade3)
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
            if (angle > constants.TAB_EDGE_MAX_ANGLE):
                    if edge.pushBackAllowed():
                        edge.pushBack(constants.PUSH_BACK_INCREMENT)
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
            if edge1.getVert().angleThreePoints(edge1.getTabVert(), edge2.getTabVert()) < constants.MIN_TAB_TAB_ANGLE:
                #print(edge1.getVert().angleThreePoints(edge1.getTabVert(), edge2.getTabVert()))

                if pair[0].pushBackAllowed():
                    pair[0].pushBack(constants.PUSH_BACK_INCREMENT)       
                    changeMade = True
                if pair[1].pushBackAllowed():
                    pair[1].pushBack(constants.PUSH_BACK_INCREMENT)
                    changeMade = True

        return changeMade
    
    
    
    # pushback round. will apply pushback to each tabVert that is part of a corner edge with length less than constants.MIN_CORNER_EDGE_LEN
    # prioritized, find ~5 edgeviews that are smallest edgeviews and pushback. repeat until it can't
    def pushBack_CornerLen_byPriority(self):
        changeMade = False
        
        # tuples (minCornerLen, edgeView)
        candidates = []
        
        for edge in self.edges:
            cornerLen = edge.getCornerLens()
            if min(cornerLen) < constants.MIN_CORNER_EDGE_LEN:
                if edge.pushBackAllowed_min():
                    candidates.append( (min(cornerLen), edge) )
                    #edge.pushBack(constants.PUSH_BACK_INCREMENT)
                    #changeMade = True
                #else:
                #    print(min(cornerLen))
      
        candidates.sort(key=lambda a: a[0])
      
        for i, c in zip(range(5), candidates):
            c[1].pushBack(constants.PUSH_BACK_INCREMENT)
            changeMade = True
      
      
        return changeMade
    
    
        
    # pushback round. will apply pushback to each tabVert that is part of a corner edge with length less than constants.MIN_CORNER_EDGE_LEN
    def pushBack_CornerLen(self):
        changeMade = False
        for edge in self.edges:
            cornerLen = edge.getCornerLens()
            if min(cornerLen) < constants.MIN_CORNER_EDGE_LEN:
                if edge.pushBackAllowed():
                    edge.pushBack(constants.PUSH_BACK_INCREMENT)
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
            if getDist(pair) < constants.MIN_AROUND_VERTEX_POINT_DIST:
                if pair[0].pushBackAllowed():
                    pair[0].pushBack(constants.PUSH_BACK_INCREMENT)       
                    changeMade = True
                if pair[1].pushBackAllowed():
                    pair[1].pushBack(constants.PUSH_BACK_INCREMENT)
                    changeMade = True
                    
        return changeMade
   

    
    
    def buildFaceLinkedList(self):
        root = None
        
        faceslocal = self.faces[:]
        
        face0 = faceslocal[0]
        for edge in face0.edges:
            if edge.vertB == self:
                assert root == None
                root = faceListEntry(EdgeView(edge, False), face0, EdgeView(edge.next, True))
                faceslocal.remove(face0)
                
        
        while len(faceslocal) > 0:
            for face in faceslocal:
                for edge in face.edges:
                    if edge.vertB == self: # check if this triangle can be added to the end of the list
                        if edge == root.last.secondEdge:
                            root.append(faceListEntry(EdgeView(edge, False), face, EdgeView(edge.next,True)))
                            faceslocal.remove(face)

            for face in faceslocal:
                for edge in face.edges:
                    if edge.vertA == self: # check if this triangle can be added to the begining of the list
                        if edge == root.first.firstEdge:
                            root.prepend(faceListEntry(EdgeView(edge.previous, False), face, EdgeView(edge, True)))
                            faceslocal.remove(face)
        
        
        #check if list should be circular
        if root.first.firstEdge == root.last.lastEdge:
            root.first.before = root.last
            root.last.after = root.first    
                
        self.faceLL = root


    
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
        
    '''
    # instead of taking index, iterate over edges while their sum angle (plus extra edge for connection) is less than <constant>. for now, use 270
    def buildVerts2DSegment(self, firstIdx, lastIdx):        
        
        #partitionFaceList_from_n(self.faceList, 0)
        
        vc = vertexCorners()
        vc.angle = 0
        
        vc.addAnnotation(self.index, planar.Point(0,0), 0)  

        
        edge0 = self.faceList[firstIdx].firstEdge
        length = self.distance(edge0.getTabVert())
        
        endPoint = planar.Vec2.polar(vc.angle, length)
        vc.lastPoint = endPoint
        vc.addEdgeLine((0, 0), (endPoint.x, endPoint.y))
        
        #iterate over edges, keep going while other edge in contact with point has a connected edge
        for face in self.faceList[firstIdx:lastIdx+1]:
            vc.consumeFace(face)
            
            
        # only if this segment goes to the end
        if lastIdx == (len(self.faceList) - 1):
            # if true, the circle of corners is linked, and we must draw one more edge
            if self.faceList[0].firstEdge == self.faceList[len(self.faceList) -1].secondEdge:
                vc.consumeFace(self.faceList[0])       
        
        return vc
    '''
    
    
    def buildVerts2D_LinkedList(self, root):
        '''
        foo = functools.reduce(lambda x, y: x+y.angle, faceList, 0)
        assert foo < 360
        '''
        
        vc = vertexCorners()
        vc.angle = 0
        
        vc.addAnnotation(self.index, planar.Point(0,0), 0)
        
        edge0 = root.first.firstEdge
        
        length = self.distance(edge0.getTabVert())
        
        endPoint = planar.Vec2.polar(vc.angle, length)
        vc.lastPoint = endPoint
        vc.addEdgeLine((0, 0), (endPoint.x, endPoint.y))

        #iterate over edges, keep going while other edge in contact with point has a connected edge
        face = root
        while face != None:
            vc.consumeFace(face)
            face = face.next

        assert vc.angle < 360
            
        return vc
    
    
    def buildVerts2D(self, faceList):
        
        foo = functools.reduce(lambda x, y: x+y.angle, faceList, 0)
        assert foo < 360
        
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

        assert vc.angle < 360
            
        return vc

    """
    def buildVerts2D(self):
        #partitionFaceList_from_n(self.faceList, 0)

        
        
        vc = vertexCorners()
        vc.angle = 0
        
        vc.addAnnotation(self.index, planar.Point(0,0), 0)  
        
        edge0 = self.faceList[0].firstEdge
        
        length = self.distance(edge0.getTabVert())
        
        endPoint = planar.Vec2.polar(vc.angle, length)
        vc.lastPoint = endPoint
        vc.addEdgeLine((0, 0), (endPoint.x, endPoint.y))

        #iterate over edges, keep going while other edge in contact with point has a connected edge
        for face in self.faceList:
            vc.consumeFace(face)

            
        # if true, the circle of corners is linked, and we must draw one more edge
        if self.faceList[0].firstEdge == self.faceList[len(self.faceList) -1].secondEdge:
            vc.consumeFace(face)
      
            
        return vc
    """
        
        
    def buildCornerPointSet(self):
        return map(lambda x: [x.getVert(), x.getTabVert(), x.getCornerVert()], self.edges)
        
        
        
        
                
    def __str__(self):
        return "point:(" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ")"        
    
    def __hash__(self):
        return hash(self.index)


def buildVerts(vertList, directory):    
    lineLists = []
    
    
    
    for v in vertList:
        '''
        if len(v.faceList) > 3:
            #midpoint is supposed to overlap
            midPoint = math.floor((len(v.faceList) -1) / 2)
            #print("midpoint: " + str(midPoint))
            lineLists.append(v.buildVerts2DSegment(0, midPoint))
            lineLists.append(v.buildVerts2DSegment(midPoint, len(v.faceList)-1))
        else:
        '''
        
        segments = partitionFaceList_from_n(v.faceList, 0)
        for segment in segments:
            lineLists.append(v.buildVerts2D(segment))
        
    d = sdxf.Drawing()
    
    offset = 0

    for llist in lineLists:
        llist.draw(d, planar.Point(offset, 0))  
        offset = (offset - llist.minX) + llist.maxX + 5
            
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
        self.annotations.append(DrawnText(text, constants.EDGE_ANNOTATION_HEIGHT, startPoint, angle))
        #print(text)
        
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

#NOT CIRCULAR YET
class faceListEntry():
    def __init__(self, firstEdge, face, secondEdge, before=None, after=None):
        self.before = before
        self.after = after
        self.firstEdge = firstEdge
        self.face = face
        self.secondEdge = secondEdge
            
    def __len__(self):
        total = 1
        if self.next != None:
            total += len(self.next)
        return total

    def prepend(self, n):
        if self.before == None:
            self.before = n
            n.after = self
        else:
            self.before.append(n)        
    
    def append(self, n):
        if self.after == None:
            self.after = n
            n.before = self
        else:
            self.after.append(n)

    @property
    def last(self):
        if self.after == None:
            return self
        else:
            return self.after.last


    @property
    def first(self):
        if self.before == None:
            return self
        else:
            return self.before.first

    @property
    def angle(self):  
        return self.firstEdge.getVert().angleThreePoints(self.firstEdge.getTabVert(), self.secondEdge.getTabVert())


    
    def __str__(self):
        return "face:"+self.face.id      
    
    def __repr__(self):
        return '{id}:{number:.{digits}f}'.format(number=self.angle, digits=0, id=self.face.id)
            
    #def angle(self):
    #    return self.firstEdge.getVert().angleThreePoints(self.firstEdge.getOppositeVert(), self.secondEdge.getOppositeVert())
    
"""
FUCK IT I'LL DO THIS LATER
#list of objects with angle, create overlapping slices with sum angle < 360,  min possible slice count
def partitionFaceList(faceList):
    possible_results = []
    for n in range(len(faceList)):
        possible_results.append(partitionFaceList_from_n(faceList, n))
    
    maxLen = len(max(possible_results, key=lambda x:len(x)))
    minLen = len(min(possible_results, key=lambda x:len(x)))
    '''
    for result in possible_results:
        print(result[0][0])
    '''
    if maxLen != minLen:
        print("maxPartition:{max}, minPartition:{min}".format(max=maxLen, min=minLen))
"""
    
        
def partitionFaceList_from_n(faceList, n):
    list_len = len(faceList) 
    assert list_len > n
    rotated_list = faceList[n:] + faceList[:n]

    list_of_lists = []
    
    print("splitting list: {}".format(rotated_list))
    
    group = []
    group.append(rotated_list[0])
    angleSum = rotated_list[0].angle

    
    for i in range(list_len):
        # check if previously added + current + next is under limit
        if ( angleSum + rotated_list[(i+1)%list_len].angle ) > 360: #can't add the current triangle
            #add the current one, but only as a tab to link the two

            #done with this group, add it to result list and init new group with this edge for overlap
            list_of_lists.append(group)
            print("result(a): {}".format(group))
            group = []
            group.append(rotated_list[i]) # intentional overlap by 1 triangle
            group.append(rotated_list[(i+1)%list_len])
            angleSum = rotated_list[i].angle

            
        else:
            group.append(rotated_list[(i+1)%list_len])
            angleSum += rotated_list[(i+1)%list_len].angle

    
    if len(group) > 0:
        if len(group) == 1:
            group.append(rotated_list[0])
        list_of_lists.append(group)
        print("result(b): {}".format(group))

    for result in list_of_lists:
        foo = functools.reduce(lambda x, y: x+y.angle, result, 0)
        assert foo < 360
        
    return list_of_lists
    
'''
def partitionFaceLinkedList(root):
    list_len = len(root) 

    list_of_lists = []
    
    
    group = root.copyNode()
    group.append(rotated_list[0])
    angleSum = rotated_list[0].angle

    
    for i in range(list_len):
        # check if previously added + current + next is under limit
        if ( angleSum + rotated_list[(i+1)%list_len].angle ) > 360: #can't add the current triangle
            #add the current one, but only as a tab to link the two

            #done with this group, add it to result list and init new group with this edge for overlap
            list_of_lists.append(group)
            group = []
            group.append(rotated_list[i]) # intentional overlap by 1 triangle
            group.append(rotated_list[(i+1)%list_len])
            angleSum = rotated_list[i].angle

            
        else:
            group.append(rotated_list[(i+1)%list_len])
            angleSum += rotated_list[(i+1)%list_len].angle

    
    if len(group) > 0:
        if len(group) == 1:
            group.append(rotated_list[0])
        list_of_lists.append(group)

    for result in list_of_lists:
        foo = functools.reduce(lambda x, y: x+y.angle, result, 0)
        assert foo < 360
        
    return list_of_lists    
    
'''
    
    
    
    
    
    
    
    
    
