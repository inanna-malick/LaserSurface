

from geometry.Point import Point

def log(message, prefix="Debug", hush=True):
    if not hush:
        print("%s : %s " % (prefix, message))



class objBuilder():

    def __init__(self):
        # tuples of floats
        self.vertexList = []
        # tuples of integer (reference into vertexList table)
        self.faceList = []
        
        
    # add a vertex. round to 10 digits, if it exists already use existing
    # return index of vertex for face use (1 based)
    def addVertex(self, v):
        rounded_v = Point(round(v.x, 10), round(v.y, 10), round(v.z, 10))
        
        try:
            # 1 based index 
            return self.vertexList.index(rounded_v) + 1
        except ValueError:
            #not in list, so add it
            self.vertexList.append(v)
            #position of new vertexList in 1-based list
            return len(self.vertexList)


    # add a face as a tuple of integers
    def addFace(self, f):
        
        #TODO(?): disallow duplicate faces
        self.faceList.append(f)
        
        
    def buildFace(self, f):
        #indexes (use i prefix when possible?)
        
        indices = []
        
        for v in f:
            indices.append(self.addVertex(v))
        
        self.addFace( tuple(indices) )
        
        
    def getDataDict(self):
        return dict(vertexList=self.vertexList, faceList=self.faceList)
        
        

 
    def writeData(self, filename="test"):
        dataDict = self.getDataDict()
        outString = "\ng default\n"
        
        # get (x, y, z) from vertices
        for i in dataDict["vertexList"]:
            log(str(i))
            outString += "v %f %f %f \n" % (i.x, i.y, i.z)
            
        '''texture vertices: not needed
        for i in dataDict["vt"]:
            log(str(i))
            outString+= "vt %faceList %faceList \n" % (i[0][0],i[0][1])
        
        
        optional for face definition, nice to have
        #vertex normals as (x, y, z)
        for i in dataDict["vn"]:
            log(str(i))
            outString+= "vn %faceList %faceList %faceList \n" % (i[0],i[1],i[2])
        outString += "g %s\n" % dataDict["g"]
        
        # face normals as string: 
        faceList  v1/vt1/vn1   v2/vt2/vn2   v3/vt3/vn3 . . .
    
        Polygonal geometry statement.
    
        Specifies a face element and its vertex reference number. You can
        optionally include the texture vertex and vertex normal reference
        numbers.
    
        The reference numbers for the vertices, texture vertices, and
        vertex normals must be separated by slashes (/). There is no space
        between the number and the slash.
    
        vertexList is the reference number for a vertex in the face element. A
        minimum of three vertices are required.
    
        vt is an optional argument.
    
        vt is the reference number for a texture vertex in the face
        element. It always follows the first slash.
    
        vn is an optional argument.
    
        vn is the reference number for a vertex normal in the face element.
        It must always follow the second slash.
        '''
        for i in dataDict["faceList"]:
            log(str(i))
            outString += "f"
            for v in i:
                outString += " {}".format(v) 
            outString += "\n"
            
        outString += "\n"
        log(outString)

        fileLocation = filename + ".obj"
        f = open(fileLocation, 'w')
        
        f.writelines(outString)
        f.close()
         
