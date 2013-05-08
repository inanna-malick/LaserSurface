'''
Created on Aug 15, 2012

@author: kinsp1
'''
from geometry import constants
from geometry.constants import dimensions
from geometry.lcAlgObjReader import lcAlgObjReader
import os
import shutil
import sys
import time

if __name__ == '__main__':
    
    srcObjName = "diamond"
    
    print("BEGIN")
    
    objReader = lcAlgObjReader(srcObjName, dimensions.scale)
    objReader.readFile(open(os.path.join(os.pardir, "input/" + srcObjName + ".obj"), 'r'))
    
    
    '''TODO: MAYBE: for edges with nothing connected, give them a constant predefined edge normal, ie windowpane
    '''
    
    objReader.generateThreeDee()
    
    #output folder is target + time
    now = time.strftime("%d %b %Y %H.%M.%S")
    directory = os.path.join(os.pardir, "output/", srcObjName, now)
    
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    
    objReader.outputThreeDee(directory)
    objReader.outputTwoDee(directory)
    

    #copy constants module to output dir, store exact settings used for this run.
    constants_src = os.path.abspath(sys.modules[constants.__name__].__file__)
    shutil.copyfileobj(open(constants_src, 'r'), open(os.path.join(directory, "constants.py"), 'w'))
            
    print("DONE")
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
