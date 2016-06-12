import rhinoscriptsyntax as rs
import math as m

def testIntersection(crv01,crv02):
    try:
        rs.CurveCurveIntersection(crv01,crv02)
    except None:
        return False
    return True
    
##################################
#GENHATCHX takes the bounding box as a starting point. 
#It defines a reference line on one axis of the
#bounding box, then moves the reference point's end point 
#until it hits the desired hatch angle. Then it calculates
#the necessary number of hatches to cover the profile, arrays
#them, splits the arrayed hatches with the profile
#and deletes all the hatches whose midpoints lie outside
#of the profile
##################################


def genHatchX(profile,ang,space):
    crvs = []
    hatch = []
    sections = []
    box = rs.BoundingBox(profile)
    start = rs.CurveStartPoint(profile)
    #creates ref VECX as a starting axis and direction of copying
    vecX = rs.VectorUnitize(rs.VectorCreate(box[1],box[0]))
    #NUMX is the req. distance to move the end point of the line to form
    #the correct angle of the hatch
    numX = rs.Distance(box[0],box[3])*m.tan(ang*m.pi/180)
    if ang<0:
        axisX = rs.PointAdd(box[0],vecX*numX)
        axisXSt = box[3]
        max = numX+rs.Distance(box[0],box[1])
    else:
        axisX = rs.PointAdd(box[3],-vecX*numX)
        axisXSt = box[0]
        max = numX+rs.Distance(box[0],box[1])
    #X is the first hatch line that will be copied to cover profile
    x = rs.AddCurve([axisXSt,axisX],1)
    #CORRECT lifts the hatch line to the height of the profile
    correct = [0,0,start[2]-box[0][2]]
    x = rs.MoveObject(x,correct)
    #MAX is the dimension that the hatch will have to move over to cover
    #entire profile
    #the for loop below copies each curve down to profile
    for i in range(int(max/space)):
        crvs.append(rs.CopyObject(x,vecX*i*space))
    for i in range(len(crvs)):
        sections.append(splitCrv(crvs[i],[profile]))
    #The splitCrv creates lists of curves that are then checked to 
    #see if they lie within the profile (by looking at their midpoint)
    for i in range(len(sections)):
        for j in range(len(sections[i])):
            if rs.PointInPlanarClosedCurve(rs.CurveMidPoint(sections[i][j]),profile):
                section = sections[i][j]
            else:
                rs.DeleteObject(sections[i][j])
            hatch.append(sections[i][j])
    #rs.DeleteObjects(crvs)
    #rs.DeleteObject(x)
    return crvs

##################################
# GENHATCHY function works the same way as the genHatchX
# it just uses the y axis of the bounding box as a reference
##################################

def genHatchY(profile,ang,space):
    crvs = []
    hatch = []
    sections = []
    box = rs.BoundingBox(profile)
    start = rs.CurveStartPoint(profile)
    vecY = rs.VectorUnitize(rs.VectorCreate(box[3],box[0]))
    numY = rs.Distance(box[0],box[1])*m.tan(ang*m.pi/180)
    axisY = rs.PointAdd(box[1],-vecY*numY)
    y = rs.AddCurve([box[0],axisY],1)
    correct = [0,0,start[2]-box[0][2]]
    y = rs.MoveObject(y,correct)
    max=numY+rs.Distance(box[0],box[3])
    for i in range(int(max/space)):
        crvs.append(rs.CopyObject(y,vecY*i*space))
    for i in range(len(crvs)):
        sections.append(splitCrv(crvs[i],[profile]))
    for i in range(len(sections)):
        for j in range(len(sections[i])):
            if rs.PointInPlanarClosedCurve(rs.CurveMidPoint(sections[i][j]),profile):
                section = sections[i][j]
            else:
                rs.DeleteObject(sections[i][j])
            hatch.append(sections[i][j])
    rs.DeleteObjects(crvs)
    rs.DeleteObject(y)
    return crvs

def splitCrv(profile,splitters):
    sects = []
    #loops through each cutting curve
    for i in range(len(splitters)):
        #checks to see if curves intersect
        if rs.CurveCurveIntersection(splitters[i],profile)!=None:
            params = []
            intersect = rs.CurveCurveIntersection(profile,splitters[i])
            #loops through the result, taking parameter on profile line 
            for j in range(len(intersect)):
                params.append(intersect[j][5])
            #splits the profile curve at those parameters
            sects = rs.SplitCurve(profile,params)
    return sects

def Main():
    profile = rs.GetObject("select profile",rs.filter.curve)
    angX = rs.GetReal("enter angle of hatch in first direction (degrees)", -45)
    angY = rs.GetReal("enter angle of hatch in second direction (degrees)", 45)
    spacingX = rs.GetReal("enter desired spacing of hatch in first direction",2)
    spacingY = rs.GetReal("enter desired spacing of hatch in second direction",2)
    genHatchX(profile,angX,spacingX)
    genHatchY(profile,angY,spacingY)

Main()