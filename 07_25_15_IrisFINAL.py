import rhinoscriptsyntax as rs
import math as m


# Get the surface object
srf = rs.GetObject("Select surface", rs.filter.surface, True)

# Get the number of rows
rows = rs.GetInteger("Number of rows", 2, 2)

# Get the number of columns
cols = rs.GetInteger("Number of columns", 2, 2)

ref=rs.GetObject("please select reference curve",rs.filter.curve)
joint= rs.GetObject("please select joint geometry",rs.filter.polysurface)
arm=rs.GetObject("please select arm geometry",rs.filter.polysurface)
smallLink=rs.GetObject("please select 4-link geometry")
bigLink=rs.GetObject("please select 2-link geometry")
gap=rs.GetReal("please indicate the spacing between arms in section",.0625)
holeRad=rs.GetReal("please indicate the hole width for link input",.125)


def attachLinks(bigLink,smallLink,crvs,smallPts,ref,cols):
    bigLinks=[]
    smallLinks=[]
    bigPts=[]
    for i in range(len(crvs)):
        if i%(cols*2-2)!=0:
            bigPts.append(rs.CurveEndPoint(crvs[i]))
            bigPts.append(rs.CurveStartPoint(crvs[i]))
        else:
            smallPts.append(rs.CurveStartPoint(crvs[i]))
            smallPts.append(rs.CurveStartPoint(crvs[i+1]))
            smallPts.append(rs.CurveEndPoint(crvs[i-1]))
            smallPts.append(rs.CurveEndPoint(crvs[i-2]))
    bigPts=removeDup(bigPts)
    smallPts=removeDup(smallPts)
    for i in range(len(bigPts)):
        bigLinks.append(rs.CopyObject(bigLink,rs.VectorCreate(bigPts[i],rs.CurveStartPoint(ref))))
    for i in range(len(smallPts)):
        smallLinks.append(rs.CopyObject(smallLink,rs.VectorCreate(smallPts[i],rs.CurveStartPoint(ref))))
    return [bigLinks,smallLinks]

def removeDup(freePts):
    pts=[]
    for i in range(len(freePts)):
        pts.append(freePts[i])
    for i in range(len(pts)):
        count=0
        dup=True
        while dup==True:
            index=freePts.index(pts[i])
            test=freePts.pop(freePts.index(pts[i]))
            if pts[i] in freePts:
                freePts.pop(freePts.index(pts[i]))
            if not pts[i] in freePts:
                freePts.insert(index,pts[i])
                dup=False
    return freePts

def ArrayPointsOnSurface(srf,rows,cols):
    lines=[]
    intersects=[]
    # Get the domain of the surface
    u, v = rs.SurfaceDomain(srf, 0), rs.SurfaceDomain(srf, 1)
    if not u or not v: return

    # Turn off redrawing (faster)
    rs.EnableRedraw(False)
    # Add the points
    for j in range(cols):
        t = v[0] + ((v[1]-v[0])/(cols-1))*j
        tA = v[0] + ((v[1]-v[0])/(cols-1))*j
        tB = v[0] + ((v[1]-v[0])/(cols-1))*(j+1)
        tC = v[0] + ((v[1]-v[0])/(cols-1))*(j-1)
        for i in range(rows):
            s = u[0] + ((u[1]-u[0])/(rows-1))*i
            sA = u[0] + ((u[1]-u[0])/(rows-1))*i
            sB = u[0] + ((u[1]-u[0])/(rows-1))*(i+1)
            sC = u[0] + ((u[1]-u[0])/(rows-1))*(i-1)
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

def attachArms(body,joint,crvs,ref,rad,gap,cols):
    arms=[]
    joints=[]
    endJoints=[]
    switch=1
    aligned=False
    box=rs.BoundingBox(joint)
    thick=rs.Distance(box[0],box[4])
    start=rs.CurveStartPoint(ref)
    end=rs.CurveEndPoint(ref)
    refLength=rs.CurveLength(ref)
    for i in range(len(crvs)):
        armStart=rs.CurveStartPoint(crvs[i])
        armEnd=rs.CurveEndPoint(crvs[i])
        armLength=rs.CurveLength(crvs[i])
        refVec=rs.VectorCreate(end,start)
        armVec=rs.VectorCreate(armEnd,armStart)
        movedBody=rs.ScaleObject(body,start,[armLength/refLength,1,1],True)
        movedBody=rs.OrientObject(movedBody,[start,end],[armStart,armEnd],1)
        movedJoint=rs.OrientObject(joint,[start,end],[armStart,armEnd],1)
        if i%(cols*2-2)==0:
            switch=-switch
        if switch==-1:
            minStep=2*thick
        else:
            minStep=0
        rs.MoveObjects([movedBody,movedJoint],[0,0,minStep+(thick+gap)*(i%2)])
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
    arms=attachArms(arm,joint,crvs,ref,holeRad,gap,cols)
    subtractLink=rs.AddCylinder(rs.CurveStartPoint(ref),5,holeRad)
    holes=attachLinks(subtractLink,subtractLink,crvs,intersects,ref,cols)
    holes[0].extend(holes[1])
    links=attachLinks(bigLink,smallLink,crvs,intersects,ref,cols)
    arms=rs.BooleanDifference(arms,holes[0])
    return [arms,links[0],links[1]]

result=Main()
a=result[0]
b=result[1]
c=result[2]