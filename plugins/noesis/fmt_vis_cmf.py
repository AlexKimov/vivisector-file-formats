from inc_noesis import *
import os
import noewin
import noewinext

SECTION_HEADER_SHORT = 0
SECTION_HEADER_LONG = 1 


def registerNoesisTypes():
    handle = noesis.register( \
        "Vivisector (2005) model", ".cmf")
    
    noesis.setHandlerTypeCheck(handle, visModelCheckType)
    noesis.setHandlerLoadModel(handle, visModelLoadModel)
        
    return 1 

# types
TYPE_UNKNOWN_1 = 1
TYPE_TEXTURE_NUMBER_SECTION = 2
TYPE_TEXTURE_LIST_SECTION = 3
TYPE_UNKNOWN_8192 = 8192

TYPE_FACE_NUMBER_SECTION = 8209
TYPE_VERTEX_NUMBER_SECTION = 8210

TYPE_FACE_INDEXES = 8211

TYPE_UNKNOWN_INDEXES_8215 = 8215
TYPE_UNKNOWN_INDEXES_8218 = 8218

TYPE_TEXTURE_INDEXES = 8220

TYPE_UNKNOWN_INDEXES_8221 = 8221

TYPE_VERTEXES_UV = 8224
TYPE_VERTEXES_UV2 = 8225
TYPE_VERTEXES = 8227

TYPE_UNKNOWN_NUMBER_8240 = 8240
TYPE_UNKNOWN_INDEXES_8241 = 8241
TYPE_UNKNOWN_INDEXES_8242 = 8242
TYPE_UNKNOWN_COORDINATES_8243 = 8243
TYPE_UNKNOWN_INDEXES_8244 = 8244
TYPE_UNKNOWN_12288 = 12288
TYPE_UNKNOWN_61441 = 61441
TYPE_OBJECT_NUMBER = 61456
TYPE_BONE_LIST = 61457
TYPE_UNKNOWN_COORDINATES_61458 = 61458
TYPE_UNKNOWN_INDEXES_61459 = 61459
TYPE_UNKNOWN_INDEXES_61460 = 61460
TYPE_MATRIXES = 61461
TYPE_UNKNOWN_INDEXES_61473 = 61473 
TYPE_UNKNOWN_INDEXES_61474 = 61474 
TYPE_UNKNOWN_INDEXES_61475 = 61475 
TYPE_UNKNOWN_INDEXES_61476 = 61476 
TYPE_UNKNOWN_INDEXES_61488 = 61488 
TYPE_UNKNOWN_INDEXES_61489 = 61489 

# consts
TEXTURE_NAME_LENGTH = 128
BONE_NAME_LENGTH = 32 

#
VERTEX_ONE_ATTRIBUTE = 1001
VERTEX_ALL_ATTRIBUTES = 1002


class Vector2F:
    def __init__(self, x=0, y=0):    
        self.x = x
        self.y = y
        
    def getStorage(self):
        return (self.x, self.y)        
        
        
class Vector3F:
    def __init__(self):    
        self.x = 0
        self.y = 0
        self.z = 0
        
    def read(self, reader):
        self.x, self.y, self.z = noeUnpack('3f', reader.readBytes(12))  
        
    def getStorage(self):
        return (self.x, self.y, self.z) 


class Vector4U16:
    def __init__(self):    
        self.i1 = 0
        self.i2 = 0
        self.i3 = 0     
        self.i4 = 0
        
    def read(self, reader):
        self.i1, self.i2, self.i3, self.i4 = noeUnpack('4H', reader.readBytes(8))   
        
    def getStorage(self):
        return (self.i1, self.i2, self.i3, self.i4) 
       
       
class Vector4U:
    def __init__(self):    
        self.i1 = 0
        self.i2 = 0
        self.i3 = 0     
        self.i4 = 0
        
    def read(self, reader):
        self.i1, self.i2, self.i3, self.i4 = noeUnpack('4I', reader.readBytes(16))
        
    def getStorage(self):
        return (self.i1, self.i2, self.i3, self.i4)         


class VISUV:
    def __init__(self):
        self.uv = None
        self.data = None
        
    def read(self, reader):
        self.data = noeUnpack('2f2f2f2f', reader.readBytes(32))
        self.uv = [Vector2F(self.data[i], self.data[4 + i]) for i in range(4)]         


class VISModel:
    def __init__(self, reader):
        self.reader = reader    
        self.textureCount = 0
        self.textureList = []
        self.boneList = []        
        self.indexes = [] # 8218
        self.indexes2 = [] # 8211
        self.indexes3 = [] # 8220       
        self.indexes3 = [] # 8221
        self.vertexes = []
        self.vertexAttributes = []        
        self.matrixes = [] 
        self.bonePositions = []
        self.boneIndexes = [] 
        self.vertexBoneIndexes = []        
        self.textureIndexes = None 
        self.boneCount = 0
        self.objCount = 0
        self.vertCount = 0
        self.faceCount = 0
        self.unknCount = 0
        
    def readHeader(self, reader): 
        magic = reader.readBytes(4).decode('ascii') # UFBC
        reader.seek(4, NOESEEK_REL)
        
    def readTextureList(self, reader):
        for i in range(self.textureCount):
            name = noeAsciiFromBytes(reader.readBytes(TEXTURE_NAME_LENGTH).split(b"\0", 1)[0])
            
            self.textureList.append(name.split(".")[0])       

    def readIndexesToArray(self, reader):    
        indexArray = []    
        indexArray.extend(noeUnpack('{}I'.format(self.faceCount), reader.readBytes(4 * self.faceCount)))
        
        return indexArray

    def readUnknownIndexes(self, reader):
        for i in range(self.faceCount):    
            faceIndexes = Vector4U()
            faceIndexes.read(reader)
            
            self.indexes.append(faceIndexes) 
          
    def readUnknownIndexes2(self, reader): 
        reader.seek(8 * self.unknCount, NOESEEK_REL)
        
    def readCordinates(self, reader): 
        reader.seek(16 * self.unknCount, NOESEEK_REL)
       
    def readUnknownCoordinates(self, reader, count): 
        reader.seek(12 * count, NOESEEK_REL)      
     
    def readVertexes(self, reader): 
        for i in range(self.vertexCount): 
            vertex = Vector3F()
            vertex.read(reader)
            
            self.vertexes.append(vertex)    

    def readBonesPositions(self, reader): 
        for i in range(self.objCount): 
            position = Vector3F()
            position.read(reader)
            
            self.bonePositions.append(position)  

    def readVertexBoneIndexes(self, reader):  
        self.vertexBoneIndexes = noeUnpack('{}H'.format(self.vertexCount), reader.readBytes(2 * self.vertexCount))             
            
    def readBonesIndexes(self, reader): 
        self.boneIndexes = noeUnpack('{}h'.format(self.objCount), reader.readBytes(2 * self.objCount))            
            
    def readVertexUV(self, reader): 
        for i in range(self.faceCount): 
            vertUV = VISUV()
            vertUV.read(reader)
            
            self.vertexAttributes.append(vertUV)        
 
    def readBoneNameList(self, reader):  
        for i in range(self.objCount):
            name = noeAsciiFromBytes(reader.readBytes(BONE_NAME_LENGTH).split(b"\0", 1)[0])
            self.boneList.append(name) 
    
    def readMatrixes(self, reader):
        #for i in range(self.objCount):
        reader.seek(36 * self.objCount, NOESEEK_REL)   
            
    def readChunk(self, reader):    
        type = reader.readUInt()
        size = reader.readUInt() 
        
        if type == TYPE_UNKNOWN_1: #1
            pass # ??
        elif type == TYPE_TEXTURE_NUMBER_SECTION: #2
            self.textureCount = reader.readUInt()
            
        elif type == TYPE_TEXTURE_LIST_SECTION: #3          
            self.readTextureList(reader)
            
        elif type == TYPE_UNKNOWN_8192:
            pass # ??
            
        elif type == TYPE_FACE_NUMBER_SECTION:
            self.faceCount = reader.readUInt()
        elif type == TYPE_VERTEX_NUMBER_SECTION:
            self.vertexCount = reader.readUInt()
            
        elif type == TYPE_FACE_INDEXES:
            self.readUnknownIndexes(reader)             
           
        elif type == TYPE_UNKNOWN_INDEXES_8215:
            self.readIndexesToArray(reader)                
        elif type == TYPE_UNKNOWN_INDEXES_8218:
            self.readIndexesToArray(reader)    
     
        elif type == TYPE_TEXTURE_INDEXES:
            self.textureIndexes = self.readIndexesToArray(reader)  
            
        elif type == TYPE_UNKNOWN_INDEXES_8221:
            self.readIndexesToArray(reader)  

        elif type == TYPE_VERTEXES_UV:
            self.readVertexUV(reader)           
        elif type == TYPE_VERTEXES_UV2:      
            self.readVertexUV(reader)
             
        elif type == TYPE_VERTEXES: 
            self.readVertexes(reader) 
            
 
        elif type == TYPE_UNKNOWN_NUMBER_8240: 
            self.unknCount = reader.readUInt()
        elif type == TYPE_UNKNOWN_INDEXES_8241:        
            self.readUnknownIndexes2(reader)            
              
        elif type == TYPE_UNKNOWN_INDEXES_8242: 
            self.readUnknownIndexes2(reader)            
            
        elif type == TYPE_UNKNOWN_COORDINATES_8243: 
            self.readUnknownCoordinates(reader, self.unknCount)           
            
        elif type == TYPE_UNKNOWN_INDEXES_8244: 
            reader.seek(16 * self.faceCount, NOESEEK_REL)                 
            
        elif type == TYPE_UNKNOWN_12288:         
            pass # ??
        elif type == TYPE_UNKNOWN_61441: 
            reader.seek(44, NOESEEK_REL)           
        elif type == TYPE_OBJECT_NUMBER: 
            self.objCount = reader.readUInt()   
            
        elif type == TYPE_BONE_LIST:        
            self.readBoneNameList(reader)             
        elif type == TYPE_UNKNOWN_COORDINATES_61458:  
            self.readBonesPositions(reader)
            
        elif type == TYPE_UNKNOWN_INDEXES_61459: 
            reader.seek(2 * self.objCount, NOESEEK_REL)              

        elif type == TYPE_UNKNOWN_INDEXES_61460: 
            self.readBonesIndexes(reader)    
            
        elif type == TYPE_MATRIXES: 
            self.readMatrixes(reader)           
        elif type == TYPE_UNKNOWN_INDEXES_61473: 
            reader.seek(4 * self.faceCount, NOESEEK_REL)   
          
        elif type == TYPE_UNKNOWN_INDEXES_61474:
            reader.seek(self.faceCount, NOESEEK_REL)     
            
        elif type == TYPE_UNKNOWN_INDEXES_61475:
            reader.seek(2 * self.faceCount, NOESEEK_REL)        
        elif type == TYPE_UNKNOWN_INDEXES_61476:
            reader.seek(size, NOESEEK_REL)        

        elif type == TYPE_UNKNOWN_INDEXES_61488:         
            self.readVertexBoneIndexes(reader)
            
        elif type == TYPE_UNKNOWN_INDEXES_61489:
            reader.seek(2 * self.vertexCount, NOESEEK_REL)                   
        
    def readChunks(self, reader):
        while not reader.checkEOF():
            self.readChunk(reader)          
            
    def read(self):
        self.readHeader(self.reader)
        self.readChunks(self.reader)        
    
    
def visModelCheckType(data):

    return 1     
    
    
def visModelLoadModel(data, mdlList):
    #noesis.logPopup()
    
    model = VISModel(NoeBitStream(data))
    model.read()
    
    ctx = rapi.rpgCreateContext()    
    
    transMatrix = NoeMat43( ((1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 0, 0)) ) 
    rapi.rpgSetTransform(transMatrix)       
    
    materials = []
    textures = []
    
    dataPath = 'F:/Games/Vivisector - Beast Within/DATA/'
    
    for name in model.textureList:
        textures.append(rapi.loadExternalTex(dataPath + name + ".dds"))
        print(dataPath + name + ".dds")
        material = NoeMaterial(name, dataPath + name + ".dds")
        material.setFlags(noesis.NMATFLAG_TWOSIDED, 0)
        materials.append(material)
    
    #rapi.rpgSetName("obj")

    index0 = 0
    index1 = 0    
    for face in model.indexes:
        rapi.rpgSetMaterial(model.textureList[model.textureIndexes[index0]])
        rapi.immBegin(noesis.RPGEO_QUAD)
        
        for vIndex in face.getStorage():          
            rapi.immUV2(model.vertexAttributes[index0].uv[index1].getStorage()) 
            rapi.immBoneIndex([model.vertexBoneIndexes[vIndex]])
            rapi.immBoneWeight([1])             
            rapi.immVertex3(model.vertexes[vIndex].getStorage()) 
            
            index1 += 1    
            
        rapi.immEnd()
        
        index1 = 0
        index0 += 1 

    # show skeleton
    bones = []
    for i in range(model.objCount):
        boneName = model.boneList[i] 
      
        parentBoneName = model.boneList[model.boneIndexes[i]] if model.boneIndexes[i] >= 0 else ""
        
        matrix = NoeMat43().translate(model.bonePositions[i].getStorage())
   
        if parentBoneName != "":
            parentMat = NoeMat43().translate(model.bonePositions[model.boneIndexes[i]].getStorage())
            boneMat = matrix * parentMat
        else:         
            boneMat = matrix
   
        bones.append(NoeBone(i, boneName, boneMat, parentBoneName))           
       
    mdl = rapi.rpgConstructModelSlim()
    mdl.setBones(bones)     
    mdl.setModelMaterials(NoeModelMaterials(textures, materials)) 
    mdlList.append(mdl)    
    
    return 1