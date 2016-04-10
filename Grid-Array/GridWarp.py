import rhinoscriptsyntax as rs
import math as m

"""
class cell:
    def __init__(self,VERTICIES,RATIOS):
        self.ratio = RATIOS
        self.vert = VERTICIES
        self.x = rs.VectorCreate(self.vert[0],self.vert[1])
        self.y = rs.VectorCreate(self.vert[0],self.vert[3])
        self.z = rs.VectorCreate(self.vert[0],self.vert[4])
        self.v = rs.VectorCreate(self.vert[0],self.vert[2])
        
"""
def gridArray(x,y,z,dim,objs,attPts,thres):
    newObjs = []
    pts = []
    for i in range(dim):
        for j in range(dim):
            for k in range(dim):
                pts.append([x*i,y*j,z*k])
    box = rs.BoundingBox(objs)
    for i in range(len(pts)):
        vecSum = [0,0,0]
        sum = 0
        num = 0
        for j in range(len(attPts)):
            dist = rs.Distance(pts[i],attPts[j])
            if dist<thres:
                vec = rs.VectorCreate(attPts[j],pts[i])
                vecSum = rs.PointAdd(vecSum,vec)
                sum = sum+dist/thres
                num = num+1
            if num>0:
                val = 1-sum/num
                if val>.8:
                    val = .8
                pts[i] = rs.PointAdd(pts[i],val*vecSum)
    for i in range(len(pts)):
        vec = rs.VectorCreate(pts[i],box[0])
        newObjs.append(rs.CopyObjects(objs,vec))
    return newObjs


def Main():
    objs = rs.GetObjects("select objects")
    attPts = rs.GetObjects("select attPts",rs.filter.point)
    box = rs.BoundingBox(objs)
    spaceX = rs.GetReal("please enter x axis spacing",rs.Distance(box[1],box[0]))
    spaceY = rs.GetReal("please enter y axis spacing",rs.Distance(box[0],box[3]))
    spaceZ = rs.GetReal("please enter z axis spacing",rs.Distance(box[0],box[4]))
    newObjs = gridArray(spaceX,spaceY,spaceZ,6,objs,attPts,20)
    return newObjs

Main()