import rhinoscriptsyntax as rs

def ArrayPointsOnSurface():
    # Get the surface object
    srf = rs.GetObject("Select surface", rs.filter.surface, True)
    if not srf: return

    # Get the number of rows
    rows = rs.GetInteger("Number of rows", 2, 2)
    if not rows: return

    # Get the number of columns
    cols = rs.GetInteger("Number of columns", 2, 2)
    if not cols: return

    # Get the domain of the surface
    u, v = rs.SurfaceDomain(srf, 0), rs.SurfaceDomain(srf, 1)
    if not u or not v: return


    # Turn off redrawing (faster)
    rs.EnableRedraw(False)
    print("test")
    # Add the points
    for i in range(rows):
        s = u[0] + ((u[1]-u[0])/(rows-1))*i
        sA = u[0] + ((u[1]-u[0])/(rows-1))*i
        sB = u[0] + ((u[1]-u[0])/(rows-1))*(i+1)
        sC = u[0] + ((u[1]-u[0])/(rows-1))*(i-1)
        for j in range(cols):
            t = v[0] + ((v[1]-v[0])/(cols-1))*j
            tA = v[0] + ((v[1]-v[0])/(cols-1))*j
            tB = v[0] + ((v[1]-v[0])/(cols-1))*(j+1)
            tC = v[0] + ((v[1]-v[0])/(cols-1))*(j-1)

            #ln = rs.AddLine(start, end)
            pt = rs.EvaluateSurface(srf, s, t)
            obj = rs.AddPoint(pt) # add the point
            #rs.SelectObject(obj)  # select the point

            if i+1 < len(range(rows)) and j+1 < len(range(cols)):
                lnA = rs.AddLine(rs.EvaluateSurface(srf, sA, tA), rs.EvaluateSurface(srf, sB, tB))
                lnB = rs.AddLine(rs.EvaluateSurface(srf, sA, tB), rs.EvaluateSurface(srf, sB, tA))
                cI = rs.CurveCurveIntersection(lnA,lnB)
                rs.AddPoint(cI[0][3])


    # Turn on redrawing
    rs.EnableRedraw(True)


ArrayPointsOnSurface()
