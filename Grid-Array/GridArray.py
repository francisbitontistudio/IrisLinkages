import rhinoscriptsyntax as rs
import math as m

def gridArray(x,y,z,dim,objs):
    newObjs = []
    pts = []
    for i in range(dim):
        for j in range(dim):
            for k in range(dim):
                pts.append([x*i,y*j,z*k])
    box = rs.BoundingBox(objs)
    for i in range(len(pts)):
        vec = rs.VectorCreate(pts[i],box[0])
        newObjs.append(rs.CopyObjects(objs,vec))
    return newObjs


def Main():
    objs = rs.GetObjects("select objects")
    box = rs.BoundingBox(objs)
    spaceX = rs.GetReal("please enter x axis spacing",rs.Distance(box[1],box[0]))
    spaceY = rs.GetReal("please enter y axis spacing",rs.Distance(box[0],box[3]))
    spaceZ = rs.GetReal("please enter z axis spacing",rs.Distance(box[0],box[4]))
    newObjs = gridArray(spaceX,spaceY,spaceZ,4,objs)
    return newObjs

Main()