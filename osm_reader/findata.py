# coding=utf-8

import os
import pprint


def findwayData(id):
    path = "../../lidar_osm"
    fs = os.listdir(path)
    for fn in fs:
        if fn[-3:] == 'osm' and fn[0:2] != 't2':
            fa = os.path.join(path, fn)
            f = open(fa)
            # pprint.pprint(f)
            res = unicode(f.read(), 'utf-8')
            # pprint.pprint(res[-1:])
            if id in res:
                return fa
    return None


if __name__ == '__main__':
    res = findwayData(raw_input())
    if res:
        print res
    else:
        print "未找到！"
