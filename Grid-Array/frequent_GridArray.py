import rhinoscriptsyntax as rs
import math as m

def gridArray(space,dim,objs):
    newObjs = []
    pts = []
    for i in range(dim):
        for j in range(dim):
            for k in range(dim):
                pts.append([space*i,space*j,space*k])
    box = rs.BoundingBox(objs)
    for i in range(len(pts)):
        vec = rs.VectorCreate(pts[i],box[0])
        newObjs.append(rs.CopyObjects(objs,vec))
    return newObjs


def Main():
    objs = rs.GetObjects("select objects")
    box = rs.BoundingBox(objs)
    space = rs.VectorLength(rs.VectorCreate(box[1],box[0]))
    spacing = rs.GetReal("please enter object spacing",space)
    newObjs = gridArray(spacing,4,objs)
    return newObjs

Main()