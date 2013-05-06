'''
Created on Dec 2, 2012

@author: kinsp1
'''

from geometry import sdxf
from geometry.SimpleEdge import SimpleEdge
from geometry import constants
from planar import Point

#from geometry.PlanarUtils import twoD_midPoint, twoD_lineAngle


class DrawnText():
    def __init__(self, text, height, startPoint, angle=0):
        self.text = text
        self.h = height
        self.p = startPoint
        self.angle = angle
        
    def shift(self, vector):
        self.p = self.p + vector
        
    def draw(self, drawing, offset):
        drawing.append(sdxf.Text(style="Annotative", text=self.text , height=self.h, rotation=self.angle, color=constants.colors.annotations, point=[self.p.x + offset.x, self.p.y + offset.y, 0]))

class TwoDeeFace(object):
    def __init__(self, face, initialAngle=0, initialPoint=Point(0,0)):
        self.edges = []
        self.annotations = []
        
        initialEdge0 = face.edges[0]
        initialEdge1 = face.edges[1]
        initialEdge2 = face.edges[2]
        
        # build initial 3 triangle points
        side0len = initialEdge0.magnitude
        side1len = initialEdge1.magnitude
        
        angle01 = initialEdge0.vertB.angleThreePoints(initialEdge2.vertB, initialEdge1.vertB)    
        
        twoDPoint20 = Point(0, 0)
        twoDPoint01 = twoDPoint20.plusPolar( side0len, initialAngle)
        twoDPoint12 = twoDPoint01.plusPolar( side1len, 180 - angle01 + initialAngle)
        
        # draw center annotation
        midpoint = (twoDPoint01+twoDPoint12)/2        
        midpoint = (midpoint+twoDPoint20)/2        
        centerAnnotation = DrawnText(initialEdge0.faceId, constants.CENTER_ANNOTATION_HEIGHT, midpoint)
        self.addAnnotation(centerAnnotation)
        
        self.buildEdge(initialEdge0, twoDPoint20, twoDPoint01, False)
        self.buildEdge(initialEdge1, twoDPoint01, twoDPoint12, False)
        self.buildEdge(initialEdge2, twoDPoint12, twoDPoint20, False)
    
        self.offset = initialPoint

        
    def addEdge(self, toAdd):
        self.edges.append(toAdd)
        
    def addAnnotation(self, toAdd):
        self.annotations.append(toAdd)
                
    @property
    def width(self):
        minX = 0
        maxX = 0
        for edge in self.edges:
            minX = min(minX, edge.minX)
            maxX = max(maxX, edge.maxX)
        return (maxX - minX)
            
        
    def drawSlit(self, tabVertA, tabVertB, slotLen):
        downwardAngle = (tabVertB-tabVertA).angle + 90
        mp = (tabVertA + tabVertB) / 2.0
        
        rt_slot = mp.plusPolar( 0.1, downwardAngle)
        rb_slot = rt_slot.plusPolar( slotLen, downwardAngle)
        self.addEdge(SimpleEdge(rt_slot, rb_slot, 5))
        
        
    def buildEdge(self, threeDeeEdge, vertA, vertB, gapEdge):
        
        # build folded edge
        edge = SimpleEdge(vertA, vertB, color=constants.colors.perforations)
        self.addEdge(edge)
        
        # build edge from vertA to tabA
        edgeAngle = (vertB-vertA).angle
        tabVertAngleA = edgeAngle - (threeDeeEdge.previous.vertB.angleThreePoints(threeDeeEdge.vertB, threeDeeEdge.tabVertA))
        tabVertA = vertA.plusPolar(threeDeeEdge.previous.vertB.distance(threeDeeEdge.tabVertA), tabVertAngleA)
        edgeTabEdgeA = SimpleEdge(vertA, tabVertA, color=constants.colors.perforations)
        self.addEdge(edgeTabEdgeA)
        

        # build edge from vertA to cornerA
        cornerVertAngleA = tabVertAngleA - threeDeeEdge.previous.vertB.angleThreePoints(threeDeeEdge.tabVertA, threeDeeEdge.previous.tabVertB)
        cornerVertA = vertA.plusPolar(threeDeeEdge.previous.vertB.distance(threeDeeEdge.previous.tabVertB), cornerVertAngleA)
        edgeCornerEdgeA = SimpleEdge(vertA, cornerVertA, color=constants.colors.cuts)
        self.addEdge(edgeCornerEdgeA)
        

        cornerTabEdge = SimpleEdge(cornerVertA, tabVertA, color = constants.colors.perforations)
        # build edge from tab to corner
        self.addEdge(cornerTabEdge)
        
        
        # build edge from vertB to tabB
        tabVertAngleB = (vertA-vertB).angle + threeDeeEdge.vertB.angleThreePoints(threeDeeEdge.previous.vertB, threeDeeEdge.tabVertB)
        tabVertB = vertB.plusPolar(threeDeeEdge.vertB.distance(threeDeeEdge.tabVertB), tabVertAngleB)
        edgeTabEdgeB = SimpleEdge(vertB, tabVertB, color=constants.colors.perforations)
        self.addEdge(edgeTabEdgeB)
        
        # build edge from vertB to cornerB
        cornerVertAngleB = tabVertAngleB + threeDeeEdge.vertB.angleThreePoints(threeDeeEdge.tabVertB, threeDeeEdge.next.tabVertA)
        cornerVertB = vertB.plusPolar( threeDeeEdge.vertB.distance(threeDeeEdge.next.tabVertA), cornerVertAngleB)
        edgeCornerEdgeB = SimpleEdge(vertB, cornerVertB, color=constants.colors.cuts)
        self.addEdge(edgeCornerEdgeB)        
        



        
        '''
        1. get line tabA-B, find intersection with corner
        '''
        

        #if(threeDeeEdge.connectedId != "n/a"):  
            
        #if threeDeeEdge.baseEdge.reinforced == None:
        reinfAngle = (tabVertB-tabVertA).angle - 90
        
        
        # outer tabs
        outertabA = tabVertA.plusPolar( constants.EDGE_OUT_LEN, reinfAngle)
        outertabB = tabVertB.plusPolar(  constants.EDGE_OUT_LEN , reinfAngle)        
        #self.addEdge(SimpleEdge(outertabA, outertabB, constants.colors.cuts))
        
        #angle between corner-tab line and tab-triangle line (NEED TERMINOLOGY THAT IS BETTER NOW PLS)
        tabAngle = (vertA-tabVertA).angle
        cornerAngle =  (cornerVertA-tabVertA).angle
        tab_cornerAngle = tabAngle - cornerAngle
        #draw us a line A
        pt2 = tabVertA.plusPolar( edgeTabEdgeA.magnitude, (cornerVertA-tabVertA).angle - tab_cornerAngle )
        intersectionLinesA = self.buildReflectedCorner(pt2, cornerVertA, tabVertA, tabVertB)
        
        intersectionPointA = findIntersection(outertabA, outertabB, intersectionLinesA)
        
        lowerIntersectionPointA = findIntersection(tabVertA, outertabA, intersectionLinesA)
        
        #angle between corner-tab line and tab-triangle line (NEED TERMINOLOGY THAT IS BETTER NOW PLS)
        tabAngle = (vertB-tabVertB).angle
        cornerAngle =  (cornerVertB-tabVertB).angle
        tab_cornerAngle = tabAngle - cornerAngle
        #draw us a line B
        pt2 = tabVertB.plusPolar( edgeTabEdgeB.magnitude, (cornerVertB-tabVertB).angle - tab_cornerAngle )
        intersectionLinesB = self.buildReflectedCorner(pt2, cornerVertB, tabVertB, tabVertA)
        
        intersectionPointB = findIntersection(outertabB, outertabA, intersectionLinesB)
        
        lowerIntersectionPointB = findIntersection(tabVertB, outertabB, intersectionLinesB)

        
        if intersectionPointA == None:
            if lowerIntersectionPointA == None:
                lowerIntersectionPointA = tabVertA
                print("a1")
            else:
                print("a2")
            self.addEdge(SimpleEdge(lowerIntersectionPointA, outertabA, constants.colors.cuts))
            intersectionPointA = outertabA
            
        if intersectionPointB == None:
            if lowerIntersectionPointB == None:
                lowerIntersectionPointB = tabVertB
                print("b1")
            else:
                print("b2")
            self.addEdge(SimpleEdge(lowerIntersectionPointB, outertabB, constants.colors.cuts))
            intersectionPointB = outertabB

        #outer tab
        self.addEdge(SimpleEdge(intersectionPointA, intersectionPointB, constants.colors.cuts))


          
        self.drawSlit(tabVertA, tabVertB, constants.SLOT_LEN)        
        self.drawSlit(tabVertB, tabVertA, constants.SLOT_LEN)        

        
        # build edge from tab to corner
        cornerTabEdge = SimpleEdge(cornerVertB, tabVertB, color=constants.colors.perforations)
        self.addEdge(cornerTabEdge)
        
        
        #tabs and slots in corners
        slitA = buildCornerSlit(vertA, tabVertA, cornerVertA)
        self.addEdge(slitA)
        
        slitB = buildCornerSlit(vertB, cornerVertB, tabVertB)
        self.addEdge(slitB)

        #for vertex-circle-linking
        self.addAnnotation(DrawnText(threeDeeEdge.vertB.index, constants.EDGE_ANNOTATION_HEIGHT, vertB, 0))
        
                
        #if threeDeeEdge.baseEdge.reinforced != None:
        self.addEdge(SimpleEdge(tabVertA, tabVertB, color=constants.colors.perforations))
        #else:
        #self.addEdge(SimpleEdge(tabVertA, tabVertB, color=constants.colors.perforations))
        #threeDeeEdge.baseEdge.reinforced = True
        

        # build annotation along tab edge to guarantee maximum space
        textStartPoint = tabVertA.plusPolar( constants.EDGE_OUT_LEN + ((constants.EDGE_OUT_LEN - constants.EDGE_ANNOTATION_HEIGHT) / 2), (vertB-vertA).angle+ 90)
        edgeAnnotation = DrawnText(text=threeDeeEdge.connectedId, height=constants.EDGE_ANNOTATION_HEIGHT, startPoint=textStartPoint, angle=(vertB-vertA).angle)
        self.addAnnotation(edgeAnnotation)        
        

        
    def buildReflectedCorner(self, new_cornerPoint, old_cornerPoint, tabPoint, oppositeTabPoint):
        #build slit
        self.addEdge(buildCornerSlit(new_cornerPoint, old_cornerPoint, tabPoint))
        
        
        slitOffset = 0.5
        
        innerSlit = old_cornerPoint.plusPolar( slitOffset, (new_cornerPoint-old_cornerPoint).angle)
        outerSlit = tabPoint.plusPolar( slitOffset, (new_cornerPoint-tabPoint).angle)
                
        #USE EDGE INTERSECTION
        possible = LineEquation(innerSlit, outerSlit)
        pt = possible.intersectionWithLine(LineEquation(tabPoint, oppositeTabPoint))
        intersection = isBetween(innerSlit, outerSlit, pt) and isBetween(tabPoint, oppositeTabPoint, pt)
        
        # TODO: draw only if no no_intersection with tab edge
        if not intersection:
            self.addEdge(SimpleEdge(tabPoint, outerSlit, constants.colors.cuts))

        
        # TODO: chop off edge if no_intersection with tab edge
        if intersection:
            outerSlit = pt
            
        self.addEdge(SimpleEdge(innerSlit, outerSlit, constants.colors.cuts))
        
        
        
        self.addEdge(SimpleEdge(old_cornerPoint, innerSlit, constants.colors.cuts))
        
        
        
        
        # return the three possible lines that the tab line could intersect with
        return ((tabPoint, outerSlit), (innerSlit, outerSlit), (old_cornerPoint, innerSlit))


        
    '''return (xMin, yMin), (xMax, yMax)
    '''
    def getBounds(self):
        xMin = self.edges[0].startPoint.x
        xMax = self.edges[0].startPoint.x
        yMin = self.edges[0].startPoint.y
        yMax = self.edges[0].startPoint.y
                
        for e in self.edges:
            xMin = min(xMin, e.startPoint.x)
            xMin = min(xMin, e.endPoint.x)
            
            xMax = max(xMax, e.startPoint.x)
            xMax = max(xMax, e.endPoint.x)
          
            yMin = min(yMin, e.startPoint.y)
            yMin = min(yMin, e.endPoint.y)
            
            yMax = max(yMax, e.startPoint.y)
            yMax = max(yMax, e.endPoint.y)
        
        return ((xMin, yMin), (xMax, yMax))
    
    
    
    def printToFile(self, name):
        d = sdxf.Drawing()
        for e in self.edges:
            e.draw(d, Point(0, 0))
        for a in self.annotations:
            a.draw(d, Point(0, 0))
            d.append(a)
        d.saveas(name + ".dxf")
        
        
        
    def printToDrawing(self, d):
        #print("edge count: {}".format(len(self.edges)))
        for e in self.edges:
            e.draw(d, self.offset)
        for a in self.annotations:
            a.draw(d, self.offset)
            
            
            
    def shift(self, vector):
        for e in self.edges:
            e.shift(vector)
        for a in self.annotations:
            a.shift(vector)






def buildCornerSlit(cornerPoint, innerPoint, outerPoint):
    slitOffset = 0.25
    
    innerSlit = innerPoint.plusPolar( slitOffset, (cornerPoint-innerPoint).angle)
    outerSlit = outerPoint.plusPolar( slitOffset, (cornerPoint-outerPoint).angle)
    
    slitBisectorLen = abs(innerSlit - outerSlit)
    
    slitLen = 0.15
    
    slitA = innerSlit.plusPolar( (slitBisectorLen - slitLen)/2.0, (outerSlit-innerSlit).angle)
    slitB = outerSlit.plusPolar( (slitBisectorLen - slitLen)/2.0, (innerSlit-outerSlit).angle)
    
    return SimpleEdge(slitA, slitB, color=5)


    
class LineEquation():
    def __init__(self, pointA, pointB):
        self.pointA = pointA
        self.pointB = pointB
        dX = pointB.x -pointA.x
        dY = pointB.y - pointA.y
        
        if dX == 0:
            dX = 0.000001
            
        slope = dY / dX
        # y = mx + b
        # b = y - mx
        yIntercept = pointA.y - slope * pointA.x 
        
        self.slope = slope
        self.yIntercept = yIntercept
        
    # does point satisfy y = mx + b?
    def isPointOnLine(self, point):
        onLine = round(point.x * self.slope + self.yIntercept, 5) == round(point.y, 5)
        #onSegment = (point < self.pointB and point > self.pointA) or (point > self.pointB and point < self.pointA)
        
        return onLine# and onSegment

            
    def intersectionWithLine(self, lineEq):
        # m1x + b1 = m2x + b2
        # m1x - m2x =b2 - b1
        # (m1+m2) * x = b2-b1
        x = (lineEq.yIntercept - self.yIntercept) / (self.slope - lineEq.slope)
        y = self.slope * x + self.yIntercept
        return Point(x, y)
          

def isBetween(a, b, c):
    crossproduct = (c.y - a.y) * (b.x - a.x) - (c.x - a.x) * (b.y - a.y)
    if abs(crossproduct) > 0.01 : return False   # (or != 0 if using integers)

    dotproduct = (c.x - a.x) * (b.x - a.x) + (c.y - a.y)*(b.y - a.y)
    if dotproduct < 0 : return False

    squaredlengthba = (b.x - a.x)*(b.x - a.x) + (b.y - a.y)*(b.y - a.y)
    if dotproduct > squaredlengthba: return False

    return True          
            
def findIntersection(oppositeEdgePoint, edgePoint, possibleIntersectionLines):
    edgeLineEq = LineEquation(oppositeEdgePoint, edgePoint)
    
    for line in possibleIntersectionLines:
        #if (line_line_intersection(oppositeEdgePoint, edgePoint, line[1], line[0])):
        possible = LineEquation(line[1], line[0])
        pt = possible.intersectionWithLine(edgeLineEq)
        if isBetween(line[0], line[1], pt) and isBetween(oppositeEdgePoint, edgePoint, pt):
            return pt
    
    #return oppositeEdgePoint
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    