# coding=utf-8
__author__ = 'wlw'

import sys
sys.path.append('.')
import os
import visu

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from shapely.geometry import Point
from functools import partial
import pyproj
from shapely.ops import transform

def getpoints(fa,dd=1):
    f=open(fa)
    #print 'read'
    dx = 0.0
    dy = 0.0
    ps = []
    xll = 0.0
    yll = 0.0
    csz = 0.5
    t = 0
    while True:
        ff=f.readline()

        if ff:
            if len(ff)<100:
                print ff
                if ff.startswith('xllcorner'):
                    xll= float(ff.split('xllcorner')[1])
                if ff.startswith('yllcorner'):
                    yll= float(ff.split('yllcorner')[1])
                if ff.startswith('cellsize'):
                    csz= float(ff.split('cellsize')[1])

            elif t<dd:
                t+=1
            else:
                #print 'line',len(ff)
                t=0
                n = ff.split(' ')
                #print len(n)
                dy+=csz*dd
                dx = 0.0
                for i in range(2000/dd):
                    if n[i*dd+1]!='-9999':

                        z=float(n[i*dd+1])
                        ps.append([dx+xll,1000-dy+yll,z*2])
                        dx+=csz*dd
                #print n

        else:
            break
    f.close()
    print len(ps)
    #visu(ps[:60000])
    #print ps[:1]
    return ps
    #return visu.getpsactor(ps[:160000])
    pass

def getASC(path):
    fs = os.listdir(path)
    ps = []
    k = 1000
    i = 0
    for f in fs:
        fa = os.path.join(path,f)
        #print fa[:-3]
        if fa[-3:]=='asc':
            #print 'ss',fa

            if i<k:
                ps.extend(getpoints(fa,16*2))
            i+=1
        print fa
        #break
    #print len(ps)
    #visu.visups(ps)
    return visu.getpsactor(ps)
    pass


def trans(p):
    point1 = Point(p[:2])  # 获取lat\lon
    # print(point1)

    project = partial(
        pyproj.transform,
        pyproj.Proj(init='epsg:4326'),
        pyproj.Proj(init='epsg:27700')
    )
    point2 = transform(project, point1)  # 将经纬度转换成地图坐标
    # print (point2.x)
    res = [point2.x, point2.y]
    res.extend(p[2:])
    return res

# def trans(p):
#     point1 = Point(p[:2])  # 获取lat\lon
#     point2 = Point(0, 0)
#     # print(point1)
#
#     project = partial(
#         pyproj.transform,
#         pyproj.Proj(init='epsg:4326'),
#         pyproj.Proj(init='epsg:27700')
#     )
#     try:
#         point2 = transform(project, point1)  # 将经纬度转换成地图坐标
#     except:
#         print point1
#     # print (point2.x)
#     res = [point2.x, point2.y]
#     res.extend(p[2:])
#     return res

def untrans(p):
    point1 = Point(p[:2])

    # print (point1)

    project = partial(
        pyproj.transform,
        pyproj.Proj(init='epsg:27700'),
        pyproj.Proj(init='epsg:4326'))

    point2 = transform(project, point1)
    # print (point2.x)
    res = [point2.x, point2.y]
    res.extend(p[2:])
    return res


def getXY(ox, f=0):
    # print ox
    dx = 12698962.99
    dy = 3750817.06
    res = [ox[0], ox[1], 0]
    # print res
    if f == 0:
        rr = trans(res)  # 将经纬度转换成地图坐标
    else:
        rr = untrans(res)
    return [rr[0], rr[1], rr[2]]

def drawOSM(input):

    tree = ET.parse(input)
    root = tree.getroot()
    print root.tag

    latlon = []
    elenum = {}
    nodes = {}
    ps = []
    for ch in root:
        if ch.tag in elenum:
            elenum[ch.tag] += 1
        else:
            elenum[ch.tag] = 0

        if ch.tag == 'node':
            lat = float(ch.attrib['lat'])

            lon = float(ch.attrib['lon'])
            latlon.append([lon,lat])
            nodes[ch.attrib['id']] = [lon, lat]


    ls = []
    for ch in root:
        if ch.tag == 'node':
            x = float(ch.attrib['lat'])
            y = float(ch.attrib['lon'])
            ps.append([x, y, 0])
        if ch.tag == 'way':
            lines = []
            for nd in ch:
                if nd.tag == 'nd':
                    lines.append(nodes[nd.attrib['ref']])

            for i in range(len(lines)-1):
                # print len(lines),lines[i][0]*100000
                c0 = getXY(lines[i])
                c1 = getXY(lines[i+1])
                # x2,y2 = getXY(lines[i+1][0],lines[i+1][1])
                l = [c0, c1]
                ls.append(l)
                pass
                # draw.line((x1,y1, x2,y2), fill=128)



    #im.show()
    #im.save(out)

    print len(ls), ls[:10]
    #visulines(ls[:20])
    #print nodes
    print elenum
    return visu.getlsactor(ls)


if __name__ == '__main__':
    print 'ss'
    path = "../../lidar_asc/TQ37"
    a1 = getASC(path)
    gl = '/home/wlw/K40/osm/greater-london-latest.osm'
    a2 = drawOSM('../lidar/t2.osm')
    a3 = drawOSM('../lidar/t3.osm')
    a4 = drawOSM('../lidar/t5.osm')
    a6 = drawOSM('../lidar/t6.osm')
    a7 = drawOSM('../lidar/t7.osm')
    a8 = drawOSM('../lidar/t8.osm')
    a9 = drawOSM('../lidar/t9.osm')
    #a3 = drawOSM(gl)
    visu.showact([a1, a6, a7, a8, a9])
