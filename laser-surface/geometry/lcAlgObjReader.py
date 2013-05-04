'''
Created on Aug 15, 2012

@author: kinsp1
'''
import os


from geometry.objReader import OBJReader
from geometry.Face import Face
from geometry.ObjVertex import ObjVertex, buildVerts
from geometry.objExport import objBuilder
from geometry.TwoDeeFace import TwoDeeFace
from geometry import sdxf
from planar import Point
import geometry

class lcAlgObjReader(OBJReader):

    def __init__(self, srcObjName, scale=1.0):
        OBJReader.__init__(self)
        self.scale = scale
        self.vertices = []
        self.faces = []
        self.knownEdges = []
        
        self.srcObjName = srcObjName

        
        
    def readFile(self, sourceFile):
        print("Reading " + self.srcObjName + ".obj...")
        self.begin()
        self.read(sourceFile)   
        self.end()  
        sourceFile.close()
        


    def generateThreeDee(self):
        '''
        #hack to force normal for unconnected edges:
        for face in self.faces:
            for edge in face.edges:
                if edge.otherEdge == None:
                    print(type(edge.baseEdge.sharedEdgeNormal))
                    edge.baseEdge.sharedEdgeNormal = geometry.Point.Point(-1, 0, 0).normalized()
                    print(type(edge.baseEdge.sharedEdgeNormal))
        '''
        
        
        print("Calculating points...")
        for face in self.faces:
            face.calculatePlanes()
            face.calculatePoints3D()
            
        for vertex in self.vertices:
            vertex.buildEdgeViews()
            
        
        '''
        changeMade = True
        while changeMade:
            changeMade = False
            for vertex in self.vertices:
                changeLocal = vertex.doPriorityPushback()
                changeMade = changeMade or changeLocal        
        '''
        
        # give each vertex cluster a chance to make changes until none do
        changeMade = True
        while changeMade:
            changeMade = False
            for vertex in self.vertices:
                # FIXME: will break, changes are checked against prev state then all run, can go over defined limits
                changeLocal = vertex.doPushBackRound()
                changeMade = changeMade or changeLocal
                
        print("Done calculating points")
                    
    def faceList(self, *verts):        
        if len(verts) != 3:
            raise Exception("error: face with " + str(len(verts)) + " sides")
        
        vertA = self.vertices[verts[0][0] - 1]
        vertB = self.vertices[verts[1][0] - 1]
        vertC = self.vertices[verts[2][0] - 1]
        
        faceToAdd = Face(vertA, vertB, vertC, self.knownEdges, str(len(self.faces) + 1))
        
        vertA.faces.append(faceToAdd)
        vertB.faces.append(faceToAdd)
        vertC.faces.append(faceToAdd)
        
        self.faces.append(faceToAdd)
        
    def handle_v(self, x, y, z, w=1):
        self.v_count += 1
        self.vertexList(ObjVertex(float(x), float(y), float(z), index=self.v_count - 1))
        
    def vertexList(self, vert):
        vert.scale(self.scale)
        self.vertices.append(vert)
    

    def outputThreeDee(self, directory):
        print("Building 3D output...")
        builder = objBuilder()
        for face in self.faces:
            face.buildObj(builder)
            
            
        builder.writeData(os.path.join(directory, "visualization"))
    
        
        
    def outputTwoDee(self, directory):
        print("Building 2D output...")
        edgeSetList = []
        for face in self.faces:
            toDraw = TwoDeeFace(face)
            edgeSetList.append(toDraw)
            
        maxX = -9999
        maxY = -9999
        maxZ = -9999
        
        minX = 9999
        minY = 9999
        minZ = 9999
        for face in self.faces:
            maxX = max(maxX, face.maxX)
            maxY = max(maxY, face.maxY)
            maxZ = max(maxZ, face.maxZ)
            
            minX = min(minX, face.minX)
            minY = min(minY, face.minY)
            minZ = min(minZ, face.minZ)          
            
        d = sdxf.Drawing()
        c = 0
        # add each triangle to a single dxf at intervals
        for e in edgeSetList:
            e.offset = Point(c, 0)
            e.printToDrawing(d)
            c = c + e.width + 5
        
        # TODO: draw annotated lines for final x, y, z
        d.append(sdxf.Line(points=[(minX, 30, 0), (maxX , 30, 0)]))
        d.append(sdxf.Line(points=[(minY, 35, 0), (maxY , 35, 0)]))
        d.append(sdxf.Line(points=[(minZ, 40, 0), (maxZ , 40, 0)]))
        
        
        buildVerts(self.vertices, directory)

            
        d.saveas(os.path.join(directory, "faces"))
        
    
