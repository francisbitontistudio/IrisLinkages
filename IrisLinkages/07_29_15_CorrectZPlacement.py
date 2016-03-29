import rhinoscriptsyntax as rs
import math as m

#.0625
#.125

#Get the surface object
srf = rs.GetObject("Select surface", rs.filter.surface, True)

#Get the number of rows
rows = rs.GetInteger("Number of rows", 4, 2)

#Get the number of columns
cols = rs.GetInteger("Number of columns",3, 2)

ref=rs.GetObject("please select reference curve",rs.filter.curve)
joint= rs.GetObject("please select joint geometry",rs.filter.polysurface)
arm=rs.GetObject("please select arm geometry",rs.filter.polysurface)
#linkLine=rs.GetObject("please select link line",
#smallLink=rs.GetObject("please select 4-link geometry")
#bigLink=rs.GetObject("please select 2-link geometry")
#gap=rs.GetReal("please indicate the spacing between arms in section",0.625)
#holeRad=rs.GetReal("please indicate the hole width for link input",0.125)

#rows=4
#cols=8
gap=0.5
linkRadius=.5
holeRad=0.5+linkRadius


def attachLinks(bigLink,smallLink,crvs,bigPts,smallPts,ref,rows):
    bigLinks=[]
    smallLinks=[]
    ########################################
    #PROBLEM PLACING LINKS IN RIGHT PLACES... CAN'T SEEM TO FIND RIGHT
    #INDEX VALUES
    for i in range(len(bigPts)):
        vec=rs.VectorCreate(bigPts[i], rs.CurveStartPoint(ref))
        bigLinks.append(rs.CopyObject(bigLink,vec))
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

def genStructure(srf,rows,cols):
    # Get the domain of the surface
    u, v = rs.SurfaceDomain(srf, 0), rs.SurfaceDomain(srf, 1)
    # Turn off redrawing (faster)
    rs.EnableRedraw(False)
    # Add the points
    Epts = []
    Cpts = []
    lns = []
    out = []
    cPointOut = []
    ptsBOX = []
    momentPT = []
    moment = []
    srfEdgePts=[]
    endPts=[]
    for i in range(rows):
        s = u[0] + ((u[1]-u[0])/(rows-1))*i
        sA = u[0] + ((u[1]-u[0])/(rows-1))*i
        sB = u[0] + ((u[1]-u[0])/(rows-1))*(i+1)
        for j in range(cols):
            t = v[0] + ((v[1]-v[0])/(cols-1))*j
            tA = v[0] + ((v[1]-v[0])/(cols-1))*j
            tB = v[0] + ((v[1]-v[0])/(cols-1))*(j+1)

            pt = rs.EvaluateSurface(srf, s, t)
            obj = rs.AddPoint(pt) # add the point
            if j==0 or j==cols-1 or i==0 or i==rows-1:
                srfEdgePts.append(pt)
            else:
                endPts.append(pt)
            if i+1 < len(range(rows)) and j+1 < len(range(cols)):
                lnA = rs.AddLine(rs.EvaluateSurface(srf, sA, tA), rs.EvaluateSurface(srf, sB, tB))
                lnB = rs.AddLine(rs.EvaluateSurface(srf, sA, tB), rs.EvaluateSurface(srf, sB, tA))
                edgeOne = rs.AddLine(rs.EvaluateSurface(srf,sB,tB),rs.EvaluateSurface(srf,sA,tB))
                edgeTwo = rs.AddLine(rs.EvaluateSurface(srf,sA,tA),rs.EvaluateSurface(srf,sB,tA))
                midOne = rs.CurveMidPoint(edgeOne)
                midTwo = rs.CurveMidPoint(edgeTwo)
                rs.AddPoint(midOne)
                rs.AddPoint(midTwo)
                vectorOne = rs.VectorCreate(rs.EvaluateSurface(srf,sA,tA),rs.EvaluateSurface(srf,sB,tA))
                vectorTwo = rs.VectorCreate(rs.EvaluateSurface(srf,sB,tA),rs.EvaluateSurface(srf,sA,tA))

                rEdgeOne=rs.RotateObject(edgeOne, midOne, 90.0, None, copy=False)
                eP1=rs.AddPoint(rs.CurveStartPoint(rEdgeOne))
                ecurveOne=rs.AddLine(midOne,eP1)
                rEdgeTwo=rs.RotateObject(edgeTwo, midTwo, 90.0, None, copy=False)
                eP2=rs.AddPoint(rs.CurveStartPoint(rEdgeTwo))
                ecurveTwo=rs.AddLine(midTwo,eP2)
                rs.DeleteObject(rEdgeTwo)
                rs.DeleteObject(rEdgeOne)
                ptsBOX = [1,2,3,4,5]
                ptsBOX[0]=rs.EvaluateSurface(srf, sA, tA)
                ptsBOX[1]=rs.EvaluateSurface(srf, sA, tB)
                ptsBOX[2]=rs.EvaluateSurface(srf, sB, tB)
                ptsBOX[3]=rs.EvaluateSurface(srf, sB, tA)
                ptsBOX[4]=rs.EvaluateSurface(srf, sA, tA)

                bBox=rs.AddInterpCurve(ptsBOX,1)
                bndry=rs.ExplodeCurves(bBox)
                x=rs.ExtendCurve(ecurveOne,0,1,bndry)
                y=rs.ExtendCurve(ecurveTwo,0,1,bndry)

                nPT=rs.CurveCurveIntersection(x,y,-1)

                if nPT[0][0] == 2:
                    rs.ObjectLayer(momentPT,"Layer 05")
                    nPTx=rs.CurveCurveIntersection(lnA,lnB,-1)
                    momentPT.append(rs.AddPoint(nPTx[0][3]))
                    moment=rs.AddPoint(nPTx[0][3])
                else:
                    momentPT.append(rs.AddPoint(nPT[0][3]))
                    moment=rs.AddPoint(nPT[0][3])
                    rs.ObjectLayer(momentPT,"Layer 05")

                polylnOne=[]
                polylnOne.append(rs.EvaluateSurface(srf,sA,tA))
                polylnOne.append(moment)
                polylnOne.append(rs.EvaluateSurface(srf,sB,tB))
                p1=rs.AddPolyline(polylnOne)

                polylnTwo=[]
                polylnTwo.append(rs.EvaluateSurface(srf,sA,tB))
                polylnTwo.append(moment)
                polylnTwo.append(rs.EvaluateSurface(srf,sB,tA))
                p2=rs.AddPolyline(polylnTwo)

                rs.ObjectLayer(p1,"Layer 05")
                rs.ObjectLayer(p2,"Layer 05")
                lns.append(p1)
                lns.append(p2)


    # Turn on redrawing
    rs.EnableRedraw(True)

    out.append(endPts)
    out.append(srfEdgePts)
    out.append(momentPT)
    out.append(lns)
    return out



def divideline(line):
    pts=[]
    stpt=rs.CurveStartPoint(line)
    edpt=rs.CurveEndPoint(line)
    midpt=rs.CurveMidPoint(line)
    pts.append(stpt)
    pts.append(midpt)
    pts.append(edpt)
    newline=rs.AddPolyline(pts)
    return newline

#### FOR SOME REASON SOME OF THE JOINT GEOMETRIES STOPPED WORKING.
#### YOU HAVE TO USE THE ARM AS THE JOINT GEOMETRY... I DONT KNOW WHY 

def attachArms(body,joint,crvs,ref,rad,gap,rows):
    arms=[]
    joints=[]
    endJoints=[]
    linkPts=[]
    links=[]
    switch=1
    switch2=1
    ####FOR SOME REASON YOU HAVE TO DEFINE GAP IN THE ACTUAL FUNCTION##
    gap=.5
    box=rs.BoundingBox(joint)
    thick=rs.Distance(box[0],box[4])
    start=rs.CurveStartPoint(ref)
    end=rs.CurveEndPoint(ref)
    refLength=rs.CurveLength(ref)
    caps=[]
    for i in xrange(len(crvs)):
        ptpairs=[]
        armpair=[]
        points=rs.CurveEditPoints(crvs[i])
        pts1=[points[0],points[1]]
        pts2=[points[1],points[2]]
        ptpairs.append(pts1)
        #############################3
        ptpairs.append(pts2)
        if i%(rows*2-2)==0:
                switch=-switch
        if switch==-1:
            minStep=4*thick
        else:
            minStep=2*thick
        if switch==-1:
            if i%2==0:
                switch2=-switch2
            if switch2==-1:
                move=minStep+(thick+gap)*(i%2)+gap
            else:
                move=minStep-(thick+gap)*(i%2)+gap
        else:
            if i%2==0:
                switch2=-switch2
            if switch2==-1:
                move=minStep+(thick+gap)*(i%2)-gap
            else:
                move=minStep-(thick+gap)*(i%2)-gap

        for ptpair in ptpairs:
            armStart=ptpair[0]
            armEnd=ptpair[1]
            armLength=rs.Distance(armStart,armEnd)
            refVec=rs.VectorCreate(end,start)
            armVec=rs.VectorCreate(armEnd,armStart)
            movedBody=rs.ScaleObject(body,start,[armLength/refLength,1,1],True)
            movedBody=rs.OrientObject(movedBody,[start,end],[armStart,armEnd],1)
            movedJoint=rs.OrientObject(joint,[start,end],[armStart,armEnd],1)
            
            ptStart=rs.PointAdd(armStart,[0,0,move-gap])
            ptEnd=rs.PointAdd(armStart,[0,0,move+thick+gap])
            linkPts.extend([ptStart,ptEnd])
            rs.MoveObject([movedBody,movedJoint],[0,0,move])
            
            endJoint=rs.CopyObject(movedJoint,armVec)
            linkPts.extend([rs.PointAdd(ptStart,armVec),rs.PointAdd(ptEnd,armVec)])
            endJoint=rs.RotateObject(endJoint,armEnd,180)
            arm=rs.BooleanUnion([movedBody,movedJoint])
            arm=rs.BooleanUnion([arm[0],endJoint])
            armpair.append(arm[0])
        arm=rs.BooleanUnion([armpair[0],armpair[1]])
        arms.append(arm[0])
    #groups all the points that have the same x,y placement then
    #arranges them in z direction
    groups=findOverlays(linkPts)
    for i in range(len(groups)):
        #attaches highest point in sorted list with lowest
        if len(groups[i])>2:
            offset=1.2
            end = groups[i][len(groups[i])-1]
            start=groups[i][0]
            #end=rs.PointAdd(groups[i][len(groups[i])-1],[0,0,-offset])
            #start=rs.PointAdd(groups[i][0],[0,0,offset])
            links.append(rs.AddCylinder(start,end,linkRadius))
        ### THE CAP PLACEMENT ISN'T WORKING FOR SOME REASON ###
        #the caps should end right above the arms, but for some reason
        #their heights are off...
            capBottom=rs.AddCylinder(end,rs.PointAdd(end,[0,0,-offset]),linkRadius*2)
            capTop=rs.AddCylinder(start,rs.PointAdd(start,[0,0,offset]),linkRadius*2)
            caps.extend([capBottom,capTop])
    return [arms,links,caps]


def findOverlays(pts):
    groups=[]
    for i in range(len(pts)):
        group=[pts[i]]
        for j in range(len(pts)):
            valueX=abs(pts[i][0]-pts[j][0])
            valueY=abs(pts[i][1]-pts[j][1])
            #For some reason some arm points are slightly off in the x
            #and y direction which means I had to create a tolerance
            if valueX<3 and valueY<3 and i!=j:
                group.append(pts[j])
        groups.append(group)
    for i in range(len(groups)):
        groups[i]=sortZ(groups[i])
    return groups

def sortZ(pts):
    zPlace=[]
    zSorted=[]
    indexs=[]
    sortedPts=[]
    for i in range(len(pts)):
        zPlace.append(pts[i][2])
    for i in range(len(zPlace)):
        zSorted.append(zPlace[i])
    for i in range(len(zPlace)):
        for j in range(len(zPlace)):
            if zSorted[i]>zSorted[j]:
                zSorted.insert(j,zSorted.pop(i))
    for i in range(len(zPlace)):
        sortedPts.append(pts[zPlace.index(zSorted[i])])
    return sortedPts

def Main():
    rs.EnableRedraw(False)
    setup=genStructure(srf,rows,cols)
    crvs=setup[3]
    sLink=setup[2]
    sLink.extend(setup[1])
    bLink=setup[0]
    parts=attachArms(arm,joint,crvs,ref,gap,holeRad,cols)
    arms=parts[0]
    links=parts[1]
    caps=parts[2]
    remove=rs.AddCylinder(rs.PointAdd(rs.CurveStartPoint(ref),[0,0,1]),12,holeRad)
    holes=attachLinks(remove,remove,crvs,bLink,sLink,ref,cols)
    holes[0].extend(holes[1])
    arms=rs.BooleanDifference(arms,holes[0])
    return [arms,links,caps]

result=Main()
a=result[0]
b=result[1]
c=result[2]