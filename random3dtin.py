#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 12 11:27:15 2018

@author: kavisha
"""

#Random TIN terrain generator at CityGML LOD0, LOD1, LOD2, & LOD3

import argparse
import uuid
import random
from lxml import etree
from math import pi, sin, cos, sqrt
import math
import numpy as np
import triangle
from shapely import geometry
from shapely.geometry import Polygon,Point

#CityGML 2.0 namespaces
ns_citygml = "http://www.opengis.net/citygml/2.0"
ns_gml = "http://www.opengis.net/gml"
ns_bldg = "http://www.opengis.net/citygml/building/2.0"
ns_xsi = "http://www.w3.org/2001/XMLSchema-instance"
ns_xAL = "urn:oasis:names:tc:ciq:xsdschema:xAL:2.0"
ns_xlink = "http://www.w3.org/1999/xlink"
ns_dem = "http://www.opengis.net/citygml/relief/2.0"
ns_gen = "http://www.opengis.net/citygml/generics/2.0"

nsmap = {
    None: ns_citygml,
    'gml': ns_gml,
    'bldg': ns_bldg,
    'xsi': ns_xsi,
    'xAL': ns_xAL,
    'xlink': ns_xlink,
    'dem': ns_dem,
    'gen': ns_gen
}


def argRead(arg, default=None):
    if arg == "0" or arg == "False":
        arg = False
    elif arg == "1" or arg == "True":
        arg = True
    elif arg is None:
        if default:
            arg = default
        else:
            arg = False
    else:
        raise ValueError("Unknown Argument!!!")
    return arg


def getxy(points):
    p1 = np.array(points[0])
    p2 = np.array(points[1])
    p3 = np.array(points[2])

    v1 = p3 - p1
    v2 = p2 - p1

    cp = np.cross(v1, v2)
    a, b, c = cp
    d = np.dot(cp, p3)
    
    origin = np.array(points[0])
#    magnitude  = math.sqrt(pow(origin[0], 2) + pow(origin[1], 2) + pow(origin[2],2))
    
    normal = np.array([a,b,c])
    nmag = math.sqrt(pow(a, 2) + pow(b, 2) + pow(c,2))
    n = np.array([normal[0]/nmag,normal[1]/nmag,normal[2]/nmag])
    
    zxvalue = -((d+a)/c)
    
    x = np.array([abs(a),0,zxvalue]) 
    x = x - np.dot(x, n) * n
    x /= math.sqrt((x**2).sum())   
    y = np.cross(n, x)
    
    return x,y,origin,n

def polygon_overlap(square0, square1):
    poly1 = Polygon(square0)
    poly2 = Polygon(square1)
    for p0 in list(poly1.exterior.coords):
        if Point(p0).within(poly2):
            return True
    for p1 in list(poly2.exterior.coords):
        if Point(p1).within(poly1):
            return True
    return False  
        
def generate_polygons(lowerbound,upperbound,polygons_to_delete=()):
    
    while 1:
        restart = False
        x0 = random.uniform(lowerbound[0], upperbound[0])
        y0 = random.uniform(lowerbound[1], upperbound[1])
        z0 = random.uniform(lowerbound[2], upperbound[2])
            
        angle = random.random() * pi * 0.5
        fangle = angle
        x1 = x0 + side * sqrt(2) * cos(angle)
        y1 = y0 + side  * sqrt(2) * sin(angle)
        z1 = random.uniform(lowerbound[2], upperbound[2])
        
            
        angle += pi * 0.5
        x2 = x1 + side * sqrt(2) * cos(angle)
        y2 = y1 + side * sqrt(2) * sin(angle)
        z2 = random.uniform(lowerbound[2], upperbound[2])
        
        angle += pi * 0.5
        x3 = x2 + side * sqrt(2) * cos(angle)
        y3 = y2 + side  * sqrt(2) * sin(angle)
        z3 = random.uniform(lowerbound[2], upperbound[2])
            
        polycoords3D = [(x0,y0,z0),(x1,y1,z1), (x2,y2,z2),(x3,y3,z3)]
        polycoords2D =  (x0, y0), (x1, y1), (x2, y2), (x3, y3)
        
        for polygon in polygons_to_delete:
            if polygon_overlap(polycoords2D, polygon):
                restart = True
        if restart:
            continue
        return  polycoords2D, polycoords3D, fangle
        
def number_polygons(number_of_points):
    if (number_of_points <= 50):
        nums = number_of_points/number_of_points
    elif (number_of_points > 50 and number_of_points < 1000):
        nums = number_of_points/20
    elif (number_of_points >= 1000 and number_of_points < 10000):
        nums = number_of_points/200
    elif (number_of_points >= 10000 and number_of_points < 100000):
        nums = number_of_points/2000
    elif (number_of_points >= 100000 and number_of_points < 1000000):
        nums = number_of_points/20000
    elif (number_of_points >= 1000000 and number_of_points < 10000000):
        nums = number_of_points/200000  
    return nums  

def gen_vertical_walls(ground,origin,x,y):
    
    faces =[]  
    randomh = random.uniform(15.0, upperBound[2])
    side1 = [ground[0],ground[1],(ground[0][0],ground[0][1],ground[0][2]+randomh),(ground[1][0],ground[1][1],ground[1][2]+randomh)]
    localside11 = []
    for p in side1:
        localside11.append((np.dot(p - origin, x),np.dot(p - origin, y)))    
    tr = triangle.delaunay(localside11) 
    for t in tr:
        s = [side1[t[0]],side1[t[1]],side1[t[2]]]
        sp = Polygon(s)
        sp = geometry.polygon.orient(sp, 1)
        faces.append(sp)             
    
    side2 = [ground[1],ground[2],(ground[1][0],ground[1][1],ground[1][2]+randomh),(ground[2][0],ground[2][1],ground[2][2]+randomh)]
    localside22 = []
    for p in side2:
        localside22.append((np.dot(p - origin, x),np.dot(p - origin, y)))    
    tr = triangle.delaunay(localside22) 
    for t in tr:
        s = [side2[t[0]],side2[t[1]],side2[t[2]]]
        sp = Polygon(s)
        sp = geometry.polygon.orient(sp, 1)
        faces.append(sp)             
    
    side3 = [ground[2],ground[3],(ground[2][0],ground[2][1],ground[2][2]+randomh),(ground[3][0],ground[3][1],ground[3][2]+randomh)]
    localside33 = []
    for p in side3:
        localside33.append((np.dot(p - origin, x),np.dot(p - origin, y)))    
    tr = triangle.delaunay(localside33) 
    for t in tr:
        s = [side3[t[0]],side3[t[1]],side3[t[2]]]
        sp = Polygon(s)
        sp = geometry.polygon.orient(sp, 1)
        faces.append(sp)             
    
    side4 = [ground[3],ground[0],(ground[3][0],ground[3][1],ground[3][2]+randomh),(ground[0][0],ground[0][1],ground[0][2]+randomh)]
    localside44 = []
    for p in side4:
        localside44.append((np.dot(p - origin, x),np.dot(p - origin, y)))    
    tr = triangle.delaunay(localside44) 
    for t in tr:
        s = [side4[t[0]],side4[t[1]],side4[t[2]]]
        sp = Polygon(s)
        sp = geometry.polygon.orient(sp, 1)
        faces.append(sp)               
    
    roof = [(ground[0][0],ground[0][1],ground[0][2]+randomh),(ground[1][0],ground[1][1],ground[1][2]+randomh),(ground[2][0],ground[2][1],ground[2][2]+randomh),(ground[3][0],ground[3][1],ground[3][2]+randomh)]
    localroof = []
    for p in roof:
        localroof.append((np.dot(p - origin, x),np.dot(p - origin, y)))    
    tr = triangle.delaunay(localroof)  
    for t in tr:
        s = [roof[t[0]],roof[t[1]],roof[t[2]]]
        sp = Polygon(s)
        sp = geometry.polygon.orient(sp, 1)
        faces.append(sp)             
    
    return faces 
  
def gen_ground_triangles(ground,origin,x,y):    
    faces =[]       
    localGround = []
    for p in ground:
        localGround.append((np.dot(p - origin, x),np.dot(p - origin, y)))    
    tr = triangle.delaunay(localGround) 
    for t in tr:
        s = [ground[t[0]],ground[t[1]],ground[t[2]]]
        sp = Polygon(s)
        sp = geometry.polygon.orient(sp, 1)
        faces.append(sp)  
        
#    ground1 = [ground[0],ground[1],ground[2],ground[0]]
#    ground2 =[ground[2],ground[3],ground[0],ground[2]]
#    g1 = Polygon(ground1)
#    g1 = geometry.polygon.orient(g1, 1)
#    g2 = Polygon(ground2)
#    g2 = geometry.polygon.orient(g2, 1)
    
#    faces.append(g1)
#    faces.append(g2)

    return faces
         
# terrainLOD0
def terrainLOD0(fname, npoints, lowerbound, upperbound, cityModel):
    i = 0
    points = []
    ptdir = {}
    
    while i<npoints:
        randomx = random.uniform(lowerbound[0], upperbound[0])
        randomy = random.uniform(lowerbound[1], upperbound[1])
        randomz = random.uniform(lowerbound[2], upperbound[2])
        
        points.append([randomx,randomy,randomz])
        ptdir[i]=[randomx,randomy,randomz]
    
        i=i+1
    
    x,y,origin,n = getxy(points)
    
    local_coords =[]
    sep =[]
    for p in points:
        S = np.dot(n, p-origin)
        sep.append(S)
        local_coords.append((np.dot(p - origin, x),np.dot(p - origin, y)))
    
    tri = triangle.delaunay(local_coords)            
    get_TINRelief(cityModel, tri, ptdir, "lod0")  

def terrainLOD1_2_3(fname, npoints, lowerbound, upperbound, cityModel, modelRun): # 2.5D + vertical walls
    nums = int(number_polygons(npoints))
    polyCoordsList2D = []
    polyCoordsList3D = []
    polyList3D = []
    holePoints = []
    tinPoints = []
    tinPtdir = {}    
    
    #for building polygons
    i = 0
    j = 0
    while i<nums:
        polycoords2D, polycoords3D, ff = generate_polygons(lowerbound,upperbound,polygons_to_delete=polyCoordsList2D)
        polyCoordsList2D.append(polycoords2D)
        polyCoordsList3D.append(polycoords3D)
        
        poly3D = Polygon(polycoords3D)
        poly3D = geometry.polygon.orient(poly3D, 1)
        polyList3D.append(poly3D)
        
        dx = (polycoords3D[0][0]+polycoords3D[2][0])/2
        dy = (polycoords3D[0][1]+polycoords3D[2][1])/2
        dz = (polycoords3D[0][2]+polycoords3D[2][2])/2
        holePoints.append([dx,dy,dz])
        
        for polycoord in polycoords3D:
            tinPtdir[j] = list(polycoord)
            tinPoints.append(polycoord)
            j = j + 1 
        i = i + 1
    
    #for terrain 
    k = 0
    while k<(npoints-len(polyCoordsList3D)*4):
        randomx = random.uniform(lowerbound[0], upperbound[0])
        randomy = random.uniform(lowerbound[1], upperbound[1])
        randomz = random.uniform(lowerbound[2], upperbound[2])
        
        for poly3D in polyList3D:
            if poly3D.contains(Point(randomx,randomy,randomz)):
                print ("Discarded Point inside the polygon!")
            else:
                break
        tinPoints.append([randomx,randomy,randomz])           
        tinPtdir[j] = [randomx,randomy,randomz]
    
        j = j + 1    
        k = k + 1
    
    x,y,origin,n = getxy(tinPoints)
    sep =[]
    segmentList = []
    holeCoordsList = []
    localCoordsList = []
    holePtSepList = []
    for p in tinPoints:
        S = np.dot(n, p-origin)
        sep.append(S)
        localCoordsList.append((np.dot(p - origin, x),np.dot(p - origin, y)))

    for holePt in holePoints:
        holePtSep = np.dot(n, holePt-origin)
        holePtSepList.append(holePtSep)
        holeCoordsList.append((np.dot(holePt - origin, x),np.dot(holePt - origin, y)))
    
    for poly in polyList3D:
        
        polycoord = list(poly.exterior.coords)
        
        s0 = (list(tinPtdir.keys())[list(tinPtdir.values()).index(list(polycoord[0]))])
        s1 = (list(tinPtdir.keys())[list(tinPtdir.values()).index(list(polycoord[1]))])
        s2 = (list(tinPtdir.keys())[list(tinPtdir.values()).index(list(polycoord[2]))])
        s3 = (list(tinPtdir.keys())[list(tinPtdir.values()).index(list(polycoord[3]))])
        
        segmentList.append([s0,s1])
        segmentList.append([s1,s2])
        segmentList.append([s2,s3])
        segmentList.append([s3,s0])
    
    if modelRun == "lod1":
        facelist = []   
        for polycoord in polyCoordsList3D:                          
            faces = gen_vertical_walls(polycoord,origin,x,y)
            facelist.append(faces)
        
        inputs = {'vertices':np.asarray(localCoordsList),'segments': np.asarray(segmentList),'holes':np.asarray(holeCoordsList)}
        tri = triangle.triangulate(inputs,'pcS')
        get_TINRelief(cityModel, tri, tinPtdir, "lod1", facelist)
    
    elif modelRun == "lod2":
        facelist = []   
        for polycoord in polyCoordsList3D:                          
            faces = gen_ground_triangles(polycoord,origin,x,y)
            facelist.append(faces)
        
        inputs = {'vertices':np.asarray(localCoordsList),'segments': np.asarray(segmentList),'holes':np.asarray(holeCoordsList)}
        tri = triangle.triangulate(inputs,'pcS')
        get_TINRelief(cityModel, tri, tinPtdir, "lod2", facelist, polyCoordsList3D)
        
    elif modelRun == "lod3":
        facelist = []   
        for polycoord in polyCoordsList3D:                          
            faces = gen_vertical_walls(polycoord,origin,x,y)
            facelist.append(faces)
        
        inputs = {'vertices':np.asarray(localCoordsList),'segments': np.asarray(segmentList),'holes':np.asarray(holeCoordsList)}
        tri = triangle.triangulate(inputs,'pcS')
        get_TINRelief(cityModel, tri, tinPtdir, "lod3", facelist, polyCoordsList3D)
 
    
#CityGML TINRelief   
def get_TINRelief(cityModel, tri, ptdir, modelRun, facelist=None, polyCoordsList3D=None):
    cityObject = etree.SubElement(cityModel, "cityObjectMember")
    relFeature = etree.SubElement(cityObject, "{%s}ReliefFeature" % ns_dem)
    relFeature.attrib['{%s}id' % ns_gml] = "GML_"+str(uuid.uuid4())
    name = etree.SubElement(relFeature, "{%s}name" % ns_gml)
    name.text = "TIN Model"
    lod = etree.SubElement(relFeature, "{%s}lod" % ns_dem)
    
    relComponent = etree.SubElement(relFeature, "{%s}reliefComponent" % ns_dem)
    tinRelief = etree.SubElement(relComponent, "{%s}TINRelief" % ns_dem)
    tinRelief.attrib['{%s}id' % ns_gml] = "GML_"+str(uuid.uuid4())
    tinName = etree.SubElement(tinRelief, "{%s}name" % ns_gml)
    tinName.text = "TIN model"
    
    genAttribute1 = etree.SubElement(tinRelief, "{%s}intAttribute" % ns_gen)
    genAttribute1.attrib['name'] = "numberOfTriangles"
    genValue1 = etree.SubElement(genAttribute1, "{%s}value" % ns_gen)
    
    if modelRun == "lod1" or modelRun == "lod3":
        genAttribute2 = etree.SubElement(tinRelief, "{%s}stringAttribute" % ns_gen)
        genAttribute2.attrib['name'] = "vertTrianglesID"
        genValue2 = etree.SubElement(genAttribute2, "{%s}value" % ns_gen)
        genValue2.text = ""
    
#    facetrianglesID = []
    if modelRun == "lod2" or modelRun == "lod3":
        pc = 0
        for face in facelist:
            gaSet = etree.SubElement(tinRelief, "{%s}genericAttributeSet" % ns_gen)
            
            genAttribute3 = etree.SubElement(gaSet, "{%s}stringAttribute" % ns_gen)
            genAttribute3.attrib['name'] = "cityObjectType"
            genValue3 = etree.SubElement(genAttribute3, "{%s}value" % ns_gen)
            genValue3.text = ""    
            
            genAttribute4 = etree.SubElement(gaSet, "{%s}stringAttribute" % ns_gen)
            genAttribute4.attrib['name'] = "cityObjectID"
            genValue4 = etree.SubElement(genAttribute4, "{%s}value" % ns_gen)
            genValue4.text = "" 
            
            genAttribute5 = etree.SubElement(gaSet, "{%s}stringAttribute" % ns_gen)
            genAttribute5.attrib['name'] = "extent"
            genValue5 = etree.SubElement(genAttribute5, "{%s}value" % ns_gen)
            genValue5.text = "" 
            
            cityObject = etree.SubElement(cityModel, "cityObjectMember")
            building = etree.SubElement(cityObject, "{%s}Building" % ns_bldg)
            genValue3.text = "Building" 
            building.attrib['{%s}id' % ns_gml] = "GML_"+str(uuid.uuid4())
            genValue4.text = building.attrib['{%s}id' % ns_gml]
            gaSet.attrib['name'] = "Building"+genValue4.text
            bName = etree.SubElement(building, "{%s}name" % ns_gml)
            
            if modelRun == "lod2":
                bName.text = "LOD0 Building Footprint Model"
                bPrint = etree.SubElement(building, "{%s}lod0FootPrint" % ns_bldg)
            elif modelRun == "lod3":
                bName.text = "LOD1 Building Surface Model"
                bPrint = etree.SubElement(building, "{%s}lod1MultiSurface" % ns_bldg)
            
            multiSurface = etree.SubElement(bPrint, "{%s}MultiSurface" % ns_gml)
            genValue5.text = str(np.array(polyCoordsList3D[pc]).flatten()).strip(']').strip('[').replace(","," ") 
            pc = pc + 1
            for ff in face:
                surfaceMenmber=etree.SubElement(multiSurface, "{%s}surfaceMember" % ns_gml)
                bpoly=etree.SubElement(surfaceMenmber, "{%s}Polygon" % ns_gml)
                bexterior=etree.SubElement(bpoly, "{%s}exterior" % ns_gml)
                blinRing=etree.SubElement(bexterior, "{%s}LinearRing" % ns_gml)
#                blid = "GML_"+str(uuid.uuid4())
#                blinRing.attrib['{%s}id' % ns_gml] = "#"+blid
#                facetrianglesID.append(blid)
                bpList=etree.SubElement(blinRing, "{%s}posList" % ns_gml)
                bpList.attrib['srsDimension'] = "3"
                bpList.text = " "        
                bpList.text = bpList.text + str(ff).strip('POLYGON Z ((').strip('))').replace(","," ")  

    
    lodTin = etree.SubElement(tinRelief, "{%s}lod" % ns_dem)    
    demTin = etree.SubElement(tinRelief, "{%s}tin" % ns_dem)
    triSurface = etree.SubElement(demTin, "{%s}TriangulatedSurface" % ns_gml)
    triPatches = etree.SubElement(triSurface, "{%s}trianglePatches" % ns_gml)
      
    if modelRun == "lod0":
        lod.text="0"
        lodTin.text="0"
        genValue1.text = str(len(tri))
        for t in tri: 
            triangle = etree.SubElement(triPatches, "{%s}Triangle" % ns_gml)
            exterior = etree.SubElement(triangle, "{%s}exterior" % ns_gml)
            linRing = etree.SubElement(exterior, "{%s}LinearRing" % ns_gml)
            linRing.attrib['{%s}id' % ns_gml] = "GML_"+str(uuid.uuid4())
            pList = etree.SubElement(linRing, "{%s}posList" % ns_gml)
            pList.attrib['srsDimension'] = "3"
            pList.text = " "        
            coords = [ptdir[t[0]],ptdir[t[1]] ,ptdir[t[2]]]
            poly = Polygon(coords)
            poly = geometry.polygon.orient(poly, 1)
            pList.text = pList.text + str(poly).strip('POLYGON Z ((').strip('))').replace(","," ")

    if modelRun == "lod1":
        lod.text ="1"
        lodTin.text ="1"
        genValue1.text = str(len(tri['triangles']))
        
        for t in tri['triangles']: 
            triangle = etree.SubElement(triPatches, "{%s}Triangle" % ns_gml)
            exterior = etree.SubElement(triangle, "{%s}exterior" % ns_gml)
            linRing = etree.SubElement(exterior, "{%s}LinearRing" % ns_gml)
            linRing.attrib['{%s}id' % ns_gml] = "GML_"+str(uuid.uuid4())
            pList = etree.SubElement(linRing, "{%s}posList" % ns_gml)
            pList.attrib['srsDimension'] = "3"
            pList.text = " "        
            coords = [ptdir[t[0]],ptdir[t[1]] ,ptdir[t[2]]]
            poly = Polygon(coords)
            poly = geometry.polygon.orient(poly, 1)
            pList.text = pList.text + str(poly).strip('POLYGON Z ((').strip('))').replace(","," ")
        for face in facelist:
            for ff in face:
                triangle = etree.SubElement(triPatches, "{%s}Triangle" % ns_gml)
                exterior = etree.SubElement(triangle, "{%s}exterior" % ns_gml)
                linRing = etree.SubElement(exterior, "{%s}LinearRing" % ns_gml)
                linRing.attrib['{%s}id' % ns_gml] = "GML_"+str(uuid.uuid4())
                genValue2.text = genValue2.text + " " + linRing.attrib['{%s}id' % ns_gml]
                pList = etree.SubElement(linRing, "{%s}posList" % ns_gml)
                pList.attrib['srsDimension'] = "3"
                pList.text = " "        
                pList.text = pList.text + str(ff).strip('POLYGON Z ((').strip('))').replace(","," ")  
    
    if modelRun == "lod2":
        lod.text ="2"
        lodTin.text ="2"
        genValue1.text = str(len(tri['triangles']))
        
        for t in tri['triangles']: 
            triangle = etree.SubElement(triPatches, "{%s}Triangle" % ns_gml)
            exterior = etree.SubElement(triangle, "{%s}exterior" % ns_gml)
            linRing = etree.SubElement(exterior, "{%s}LinearRing" % ns_gml)
            linRing.attrib['{%s}id' % ns_gml] = "GML_"+str(uuid.uuid4())
            pList = etree.SubElement(linRing, "{%s}posList" % ns_gml)
            pList.attrib['srsDimension'] = "3"
            pList.text = " "        
            coords = [ptdir[t[0]],ptdir[t[1]] ,ptdir[t[2]]]
            poly = Polygon(coords)
            poly = geometry.polygon.orient(poly, 1)
            pList.text = pList.text + str(poly).strip('POLYGON Z ((').strip('))').replace(","," ")
        
#        fc = 0    
        for face in facelist:
            for ff in face:
                triangle = etree.SubElement(triPatches, "{%s}Triangle" % ns_gml)
                exterior = etree.SubElement(triangle, "{%s}exterior" % ns_gml)
                linRing = etree.SubElement(exterior, "{%s}LinearRing" % ns_gml)
                linRing.attrib['{%s}id' % ns_gml] = "GML_"+str(uuid.uuid4()) #facetrianglesID[fc]
#                fc =fc + 1
                pList = etree.SubElement(linRing, "{%s}posList" % ns_gml)
                pList.attrib['srsDimension'] = "3"
                pList.text = " "        
                pList.text = pList.text + str(ff).strip('POLYGON Z ((').strip('))').replace(","," ")  
    
    if modelRun == "lod3":
        lod.text ="3"
        lodTin.text ="3" 
        genValue1.text = str(len(tri['triangles']))
        for t in tri['triangles']: 
            triangle = etree.SubElement(triPatches, "{%s}Triangle" % ns_gml)
            exterior = etree.SubElement(triangle, "{%s}exterior" % ns_gml)
            linRing = etree.SubElement(exterior, "{%s}LinearRing" % ns_gml)
            linRing.attrib['{%s}id' % ns_gml] = "GML_"+str(uuid.uuid4())
            pList = etree.SubElement(linRing, "{%s}posList" % ns_gml)
            pList.attrib['srsDimension'] = "3"
            pList.text = " "        
            coords = [ptdir[t[0]],ptdir[t[1]] ,ptdir[t[2]]]
            poly = Polygon(coords)
            poly = geometry.polygon.orient(poly, 1)
            pList.text = pList.text + str(poly).strip('POLYGON Z ((').strip('))').replace(","," ")
        
#        fc = 0
        for face in facelist:
            for ff in face:
                triangle = etree.SubElement(triPatches, "{%s}Triangle" % ns_gml)
                exterior = etree.SubElement(triangle, "{%s}exterior" % ns_gml)
                linRing = etree.SubElement(exterior, "{%s}LinearRing" % ns_gml)
                linRing.attrib['{%s}id' % ns_gml] = "GML_"+str(uuid.uuid4()) #facetrianglesID[fc]
#                fc =fc + 1
                genValue2.text = genValue2.text + " " + linRing.attrib['{%s}id' % ns_gml]
                pList = etree.SubElement(linRing, "{%s}posList" % ns_gml)
                pList.attrib['srsDimension'] = "3"
                pList.text = " "        
                pList.text = pList.text + str(ff).strip('POLYGON Z ((').strip('))').replace(","," ")  
    
    citygml = etree.tostring(cityModel, pretty_print=True, encoding="UTF-8")
    wf=open(fname,'wb')
    wf.write(b"<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
    wf.write(citygml)
    wf.close() 

# ----- start of program -------             

# Parse cmd arguments
print ("\n ***** Random 3D TIN Terrain Generator *****\n")
PARSER = argparse.ArgumentParser(description='Random Terrain Generator (with vertical walls, overhangs, and integrated Buildings)')
PARSER.add_argument('-n', '--number', help='Number of points to create the TIN', required=False)
PARSER.add_argument('-o', '--filename', help='Output CityGML Filename (*.gml)', required=False)
PARSER.add_argument('-t0', '--terrainLOD0', help='Generate an LOD0 strict 2.5D terrain model without integrated objects', required=False)
PARSER.add_argument('-t1', '--terrainLOD1', help='Generate an LOD1 2.5+D/2.75D terrain model without integrated objects', required=False)
PARSER.add_argument('-t2', '--terrainLOD2', help='Generate an LOD2 strict 2.5D constrained terrain model with integrated objects', required=False)
PARSER.add_argument('-t3', '--terrainLOD3', help='Generate an LOD3 2.5+D/2.75D constrained terrain model with integrated objects', required=False)

ARGS = vars(PARSER.parse_args())
NUMBEROFPOINTS = ARGS['number']
FILENAME = ARGS['filename']
TERRAINLOD0 = argRead(ARGS['terrainLOD0']) #terrain 2.5D
TERRAINLOD1 = argRead(ARGS['terrainLOD1']) #terrain 2.5+D/2.75D
TERRAINLOD2 = argRead(ARGS['terrainLOD2']) #constrained terrain 2.5D with integrated city objects
TERRAINLOD3 = argRead(ARGS['terrainLOD3']) #constrained terrain 2.5+D/2.75D with integrated city objects

# Number of points in a TIN, user defined
if NUMBEROFPOINTS:
    npoints = int(NUMBEROFPOINTS)
else:
    npoints = 50

# Size of polygon
side = 100

# Bounding box
lowerBound = [155000, 463000, 0]
upperBound = [159000, 467000, 40]

# Output file
if FILENAME:
    fname = str(FILENAME)
else:
    fname = r"terrain.gml"

# CityModel
cityModel = etree.Element("CityModel", nsmap=nsmap)
cityModel.attrib['{%s}schemaLocation' %ns_xsi] = "http://www.opengis.net/citygml/relief/2.0 \
    http://schemas.opengis.net/citygml/relief/2.0/relief.xsd \
    http://www.opengis.net/citygml/building/2.0 \
    http://schemas.opengis.net/citygml/building/2.0/building.xsd \
    http://www.opengis.net/citygml/generics/2.0 \
    http://schemas.opengis.net/citygml/generics/2.0/generics.xsd"
boundedBy = etree.SubElement(cityModel, "{%s}boundedBy" % ns_gml)
envelope = etree.SubElement(boundedBy, "{%s}Envelope" % ns_gml)
envelope.attrib['srsDimension'] = "3"
envelope.attrib['srsName'] = "EPSG:28992"
lBound = etree.SubElement(envelope, "{%s}lowerCorner" % ns_gml)
lBound.text = str(lowerBound[0]) + " " + str(lowerBound[1]) + " " + str(lowerBound[2])
hBound = etree.SubElement(envelope, "{%s}upperCorner" % ns_gml)
hBound.text = str(upperBound[0]) + " " + str(upperBound[1]) + " " + str(upperBound[2])

if TERRAINLOD0:
    print ("Generating an LOD0 strict 2.5D terrain model without integrated objects")
    print ("Format: CityGML")
    print ("LOD: 0")
    print ("Feature: Terrain/Relief")
    terrainLOD0(fname, npoints, lowerBound, upperBound, cityModel)
    
elif TERRAINLOD1:
    print ("Generating an (2.5+D/2.75D) LOD1 terrain model with vertical walls")
    print ("Format: CityGML")
    print ("LOD: 1")
    print ("Feature: Terrain/Relief")
    terrainLOD1_2_3(fname, npoints, lowerBound, upperBound, cityModel,"lod1")
    
elif TERRAINLOD2:
    print ("Generating an LOD2 strict 2.5D constrained terrain model with integrated cityobjects")
    print ("Format: CityGML")
    print ("LOD: 2")
    print ("Feature: Terrain/Relief")
    terrainLOD1_2_3(fname, npoints, lowerBound, upperBound, cityModel,"lod2")

elif TERRAINLOD3:
    print ("Generating an LOD3 (2.5+D/2.75D) constrained terrain model with integrated city objects")
    print ("Format: CityGML")
    print ("LOD: 3")
    print ("Feature: Terrain/Relief")
    terrainLOD1_2_3(fname, npoints, lowerBound, upperBound, cityModel,"lod3")