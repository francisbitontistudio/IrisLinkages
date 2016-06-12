import rhinoscriptsyntax as rs
import random as r
import math as m

class attractors:
    def __init__(self,PTS,RESO,INVERT):
        self.locs = PTS
        self.reso = RESO
        self.invert = INVERT
        self.val = 1
    def collectVal(self,pt,min,max):
        sum = 0
        num = 0
        for i in range(len(self.locs)):
            dist = rs.Distance(self.locs[i],pt)
            if dist<self.reso:
                sum = sum+dist
                num = num+1
        if num!=0:
            val = sum/(num*self.reso)
            if self.invert == True:
                self.val = 1-val
            else:
                self.val = val
            if val < min:
                self.val = min
            if val > max:
                self.val = max
        elif self.invert == False:
            self.val = 1
        elif self.invert == True:
            self.val = 0
        return self.val

class tile:
    def __init__(self,VERTICIES,THICKNESS,HEIGHT,DIVISION):
        self.vert = VERTICIES
        self.x = rs.VectorCreate(self.vert[1],self.vert[0])
        self.y = rs.VectorCreate(self.vert[3],self.vert[0])
        self.thick = THICKNESS
        self.z = [0,0,HEIGHT]
        self.div = int(DIVISION)
        self.pts = []
        self.mesh = []
    def gen(self,cnt=False,cap=False,connect=True):
        pts = []
        newPts = []
        faces = []
        cntPt = self.cntPt()
        if cnt==False:
            self.subDiv(self.z[2])
            print len(self.pts)
        else:
            self.pts = []
            for i in range(len(self.vert)):
                self.pts.append(self.vert[i])
            self.pts.append(self.vert[0])
        for i in range(len(self.pts)):
            vec = rs.VectorCreate(cntPt,self.pts[i])*self.thick
            vec = rs.VectorAdd(vec,self.z)
            newPts.append(rs.PointAdd(self.pts[i],vec))
        pts.extend(self.pts)
        pts.extend(newPts)
        if connect==True:
            for i in range(len(self.pts)):
                if i<len(self.pts)-1:
                    faces.append([i,i+len(self.pts),i+len(self.pts)+1,i+1])
                else:
                    faces.append([i,i+len(self.pts),len(self.pts),0])
        if cap==True:
            #faces.append([0,1,2,3])
            faces.append([5,6,7,8])
        profile = rs.AddMesh(pts,faces)
        return profile
    def subDiv(self,height):
        rs.CurrentLayer("structured")
        pts = []
        divTiles = []
        cnt = self.cntPt()
        inter = 1/self.div
        for i in range(int(self.div+1)):
            xPts = []
            for j in range(int(self.div+1)):
                pt = rs.PointAdd(self.vert[0],self.x*inter*i)
                pt = rs.PointAdd(pt,self.y*inter*j)
                xPts.append(pt)
            pts.append(xPts)
        mid = int(self.div/2)
        end = int(self.div)
        divTiles.append(tile([pts[0][0],pts[mid][0],pts[mid][mid],pts[0][mid]],self.thick,height,int(self.div)))
        divTiles.append(tile([pts[0][mid],pts[mid][mid],pts[mid][end],pts[0][end]],self.thick,height,int(self.div)))
        divTiles.append(tile([pts[mid][mid],pts[end][mid],pts[end][end],pts[mid][end]],self.thick,height,int(self.div)))
        divTiles.append(tile([pts[mid][0],pts[end][0],pts[end][mid],pts[mid][mid]],self.thick,height,int(self.div)))
        for i in range(int(self.div)+1):
            self.pts.append(pts[i][0])
        for i in range(int(self.div)):
            self.pts.append(pts[int(self.div)][i+1])
        for i in range(int(self.div)):
            self.pts.append(pts[int(self.div)-(i+1)][int(self.div)])
        for i in range(int(self.div)):
                self.pts.append(pts[0][int(self.div)-(i+1)])
        return divTiles
    def subDivGen(self,height,cap=False,connect=True):
        meshes = []
        divTiles = self.subDiv(self.z[2])
        for i in range(len(divTiles)):
            divTiles[i].div = int(self.div/2)
            print divTiles[i].div
            self.mesh.append(divTiles[i].gen(False,cap,connect))
        return divTiles
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
        crvPt = [crvPt[0],crvPt[1],0]
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

def createTiles(sets,cuts,structPts,perfPts,container,strength,height,srf):
    pts = []
    myTiles = []
    profiles = []
    minThick = .1
    maxThick = .8
    division = 4
    structAtt = attractors(structPts,strength,False)
    perfAtt = attractors(perfPts,strength,False)
    for i in range(len(sets)):
        pts.append(collectIntersections(sets[i],cuts))
    for i in range(len(pts)-1):
        if len(pts[i])<len(pts[i+1]):
            min = len(pts[i])
        else:
            min = len(pts[i+1])
        for j in range(min-1):
            myTiles.append(tile([pts[i][j],pts[i+1][j],pts[i+1][j+1],pts[i][j+1]],minThick,height,division))
    for i in range(len(myTiles)):
        cntPt = myTiles[i].cntPt()
        
        if rs.IsPointInSurface(container,cntPt):
            smallTiles = []
            smallerTiles = []
            smallPerf = []
            valStruct = structAtt.collectVal(cntPt,0,1)
            valPerf = perfAtt.collectVal(cntPt,minThick,maxThick)
            factorStruct = r.random()
            myTiles[i].thick = valPerf
            cntPt = myTiles.
            if valStruct<factorStruct: 
                smallTiles = myTiles[i].subDivGen(height)
                if valStruct<factorStruct/2:
                    for k in range(len(smallTiles)):
                        cntPt=smallTiles[k].cntPt()
                        valStruct = structAtt.collectVal(cntPt,0,1)
                        valPerf = perfAtt.collectVal(cntPt,minThick,maxThick)
                        smallTiles[k].thick = valPerf
                        factorStruct = r.random()
                        if valStruct < factorStruct:
                            rs.DeleteObjects(smallTiles[k].mesh)
                            rs.DeleteObjects(myTiles[i].mesh)
                            smallerTiles.extend(smallTiles[k].subDivGen(height))
                        else:
                            smallTiles[k].gen(False,False,True)
            else:
                myTiles[i].thick = .2
                myTiles[i].gen(True,False,True)
    return profiles

def Main():
    crvs = rs.GetObjects("please select grid curves",rs.filter.curve)
    polySrf = rs.GetObjects("please select geo",rs.filter.polysurface)
    refPt = rs.GetObject("please select reference pt",rs.filter.point)
    structPts = rs.GetObjects("please select structural Pts",rs.filter.point)
    perfPts = rs.GetObjects("please select perforationPts",rs.filter.point)
    container = rs.GetObjects("please select containers",rs.filter.polysurface)
    strength = rs.GetReal("please enter attPt range",5)
    height = rs.GetReal("please enter height",.05)
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
    createTiles(crvX,crvY,structPts,perfPts,container,strength,height)
    #rs.DeleteObjects(crvX)
    #rs.DeleteObjects(crvY)

Main()