import rhinoscriptsyntax as rs
import math as m


profile=rs.GetObject("please select profile curve",rs.filter.curve)
layers=rs.GetReal("please select number of layers")
dist=rs.GetReal("offset distance?")
joint=rs.GetObject("please select joint geometry",rs.filter.polysurface)
ref=rs.GetObject("please select ref curve",rs.filter.curve)

def centerPt(crv):
    pts=rs.DivideCurve(crv,20)
    sum=[0,0,0]
    for i in range(len(pts)):
        sum=rs.PointAdd(sum,pts[i])
    center=sum/len(pts)
    return center

def offsetCrvOut(sections,crv,dist):
    crvs=[crv]
    center=centerPt(crv)
    param=rs.CurveClosestPoint(crv,center)
    closestPt=rs.EvaluateCurve(crv,param)
    dir=rs.VectorCreate(closestPt,center)
    for i in range(int(sections)):
        layer=dist/sections*(i+1)
        crvs.extend(rs.OffsetCurve(crv,-dir,layer))
    return crvs

def tileCrvs(crvs,tiles,sections):
    lines=[]
    pts=[]
    crosses=[]
    delete=[]
    innerPts=rs.DivideCurve(crvs[0],tiles)
    outerPts=rs.DivideCurve(crvs[len(crvs)-1],tiles)
    for i in range(len(innerPts)):
        line=rs.AddLine(innerPts[i],outerPts[i])
        lines.append(line)
    for i in range(len(crvs)):
        for j in range(len(lines)):
            pts.append(rs.CurveCurveIntersection(crvs[i],lines[j])[0][1])
    for i in range(len(pts)):
        if i<len(pts)-tiles-3:
            crosses.append(rs.AddLine(pts[i],pts[i+tiles+2]))
            crosses.append(rs.AddLine(pts[i],pts[i+tiles]))
    for i in range(len(crosses)):
        if i<len(crosses)-1:
            if rs.CurveLength(crosses[i])>rs.CurveLength(crosses[i+1])*6:
                delete.append(crosses[i])
    #crosses.extend(lines)
    rs.DeleteObjects(delete)
    return crosses

def attachJoints(joint,crvs,ref):
    joints=[]
    start=rs.CurveStartPoint(ref)
    end=rs.CurveEndPoint(ref)
    for i in range(len(crvs)):
        if rs.IsCurve(crvs[i]):
            armStart=rs.CurveStartPoint(crvs[i])
            armEnd=rs.CurveEndPoint(crvs[i])
            ##################################
            vec=rs.VectorCreate(armEnd,start)
            refVec=rs.VectorCreate(end,start)
            armVec=rs.VectorCreate(armEnd,armStart)
            ang=rs.VectorAngle(armVec,refVec)
            movedJoint=rs.CopyObject(joint,vec)
            if i%2!=0:
                ang=-ang
                movedJoint=rs.MoveObject(movedJoint,[0,0,-.25])
            joints.append(rs.RotateObject(movedJoint,armEnd,ang,[0,0,1]))
    return joints


def Main():
    list=offsetCrvOut(layers,profile,dist)
    crosses=tileCrvs(list,100,layers)
    joints=attachJoints(joint,crosses,ref)
    return [crosses,joints]


result=Main()
a=result[0]
b=result[1]