import rhinoscriptsyntax as rs
import random as r
import math as m

class tile:
    def __init__(self,VERTICIES,THICKNESS,HEIGHT,BASEHEIGHT):
        self.vert = VERTICIES
        self.thickness = THICKNESS
        self.x = rs.VectorCreate(self.vert[1],self.vert[0])
        self.y = rs.VectorCreate(self.vert[3],self.vert[0])
        self.z = [0,0,HEIGHT]
        self.base = [0,0,BASEHEIGHT]
    def gen(self):
        pts = []
        newPts = []
        faces = []
        for i in range(len(self.vert)):
            pts.append(rs.PointAdd(self.vert[i],self.base))
        pts.append(rs.PointAdd(self.vert[0],self.base))
        cnt = self.cntPt()
        for i in range(len(self.vert)):
            vec = rs.VectorUnitize(rs.VectorCreate(cnt,self.vert[i]))
            vec = vec*self.thickness
            vec = rs.VectorAdd(vec,self.z)
            newPts.append(rs.PointAdd(self.vert[i],vec))
        newPts.append(newPts[0])
        pts.extend(newPts)
        for i in range(len(self.vert)):
            if i<len(self.vert)-1:
                faces.append([i,i+5,i+6,i+1])
            else:
                faces.append([i,i+5,5,0])
        faces.append([0,1,2,3])
        faces.append([5,6,7,8])
        profile = rs.AddMesh(pts,faces)
        return profile
    def subDiv(self):
        rs.CurrentLayer("structured")
        divTiles = []
        cnt = self.cntPt()
        startPtX = rs.PointAdd(self.vert[0],self.x/2)
        startPtY = rs.PointAdd(self.vert[0],self.y/2)
        endPtX = rs.PointAdd(self.vert[2],-self.x/2)
        endPtY = rs.PointAdd(self.vert[2],-self.y/2)
        pts = [startPtX,startPtY,endPtX,endPtY]
        pts.extend(self.vert)
        for i in range(len(pts)):
            vec = rs.VectorUnitize(rs.VectorCreate(cnt,pts[i]))
            pts[i] = rs.PointAdd(pts[i],self.thickness*vec)
        divTiles.append(tile([pts[4],pts[0],cnt,pts[1]],self.thickness,self.z[2]*1.5,self.z[2]))
        divTiles.append(tile([pts[0],pts[5],pts[3],cnt],self.thickness,self.z[2]*1.5,self.z[2]))
        divTiles.append(tile([cnt,pts[3],pts[6],pts[2]],self.thickness,self.z[2]*1.5,self.z[2]))
        divTiles.append(tile([pts[1],cnt,pts[2],pts[7]],self.thickness,self.z[2]*1.5,self.z[2]))
        for i in range(len(divTiles)):
            divTiles[i].gen()
        return divTiles
    def perforate(self,factor):
        rs.CurrentLayer("structured")
        cnt = self.cntPt()
        vec = rs.VectorCreate(cnt,self.vert[0])
        if factor*vec>self.thickness:
            newPts = []
            cnt = self.cntPt()
            if factor<1:
                for i in range(len(self.vert)):
                    vec = rs.VectorCreate(cnt,self.vert[i])
                    newPts.append(rs.PointAdd(self.vert[i],factor*vec))
            perforatedCell = tile(newPts,0)
            rs.CurrentLayer("windows")
            return perforatedCell.gen()
        else:
            rs.CurrentLayer("structured")
            profile = self.gen()
            return profile
    def cntPt(self):
        sum = [0,0,0]
        for i in range(len(self.vert)):
            sum=rs.PointAdd(self.vert[i],sum)
        cntPt = sum/len(self.vert)
        return cntPt

def SortCurvesByPt(curves,pt):
    indexes = []
    distances = []
    sorted = []
    min = 1000000000
    for i in range(len(curves)):
        param = rs.CurveClosestPoint(curves[i],pt)
        crvPt = rs.EvaluateCurve(curves[i],param)
        distances.append(rs.Distance(crvPt,pt))
    for i in range(len(curves)):
        for j in range(len(distances)):
            if distances[j]<min:
                min = distances[j]
                index = j
        indexes.append(index)
        sorted.append(curves[index])
        distances[index] = 1000000000
        min = 1000000000
    return sorted


def collectIntersections(set,cuts):
    intersectPts = []
    for i in range(len(cuts)):
        intersect = rs.CurveCurveIntersection(set,cuts[i])
        if intersect!=None:
            intersectPts.append(intersect[0][1])
    return intersectPts

def createTiles(sets,cuts,attPts,perfPts,strength):
    pts = []
    myTiles = []
    profiles = []
    thick = .02
    height = .05
    for i in range(len(sets)):
        pts.append(collectIntersections(sets[i],cuts))
    for i in range(len(pts)-1):
        if len(pts[i])<len(pts[i+1]):
            min = len(pts[i])
        else:
            min = len(pts[i+1])
        for j in range(min-1):
            myTiles.append(tile([pts[i][j],pts[i+1][j],pts[i+1][j+1],pts[i][j+1]],thick,height,0))
    for i in range(len(myTiles)):
        cntPt = myTiles[i].cntPt()
        smallTiles = []
        smallerTiles = []
        smallPerf = []
        sum,num = 0,0
        sumP,numP = 0,0
        for j in range(len(attPts)):
            if rs.Distance(cntPt,attPts[j])<strength:
                sum = sum + rs.Distance(cntPt,attPts[j])
                num = num + 1
        for j in range(len(perfPts)):
            if rs.Distance(cntPt,perfPts[j])<strength:
                sumP = sumP + rs.Distance(cntPt,perfPts[j])
                numP = numP + 1
        if num!=0:
            valSub = sum/(num*strength)
        else:
            valSub = 5
        if numP!=0:
            valPerf = sumP/(numP*strength)
        else:
            valPerf = 0
        factorSub = r.random()
        if valSub<factorSub: 
            smallTiles.extend(myTiles[i].subDiv())
            if valSub<factorSub/2:
                for k in range(len(smallTiles)):
                    smallerTiles.extend(smallTiles[k].subDiv())
                if valSub<factorSub/3:
                    for n in range(len(smallerTiles)):
                        smallerTiles[n].thickness = thick*2
                        smallerTiles[n].subDiv()
                        #smallestTiles[n].perforate(valPerf)
        factorPerf = r.random()
        if valPerf<factorPerf and valSub>factorSub:
            myTiles[i].perforate(valPerf)
        else:
            profiles.append(myTiles[i].gen())
    return profiles

def Main():
    crvs = rs.GetObjects("please select grid curves",rs.filter.curve)
    refPt = rs.GetObject("please select reference pt",rs.filter.point)
    attPts = rs.GetObjects("please select attPts",rs.filter.point)
    perfPts = rs.GetObjects("please select perforationPts",rs.filter.point)
    strength = rs.GetReal("please enter attPt range",5)
    rs.AddLayer("windows",[0,0,255])
    rs.AddLayer("structured",[0,255,0])
    crvX = []
    crvY = []
    vecX = rs.VectorCreate(rs.CurveEndPoint(crvs[0]),rs.CurveStartPoint(crvs[0]))
    for i in range(len(crvs)):
        vec = rs.VectorCreate(rs.CurveEndPoint(crvs[i]),rs.CurveStartPoint(crvs[i]))
        if rs.VectorAngle(vec,vecX)<1:
            crvX.append(crvs[i])
        else:
            crvY.append(crvs[i])
    crvX = SortCurvesByPt(crvX,refPt)
    crvY = SortCurvesByPt(crvY,refPt)
    createTiles(crvX,crvY,attPts,perfPts,strength)
    #rs.DeleteObjects(crvX)
    #rs.DeleteObjects(crvY)

Main()