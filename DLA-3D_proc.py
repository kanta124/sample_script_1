#-------------------------------------------------------------------------------
# Name:        DLA-3D proc
# Purpose:     simulate shape by triangulated pegs
#
# Author:      Kantaro MAKANAE
#
# Created:     08/08/2014
#-------------------------------------------------------------------------------

import rhinoscriptsyntax as rs
import Rhino.Geometry as rh
import ghpythonlib.components as gh
import Rhino.DocObjects.Tables as rt
import math
import random

moveLList = []
fixedLList = []
#dataTree = DataTree[object]()
meshList = []

dla1.procDLA()

for i in range(len(dla1.moveMolList)):
    moveLList.extend(dla1.moveMolList[i].lineList)
    meshList.append(dla1.moveMolList[i].mesh)

for j in range(len(dla1.fixedMolList)):
    fixedLList.append(dla1.fixedMolList[j].lineList)
    meshList.append(dla1.fixedMolList[j].mesh)


movingUnit = moveLList
fixedUnit = fixedLList
meshes = meshList