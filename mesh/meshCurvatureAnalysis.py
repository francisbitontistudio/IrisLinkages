import rhinoscriptsyntax as rs
import math as m

class contours:
    def __init__(self,EVALPTS,BASECRV,VCRVS,RESO):
        self.pts = EVALPTS
        self.crv = BASECRV
        self.vCrvs = VCRVS
        self.reso = RESO
        self.uVals = []
        self.vVals = []
        self.colors = []
        self.position = rs.PointAdd([0,0,0],[0,0,0])
        for i in range(len(self.pts)):
            self.position = rs.PointAdd(self.position,self.pts[i])
        self.position = self.position/len(self.pts)
    def locateVCrvs(self):
        sorted = []
        for j in range(len(self.pts)):
            sorted.append(rs.PointClosestObject(self.pts[j],self.vCrvs)[0])
        self.vCrvs = sorted
        return self.vCrvs
    def uCurvature(self):
        Curvatures = []
        for i in range(len(self.pts)):
            param = rs.CurveClosestPoint(self.crv,self.pts[i])
            tan = rs.CurveTangent(self.crv,param)
            param = rs.CurveNormalizedParameter(self.crv,param)
            reso = self.reso/rs.CurveLength(self.crv)
            if param<(1-reso):
                nextParam = param+reso
            else:
                nextParam = param-reso
            regParam = rs.CurveParameter(self.crv,nextParam)
            tanNext = rs.CurveTangent(self.crv,regParam)
            Curvatures.append(rs.VectorSubtract(tan,tanNext))
        return Curvatures
    def vCurvature(self):
        Curvatures = []
        for i in range(len(self.pts)):
            param = rs.CurveClosestPoint(self.vCrvs[i],self.pts[i])
            tan = rs.CurveTangent(self.vCrvs[i],param)
            param = rs.CurveNormalizedParameter(self.vCrvs[i],param)
            reso = self.reso/rs.CurveLength(self.vCrvs[i])
            if param<(1-reso):
                nextParam = param+reso
            else:
                nextParam = param-reso
            regParam = rs.CurveParameter(self.vCrvs[i],nextParam)
            tanNext = rs.CurveTangent(self.vCrvs[i],regParam)
            Curvatures.append(rs.VectorSubtract(tan,tanNext))
        return Curvatures
    def collectUV(self):
        self.uVals = self.uCurvature()
        self.vCrvs = self.locateVCrvs()
        self.vVals = self.vCurvature()
    def colorCurvature(self):
        self.collectUV()
        maxU = self.uVals[0]
        maxV = self.vVals[0]
        for i in range(len(self.uVals)):
            length = rs.VectorLength(self.uVals[i])
            if length>maxU:
                maxU = length
        for i in range(len(self.vVals)):
            length = rs.VectorLength(self.vVals[i])
            if length>maxV:
                maxV = length
        for i in range(len(self.uVals)):
            colorU = rs.VectorLength(self.uVals[i])/(maxU+.001)*255
            colorV = rs.VectorLength(self.vVals[i])/(maxV+.001)*255
            self.colors.append([colorU,colorV,0])
        return self.colors

def curvekey(curve):
    point = rs.CurveStartPoint(curve)
    return point[2]

def SortCurvesByZ(curves):
    sorted_curves = sorted(curves, key=curvekey)
    return sorted_curves

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

def Main():
    mesh = rs.GetObject("please select mesh",rs.filter.mesh)
    uCrvs = rs.GetObjects("please select vertical contours",rs.filter.curve)
    vCrvs = rs.GetObjects("please select horizontal contours",rs.filter.curve)
    refPt = rs.GetObject("please enter reference point",rs.filter.point)
    uCrvs = SortCurvesByPt(uCrvs,refPt)
    vCrvs = SortCurvesByZ(vCrvs)
    myContours = []
    vertices = rs.MeshVertices(mesh)
    positions =[]
    colors = []
    for i in range(len(uCrvs)):
        evalPts=[]
        for j in range(len(vCrvs)):
            intersectionPts = rs.CurveCurveIntersection(uCrvs[i],vCrvs[j])
            if intersectionPts!=None:
                for i in range(len(intersectionPts)):
                    if intersectionPts[i][0]==1:
                        evalPts.append(intersectionPts[i][1])
        myContours.append(contours(evalPts,uCrvs[i],vCrvs,.01))
    for i in range(len(myContours)):
        positions.append(myContours[i].position)
    for i in range(len(vertices)):
        contourIndex = rs.PointArrayClosestPoint(positions,vertices[i])
        indexEvalPt = rs.PointArrayClosestPoint(myContours[contourIndex].pts,vertices[i])
        myContours[contourIndex].colorCurvature()
        colors.append(myContours[contourIndex].colors[indexEvalPt])
        if myContours[contourIndex].colors[indexEvalPt][0]>200:
            rs.AddPoint(myContours[contourIndex].pts[indexEvalPt])

Main()