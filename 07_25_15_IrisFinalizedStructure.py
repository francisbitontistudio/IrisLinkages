import rhinoscriptsyntax as rs
import math as m


# Get the surface object
srf = rs.GetObject("Select surface", rs.filter.surface, True)
# Get the number of rows
rows = rs.GetInteger("Number of rows", 2, 2)
# Get the number of columns
cols = rs.GetInteger("Number of columns", 2, 2)

joint= rs.GetObject("please select joint geometry",rs.filter.polysurface)
arm=rs.GetObject("please select arm geometry",rs.filter.polysurface)
ref=rs.GetObject("please select reference curve",rs.filter.curve)
link=rs.GetObject("please select link geometry")
gap=rs.GetReal("please indicate the spacing between arms in section")
holeRad=rs.GetReal("please indicate the hole width for link input")


def attachLinks(link,crvs,pts,ref):
    links=[]
    for i in range(len(crvs)):
        pts.append(rs.CurveEndPoint(crvs[i]))
        pts.append(rs.CurveStartPoint(crvs[i]))
    for i in range(len(pts)):
        links.append(rs.CopyObject(link,rs.VectorCreate(pts[i],rs.CurveStartPoint(ref))))
    return links


def ArrayPointsOnSurface(srf,rows,cols):
    lines=[]
    intersects=[]
    # Get the domain of the surface
    u, v = rs.SurfaceDomain(srf, 0), rs.SurfaceDomain(srf, 1)
    if not u or not v: return

    # Turn off redrawing (faster)
    rs.EnableRedraw(False)
    print("test")
    # Add the points
    for i in range(rows):
        s = u[0] + ((u[1]-u[0])/(rows-1))*i
        sA = u[0] + ((u[1]-u[0])/(rows-1))*i
        sB = u[0] + ((u[1]-u[0])/(rows-1))*(i+1)
        sC = u[0] + ((u[1]-u[0])/(rows-1))*(i-1)
        for j in range(cols):
            t = v[0] + ((v[1]-v[0])/(cols-1))*j
            tA = v[0] + ((v[1]-v[0])/(cols-1))*j
            tB = v[0] + ((v[1]-v[0])/(cols-1))*(j+1)
            tC = v[0] + ((v[1]-v[0])/(cols-1))*(j-1)

            #ln = rs.AddLine(start, end)
            pt = rs.EvaluateSurface(srf, s, t)
            obj = rs.AddPoint(pt) # add the point
            #rs.SelectObject(obj)  # select the point

            if i+1 < len(range(rows)) and j+1 < len(range(cols)):
                lnA = rs.AddLine(rs.EvaluateSurface(srf, sA, tA), rs.EvaluateSurface(srf, sB, tB))
                lnB = rs.AddLine(rs.EvaluateSurface(srf, sA, tB), rs.EvaluateSurface(srf, sB, tA))
                cI = rs.CurveCurveIntersection(lnA,lnB)
                pt=rs.PointAdd([0,0,0],cI[0][3])
                lines.append(lnA)
                lines.append(lnB)
                intersects.append(pt)
    # Turn on redrawing
    rs.EnableRedraw(True)
    return [lines,intersects]

def attachArms(body,joint,crvs,ref,rad,gap):
    arms=[]
    joints=[]
    endJoints=[]
    switch=-1
    levels=8
    start=rs.CurveStartPoint(ref)
    end=rs.CurveEndPoint(ref)
    refLength=rs.CurveLength(ref)
    for i in range(len(crvs)):
        armStart=rs.CurveStartPoint(crvs[i])
        armEnd=rs.CurveEndPoint(crvs[i])
        armLength=rs.CurveLength(crvs[i])
        vec=rs.VectorCreate(armStart,start)
        refVec=rs.VectorCreate(end,start)
        armVec=rs.VectorCreate(armEnd,armStart)
        ang=rs.VectorAngle(armVec,refVec)
        movedBody=rs.ScaleObject(body,start,[armLength/refLength,1,1],True)
        movedBody=rs.MoveObject(movedBody,vec)
        movedJoint=rs.CopyObject(joint,vec)
        rs.RotateObjects([movedBody,movedJoint],armStart,ang,[0,0,1])
        if rs.IsPointInSurface(movedBody,rs.CurveMidPoint(crvs[i]))==False:
            rs.RotateObjects([movedBody,movedJoint],armStart,-2*ang)
        if i%levels==0:
            switch=-switch
        if switch==1:
            rs.MoveObjects([movedBody,movedJoint],[0,0,(.25+gap)*(i%4)])
        else:
            rs.MoveObjects([movedBody,movedJoint],[0,0,.75+(3*gap)-(.25+gap)*(i%4)])
        endJoint=rs.CopyObject(movedJoint,armVec)
        endJoint=rs.RotateObject(endJoint,armEnd,180)
        arm=rs.BooleanUnion([movedBody,movedJoint])
        arm=rs.BooleanUnion([arm[0],endJoint])
        arms.append(arm[0])
    return arms


def Main():
    setup=ArrayPointsOnSurface(srf,rows,cols)
    crvs=setup[0]
    intersects=setup[1]
    arms=attachArms(arm,joint,crvs,ref,holeRad,gap)
    holes=attachLinks(rs.AddCylinder(rs.CurveStartPoint(ref),5,holeRad),crvs,intersects,ref)
    links=attachLinks(link,crvs,intersects,ref)
    arms=rs.BooleanDifference(arms,holes)
    return [arms,links]

result=Main()
a=result[0]
b=result[1]
