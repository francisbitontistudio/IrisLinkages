import rhinoscriptsyntax as rs

# Get the surface object
srf = rs.GetObject("Select surface", rs.filter.surface, True)

# Get the number of rows
rows = rs.GetInteger("Number of rows", 2, 2)

# Get the number of columns
cols = rs.GetInteger("Number of columns", 2, 2)

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
                cI = rs.CurveCurveIntersection(lnA,lnB)
                rs.AddPoint(cI[0][3])
                Cpts.append(cI[0][3])
                lns.append(lnA)
                lns.append(lnB)


    # Turn on redrawing
    rs.EnableRedraw(True)

    out.append(Epts)
    out.append(Cpts)
    out.append(lns)
    return out


x=genStructure(srf,rows,cols)
