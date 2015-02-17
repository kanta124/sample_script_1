#-------------------------------------------------------------------------------
# Name:         DLA-3D    
# Purpose:      simulate shape by triangulated pegs
#
# Author:      Kantaro MAKANAE
#
# Created:     08/08/2014
#-------------------------------------------------------------------------------

import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
import Rhino.DocObjects.Tables as rt
import math
import random
import ghpythonlib.components as gh

class Molecule3D():
    
    def __init__(self, pt, angle, len, inputMolList, brep):
        #state
        self.moveState   =  0
        self.baseState   = [0,0,0]
        self.branchState = [0,0,0]
        self.inputMolList = inputMolList
        #pt,etc
        self.pt3d = pt
        self.angle = math.pi*(angle/180)
        self.length = length
        self.zDirection = rg.Vector3d(0,0,1)
        self.yDirection = rg.Vector3d(0,1,0)
        self.plane = rg.Plane(self.pt3d, self.zDirection)
        self.brep = brep
        
        point0Vec = self.yDirection*(length/2)/math.cos(math.pi/6)
        point1Vec = rg.Vector3d(point0Vec)
        point2Vec = rg.Vector3d(point0Vec)
        rg.Vector3d.Rotate(point1Vec, math.pi*2/3, rg.Vector3d.ZAxis)
        rg.Vector3d.Rotate(point2Vec, math.pi*4/3, rg.Vector3d.ZAxis)
        point0 = rg.Point3d.Add(self.pt3d, point0Vec) ###
        point1 = rg.Point3d.Add(self.pt3d, point1Vec) ###
        point2 = rg.Point3d.Add(self.pt3d, point2Vec) ###
        vec0to1 = rg.Vector3d.Subtract(rg.Vector3d(point1), rg.Vector3d(point0))
        vec1to2 = rg.Vector3d.Subtract(rg.Vector3d(point2), rg.Vector3d(point1)) 
        vec2to0 = rg.Vector3d.Subtract(rg.Vector3d(point0), rg.Vector3d(point2))
        upVec = rg.Vector3d(0, 0,length*math.sin(self.angle))
        branchPt0Vec = rg.Vector3d.Add(upVec, vec0to1*math.cos(self.angle))
        branchPt1Vec = rg.Vector3d.Add(upVec, vec1to2*math.cos(self.angle))
        branchPt2Vec = rg.Vector3d.Add(upVec, vec2to0*math.cos(self.angle))
        branchPt0 = rg.Point3d.Add(point0, branchPt0Vec) ###
        branchPt1 = rg.Point3d.Add(point1, branchPt1Vec) ###
        branchPt2 = rg.Point3d.Add(point2, branchPt2Vec) ###
        self.basePtList = [point0, point1, point2]
        self.branchPtList = [branchPt0, branchPt1, branchPt2]
        
        handVec0to1 = rg.Vector3d(vec0to1)*0.33
        handVec1to2 = rg.Vector3d(vec1to2)*0.33
        handVec2to0 = rg.Vector3d(vec2to0)*0.33
        handPt0to1 = rg.Point3d.Add(point0, handVec0to1)
        handPt1to2 = rg.Point3d.Add(point1, handVec1to2)
        handPt2to0 = rg.Point3d.Add(point2, handVec2to0)
        handBPt0Vec = rg.Vector3d.Negate(rg.Vector3d(branchPt0Vec)*0.33)
        handBPt1Vec = rg.Vector3d.Negate(rg.Vector3d(branchPt1Vec)*0.33)
        handBPt2Vec = rg.Vector3d.Negate(rg.Vector3d(branchPt2Vec)*0.33)
        handBPt0 = rg.Point3d.Add(branchPt0, handBPt0Vec)
        handBPt1 = rg.Point3d.Add(branchPt1, handBPt1Vec)
        handBPt2 = rg.Point3d.Add(branchPt2, handBPt2Vec)
        self.handPtList = [handPt0to1, handPt1to2, handPt2to0]
        self.handBPtList = [handBPt0, handBPt1, handBPt2]
        
        #make meshes
        pl0 = rg.Polyline([point0, point1, point2, point0])
        pl1 = rg.Polyline([point0, point1, branchPt0, branchPt2, point0])
        pl2 = rg.Polyline([point1, point2, branchPt1, branchPt0, point1])
        pl3 = rg.Polyline([point2, point0, branchPt2, branchPt1, point2])
        pl4 = rg.Polyline([branchPt0, branchPt1, branchPt2, branchPt0])
        mesh0 = rg.Mesh.CreateFromClosedPolyline(pl0)
        mesh1 = rg.Mesh.CreateFromClosedPolyline(pl1)
        mesh2 = rg.Mesh.CreateFromClosedPolyline(pl2)
        mesh3 = rg.Mesh.CreateFromClosedPolyline(pl3)
        mesh4 = rg.Mesh.CreateFromClosedPolyline(pl4)
        self.mesh = gh.MeshJoin([mesh0, mesh1, mesh2, mesh3, mesh4])
        
        #make lines
        line0to1 = rg.Line(point0,point1)
        line1to2 = rg.Line(point1,point2)
        line2to0 = rg.Line(point2,point0)
        branchLine0  = rg.Line(point0,branchPt0)
        branchLine1  = rg.Line(point1,branchPt1)
        branchLine2  = rg.Line(point2,branchPt2)
        self.lineList = [line0to1,line1to2,line2to0,branchLine0,branchLine1,branchLine2]
        
        
    def move(self):
        #move the pt3d
        xDef = random.uniform(-20, 20)
        yDef = random.uniform(-20, 20)
        zDef = random.uniform(-20, 20)
        self.pt3dNext = rg.Point3d(self.pt3d.X+xDef, self.pt3d.Y+yDef, self.pt3d.Z+zDef)
        
        #here should be boundary check
        jInside = gh.PointInBrep(self.brep, self.pt3dNext, True)
        if jInside == True:
            self.pt3d = self.pt3dNext
            
        rotAngZ = math.pi*2*(random.uniform(0,360)/360)
        newPlane =  rg.Plane(self.pt3d, self.zDirection)
        newPlane = gh.RotatePlane(newPlane, rotAngZ)
        newPtList = gh.Orient(self.basePtList, self.plane, newPlane).geometry
        newbPtList = gh.Orient(self.branchPtList, self.plane, newPlane).geometry
        newhandPtList = gh.Orient(self.handPtList, self.plane, newPlane).geometry
        newhandBPtList = gh.Orient(self.handBPtList, self.plane, newPlane).geometry
        newMesh = gh.Orient(self.mesh, self.plane, newPlane).geometry
        newLineList = gh.Orient(self.lineList, self.plane, newPlane).geometry
        
        self.plane = newPlane
        self.basePtList = newPtList
        self.branchPtList = newbPtList
        self.handPtList = newhandPtList
        self.handBPtList = newhandBPtList
        self.mesh = newMesh
        self.lineList = newLineList

    def moveBaToBr(self, i, fromID, toID, inputList):
        #make plane
        newPlane = rg.Plane(self.inputMolList[i].branchPtList[toID], self.inputMolList[i].handBPtList[toID], self.inputMolList[i].handPtList[toID])
        basePlane = rg.Plane(self.handPtList[fromID], self.basePtList[fromID], self.handBPtList[fromID])
        axisPlane = rg.Plane(self.handPtList[fromID], rg.Vector3d.Subtract(rg.Vector3d(self.basePtList[fromID]), rg.Vector3d(self.handPtList[fromID])))
        basePlane = gh.Rotate(basePlane, math.pi, axisPlane).geometry
        #orient geoms
        nPlane = gh.Orient(self.plane, basePlane, newPlane).geometry
        nBasePtList = gh.Orient(self.basePtList, basePlane, newPlane).geometry
        nBranchPtList = gh.Orient(self.branchPtList, basePlane, newPlane).geometry
        nHandPtList = gh.Orient(self.handPtList, basePlane, newPlane).geometry
        nHandBPtList = gh.Orient(self.handBPtList, basePlane, newPlane).geometry
        nMesh = gh.Orient(self.mesh, basePlane, newPlane).geometry
        nLineList = gh.Orient(self.lineList, basePlane, newPlane).geometry
        
        boolInt = False
        for j in range(len(inputList)):
            iList = rg.Intersect.Intersection.MeshMeshFast(self.mesh, inputList[j].mesh)
            if len(iList) >= 1:
                boolInt = True
                break
        
        if boolInt == False:
            #change state
            self.moveState = 1
            self.baseState[fromID] = 1
            self.inputMolList[i].branchState[toID] = 1
            
            #change position
            self.plane = nPlane
            self.basePtList = nBasePtList
            self.branchPtList = nBranchPtList
            self.handPtList = nHandPtList 
            self.handBPtList = nHandBPtList
            self.mesh = nMesh
            self.lineList = nLineList
        else: pass
            
        
    def moveBrToBa(self, i, fromID, toID, inputList):
        #make plane
        newPlane = rg.Plane(self.inputMolList[i].handPtList[toID], self.inputMolList[i].basePtList[toID], self.inputMolList[i].handBPtList[toID])
        basePlane = rg.Plane(self.branchPtList[fromID], self.handBPtList[fromID], self.handPtList[fromID])
        axisPlane = rg.Plane(self.branchPtList[fromID], rg.Vector3d.Subtract(rg.Vector3d(self.handBPtList[fromID]), rg.Vector3d(self.branchPtList[fromID])))
        basePlane = gh.Rotate(basePlane, math.pi, axisPlane).geometry
        #orient geoms
        nPlane = gh.Orient(self.plane, basePlane, newPlane).geometry
        nBasePtList = gh.Orient(self.basePtList, basePlane, newPlane).geometry
        nBranchPtList = gh.Orient(self.branchPtList, basePlane, newPlane).geometry
        nHandPtList = gh.Orient(self.handPtList, basePlane, newPlane).geometry
        nHandBPtList = gh.Orient(self.handBPtList, basePlane, newPlane).geometry
        nMesh = gh.Orient(self.mesh, basePlane, newPlane).geometry
        nLineList = gh.Orient(self.lineList, basePlane, newPlane).geometry
        
        boolInt = False
        for j in range(len(inputList)):
            iList = rg.Intersect.Intersection.MeshMeshFast(self.mesh, inputList[j].mesh)
            if len(iList) >= 1:
                boolInt = True
                break
        
        if boolInt == False:
            #change state
            self.moveState = 1
            self.baseState[fromID] = 1
            self.inputMolList[i].branchState[toID] = 1
            
            #change position
            self.plane = nPlane
            self.basePtList = nBasePtList
            self.branchPtList = nBranchPtList
            self.handPtList = nHandPtList 
            self.handBPtList = nHandBPtList
            self.mesh = nMesh
            self.lineList = nLineList
        else: pass
        
    def checkAndMove(self):
        for i in range(len(self.inputMolList)):
            distPtToPt = rg.Point3d.DistanceTo(self.pt3d, self.inputMolList[i].pt3d)
            if distPtToPt <= self.length*2/math.sqrt(3) + 1:
                distBa0ToBr0 = rg.Point3d.DistanceTo(self.basePtList[0], self.inputMolList[i].branchPtList[0])
                distBa0ToBr1 = rg.Point3d.DistanceTo(self.basePtList[0], self.inputMolList[i].branchPtList[1])
                distBa0ToBr2 = rg.Point3d.DistanceTo(self.basePtList[0], self.inputMolList[i].branchPtList[2])
                distBa1ToBr0 = rg.Point3d.DistanceTo(self.basePtList[1], self.inputMolList[i].branchPtList[0])
                distBa1ToBr1 = rg.Point3d.DistanceTo(self.basePtList[1], self.inputMolList[i].branchPtList[1])
                distBa1ToBr2 = rg.Point3d.DistanceTo(self.basePtList[1], self.inputMolList[i].branchPtList[2])
                distBa2ToBr0 = rg.Point3d.DistanceTo(self.basePtList[2], self.inputMolList[i].branchPtList[0])
                distBa2ToBr1 = rg.Point3d.DistanceTo(self.basePtList[2], self.inputMolList[i].branchPtList[1])
                distBa2ToBr2 = rg.Point3d.DistanceTo(self.basePtList[2], self.inputMolList[i].branchPtList[2])
                
                distBr0ToBa0 = rg.Point3d.DistanceTo(self.branchPtList[0], self.inputMolList[i].basePtList[0])
                distBr0ToBa1 = rg.Point3d.DistanceTo(self.branchPtList[0], self.inputMolList[i].basePtList[1])
                distBr0ToBa2 = rg.Point3d.DistanceTo(self.branchPtList[0], self.inputMolList[i].basePtList[2])
                distBr1ToBa0 = rg.Point3d.DistanceTo(self.branchPtList[1], self.inputMolList[i].basePtList[0])
                distBr1ToBa1 = rg.Point3d.DistanceTo(self.branchPtList[1], self.inputMolList[i].basePtList[1])
                distBr1ToBa2 = rg.Point3d.DistanceTo(self.branchPtList[1], self.inputMolList[i].basePtList[2])
                distBr2ToBa0 = rg.Point3d.DistanceTo(self.branchPtList[2], self.inputMolList[i].basePtList[0])
                distBr2ToBa1 = rg.Point3d.DistanceTo(self.branchPtList[2], self.inputMolList[i].basePtList[1])
                distBr2ToBa2 = rg.Point3d.DistanceTo(self.branchPtList[2], self.inputMolList[i].basePtList[2])
                
                ###from base to branch
                if   distBa0ToBr0 <= 20 and self.inputMolList[i].branchState[0] == 0:
                    self.moveBaToBr(i,0,0,self.inputMolList)
                    break
                elif distBa0ToBr1 <= 20 and self.inputMolList[i].branchState[1] == 0:
                    self.moveBaToBr(i,0,1,self.inputMolList)
                    break
                elif distBa0ToBr2 <= 20 and self.inputMolList[i].branchState[2] == 0:
                    self.moveBaToBr(i,0,2,self.inputMolList)
                    break
                elif distBa1ToBr0 <= 20 and self.inputMolList[i].branchState[0] == 0:
                    self.moveBaToBr(i,1,0,self.inputMolList)
                    break
                elif distBa1ToBr1 <= 20 and self.inputMolList[i].branchState[1] == 0:
                    self.moveBaToBr(i,1,1,self.inputMolList)
                    break
                elif distBa1ToBr2 <= 20 and self.inputMolList[i].branchState[2] == 0:
                    self.moveBaToBr(i,1,2,self.inputMolList)
                    break
                elif distBa2ToBr0 <= 20 and self.inputMolList[i].branchState[0] == 0:
                    self.moveBaToBr(i,2,0,self.inputMolList)
                    break
                elif distBa2ToBr1 <= 20 and self.inputMolList[i].branchState[1] == 0:
                    self.moveBaToBr(i,2,1,self.inputMolList)
                    break
                elif distBa2ToBr2 <= 20 and self.inputMolList[i].branchState[2] == 0:
                    self.moveBaToBr(i,2,2,self.inputMolList)
                    break
                    
                ###from branch to base
                elif distBr0ToBa0 <= 20 and self.inputMolList[i].baseState[0] == 0:
                    self.moveBrToBa(i,0,0,self.inputMolList)
                    break
                elif distBr0ToBa1 <= 20 and self.inputMolList[i].baseState[1] == 0:
                    self.moveBrToBa(i,0,1,self.inputMolList)
                    break
                elif distBr0ToBa2 <= 20 and self.inputMolList[i].baseState[2] == 0:
                    self.moveBrToBa(i,0,2,self.inputMolList)
                    break
                elif distBr1ToBa0 <= 20 and self.inputMolList[i].baseState[0] == 0:
                    self.moveBrToBa(i,1,0,self.inputMolList)
                    break
                elif distBr1ToBa1 <= 20 and self.inputMolList[i].baseState[1] == 0:
                    self.moveBrToBa(i,1,1,self.inputMolList)
                    break
                elif distBr1ToBa2 <= 20 and self.inputMolList[i].baseState[2] == 0:
                    self.moveBrToBa(i,1,2,self.inputMolList)
                    break
                elif distBr2ToBa0 <= 20 and self.inputMolList[i].baseState[0] == 0:
                    self.moveBrToBa(i,2,0,self.inputMolList)
                    break
                elif distBr2ToBa1 <= 20 and self.inputMolList[i].baseState[1] == 0:
                    self.moveBrToBa(i,2,1,self.inputMolList)
                    break
                elif distBr2ToBa2 <= 20 and self.inputMolList[i].baseState[2] == 0:
                    self.moveBrToBa(i,2,2,self.inputMolList)
                    break
            else: pass
            
    def proc(self):
        if self.moveState == 0:
            self.move()
            self.checkAndMove()


class DLA3D():
    
    def __init__(self, brep, num, angle, length):
        self.moveMolList = []
        self.fixedMolList = []
        self.brep = brep
        self.ptNum = num
        self.angle = angle
        self.len = length
        
    def initialState(self, lines):
        #make seedpoint
        for i in range(len(lines)):
            sPt = rg.Line.PointAt(lines[i], 0)
            ePt = rg.Line.PointAt(lines[i], 1)
            iniMol = Molecule3D(sPt, self.angle, self.len, [], self.brep)
            iniMol.moveState = 1
            iniMol.baseState = [1,1,1]
            self.fixedMolList.append(iniMol)
        
        #make pointcloud in the frame
        bbox = rg.Brep.GetBoundingBox(self.brep, rg.Plane.WorldXY)
        edgeList = rg.BoundingBox.GetEdges(bbox)
        numb = 0
        while numb <= self.ptNum:
            random.seed()
            x = random.randint(int(edgeList[0].FromX), int(edgeList[0].ToX))
            y = random.randint(int(edgeList[1].FromY), int(edgeList[1].ToY))
            z = random.randint(int(edgeList[8].FromZ), int(edgeList[8].ToZ))
            pt = rg.Point3d(x,y,z)
            ptin = gh.PointInBrep(self.brep, pt, True)
            if ptin == True:
                mol = Molecule3D(pt, self.angle, self.len, [], self.brep)
                self.moveMolList.append(mol)
                numb += 1
            
        for i in range(self.ptNum):
            self.moveMolList[i].inputMolList = self.fixedMolList
    
    def procDLA(self):
        newFixedMolList = []
        
        for i in range(len(self.moveMolList)):
            self.moveMolList[i].proc()
            if self.moveMolList[i].moveState == 1:
                self.fixedMolList.append(self.moveMolList[i])
                newFixedMolList.append(self.moveMolList[i])
        
        for j in newFixedMolList:
            self.moveMolList.remove(j)
        
        #update each inputMolList
        for i in range(len(self.moveMolList)):
            self.moveMolList[i].inputMolList = self.fixedMolList
        

if reset == False:
    dla1 = DLA3D(brep, num, angle, length)
    dla1.initialState(seeds)

a = dla1