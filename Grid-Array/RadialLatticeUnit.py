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
    def genCell(self,attPts,thres,maxRatio):
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
            newOrder = mySubCells[i].warpSelf(attPts,thres,maxRatio)
            members.append(mySubCells[i].form(newOrder))
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
            members.append([self.origin,self.vert[i]])
        members.append(self.vert)
        return members
    def warpSelf(self,attPts,thres,maxRatio):
        members = self.gen()
        for i in range(len(members)):
            members[i] = warp(members[i],attPts,thres,maxRatio)
        return members
    def form(self,members):
        crvs = []
        toJoin = []
        for i in range(len(members)):
            crvs.append(rs.AddPolyline(members[i]))
        crvs = rs.JoinCurves(crvs,True)
        return crvs

def grid(theta,phi,rho,nTheta,nPhi,nR,attPts):
    newObjs = []
    pts = []
    for i in range(nTheta):
        for j in range(nPhi):
            for k in range(nR):
                r = k+1
                X = rho*r*m.cos(m.pi/180*phi*j)*m.cos(m.pi/180*theta*i)
                Y = rho*r*m.cos(m.pi/180*phi*j)*m.sin(m.pi/180*theta*i)
                Z = rho*r*m.sin(m.pi/180*phi*j)
                pts.append([X,Y,Z])
    return pts

def warp(pts,attPts,thres,maxRatio):
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
            if val>maxRatio:
                val = maxRatio
            vecSum = vecSum/num
            pts[i] = rs.PointAdd(pts[i],val*vecSum)
    return pts

def Main():
    attPts = rs.GetObjects("select attPts",rs.filter.point)
    theta = rs.GetReal("please enter xy ang spacing",20)
    phi = rs.GetReal("please enter yz ang spacing",20)
    rho = rs.GetReal("please enter shell spacing",10)
    thres = rs.GetReal("please enter attractor strength",rho*4)
    nTheta = rs.GetInteger("please enter angle of XY plane",360/theta)
    nPhi = rs.GetInteger("please enter angle of YZ plane",360/phi)
    nR = rs.GetInteger("please enter number of shells",10)
    maxRatio = rs.GetReal("please enter maximum ratio",.5)
    gridPts = grid(theta,phi,rho,nTheta,nPhi,nR,attPts)
    for i in range(len(gridPts)-nPhi*nR-1):
        cellPts = [gridPts[i],gridPts[i+nR],gridPts[i+nR*nPhi+nR],gridPts[i+nR*nPhi]] 
        cellPts.extend([gridPts[i+1],gridPts[i+nR+1],gridPts[i+nR*nPhi+nR+1],gridPts[i+nR*nPhi+1]])
        max = 0
        sum = [0,0,0]
        for j in range(len(cellPts)):
            sum = rs.PointAdd(sum,cellPts[j])
            for k in range(len(cellPts)):
                dist = rs.Distance(cellPts[j],cellPts[k])
                if dist>max:
                    max=dist
        cnt = sum/len(cellPts)
        sum = [0,0,0]
        if max<rho*2:
            myCell = cell(cellPts,[.5,0,.5])
            members = myCell.genCell(attPts,thres,maxRatio)
            #for j in range(len(members)):
            #    members[j] = rs.ScaleObjects(members[j],cnt,[1.25,1.25,1.25])
        cellPts = []
    return dim

Main()