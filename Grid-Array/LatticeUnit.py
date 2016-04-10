import rhinoscriptsyntax as rs
import math as m


class cell:
    def __init__(self,VERTICIES,RATIOS):
        self.ratio = RATIOS
        self.vert = VERTICIES
        self.x = rs.VectorCreate(self.vert[0],self.vert[1])
        self.y = rs.VectorCreate(self.vert[0],self.vert[3])
        self.z = rs.VectorCreate(self.vert[0],self.vert[4])
    def genSubCell(self,origin,indexes):
        subPts = []
        for i in range(len(indexes)):
            vec = rs.VectorCreate(self.vert[origin],self.vert[indexes[i]])/2
            subPt = rs.PointAdd(self.vert[indexes[i]],vec)
            subPts.append(subPt)
        piece = subCell(self.vert[origin],subPts,self.ratio)
        return piece
    def genCell(self):
        mySubCells = []
        members = []
        mySubCells.append(self.genSubCell(0,[1,3,4]))
        mySubCells.append(self.genSubCell(1,[0,2,5]))
        mySubCells.append(self.genSubCell(2,[3,1,6]))
        mySubCells.append(self.genSubCell(3,[2,0,7]))
        mySubCells.append(self.genSubCell(4,[5,7,0]))
        mySubCells.append(self.genSubCell(5,[4,6,1]))
        mySubCells.append(self.genSubCell(6,[7,5,2]))
        mySubCells.append(self.genSubCell(7,[6,4,3]))
        for i in range(len(mySubCells)):
            members.append(mySubCells[i].gen())
        return members

class subCell:
    def __init__(self,ORIGIN,PTS,RATIOS):
        self.origin = ORIGIN
        self.vert = PTS
        self.ratio = RATIOS
        self.axes = []
        for i in range(len(self.vert)):
            self.axes.append(rs.VectorCreate(self.vert[i],self.origin))
    def gen(self):
        members = []
        for i in range(len(self.vert)):
            for j in range(len(self.axes)):
                if i!=j:
                    self.vert[i] = rs.PointAdd(self.vert[i],self.axes[j]*self.ratio[j])
        for i in range(len(self.vert)):
            members.append(rs.AddLine(self.origin,self.vert[i]))
        members.append(rs.AddPolyline(self.vert))
        return members

def grid(x,y,z,dim,attPts,thres):
    newObjs = []
    pts = []
    for i in range(dim):
        for j in range(dim):
            for k in range(dim):
                pts.append([x*i,y*j,z*k])
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
                if val>.5:
                    val = .5
                pts[i] = rs.PointAdd(pts[i],val*vecSum)
    return pts


def Main():
    objs = rs.GetObjects("select objects")
    attPts = rs.GetObjects("select attPts",rs.filter.point)
    box = rs.BoundingBox(objs)
    dim = 8
    X = rs.GetReal("please enter x axis spacing",rs.Distance(box[1],box[0]))
    Y = rs.GetReal("please enter y axis spacing",rs.Distance(box[0],box[3]))
    Z = rs.GetReal("please enter z axis spacing",rs.Distance(box[0],box[4]))
    thres = rs.GetReal("please enter attractor strength",(X+Y+Z)/3*4)
    gridPts = grid(X,Y,Z,dim,attPts,40)
    for i in range(len(gridPts)-dim*dim-1):
        cellPts = [gridPts[i],gridPts[i+dim],gridPts[i+dim*dim+dim],gridPts[i+dim*dim]] 
        cellPts.extend([gridPts[i+1],gridPts[i+dim+1],gridPts[i+dim*dim+dim+1],gridPts[i+dim*dim+1]])
        max = 0
        for j in range(len(cellPts)):
            for k in range(len(cellPts)):
                dist = rs.Distance(cellPts[j],cellPts[k])
                if dist>max:
                    max=dist
        if max<X+Y+Z:
            myCell = cell(cellPts,[.5,0,.5])
            members = myCell.genCell()
        cellPts = []
    return dim

Main()