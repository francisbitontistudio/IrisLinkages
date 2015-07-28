import rhinoscriptsyntax as rs

# Get the surface object
srf = rs.GetObject("Select surface", rs.filter.surface, True)

# Get the number of rows
rows = rs.GetInteger("Number of rows", 10)

# Get the number of columns
cols = rs.GetInteger("Number of columns", 20)

# Get the domain of the surface
u, v = rs.SurfaceDomain(srf, 0), rs.SurfaceDomain(srf, 1)



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
    ptsBOX = []
    momentPT = []

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
            Epts.append(pt)


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
                    momentPT=rs.AddPoint(nPTx[0][3])
                else:
                    momentPT=rs.AddPoint(nPT[0][3])
                    rs.ObjectLayer(momentPT,"Layer 05")

                polylnOne=[]
                polylnOne.append(rs.EvaluateSurface(srf,sA,tA))
                polylnOne.append(momentPT)
                polylnOne.append(rs.EvaluateSurface(srf,sB,tB))
                p1=rs.AddPolyline(polylnOne)

                polylnTwo=[]
                polylnTwo.append(rs.EvaluateSurface(srf,sA,tB))
                polylnTwo.append(momentPT)
                polylnTwo.append(rs.EvaluateSurface(srf,sB,tA))
                p2=rs.AddPolyline(polylnTwo)

                rs.ObjectLayer(p1,"Layer 05")
                rs.ObjectLayer(p2,"Layer 05")
                lns.append(p1)
                lns.append(p2)


    # Turn on redrawing
    rs.EnableRedraw(True)

    out.append(Epts)
    out.append(momentPT)
    out.append(lns)
    return out


x=genStructure(srf,rows,cols)
