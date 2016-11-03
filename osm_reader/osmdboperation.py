# coding=utf-8

import sqlite3
import pprint
import dealfile
import string


class osmdbOperation():


    def __init__(self, path="./osmdb.db"):
        self.path = path
        self.conn = sqlite3.connect(self.path)
        self.curs = self.conn.cursor()
        pass

    def dbclose(self):      # 判断self.conn不为空！！！！！！！！！！！
        self.conn.close()


    """
    # 创建osm数据库
    #   1. nodes用于存储osm的点集
    #   2. ways用于存储osm中所有way的集合
            [1] ref包含该way引用的所有点的id　用空格分开
            [2] tags 包含该ways的所有tag的信息，tag之间用空格分开
    #   3. relations 用于存储osm中所有relation的信息　
            其中ref　包含该relation引用的所有member的Type和id，用空格分开　读取时应两两一起读
    #   4. 以上三者的共同属性（暂时用不上,没有加入到表中）：
          # visible   TEXT,
          # version   TEXT,
          # changeset TEXT,
          # timestamp TEXT,
          # user      TEXT,
          # uid       TEXT,
    """
    def createnodestable(self):
        self.curs.execute("""
            CREATE TABLE IF NOT EXISTS nodes(
                  id        TEXT        PRIMARY KEY  NOT NULL,
                  lon       TEXT,
                  lat       TEXT
                )
            """)


    def createwaystable(self):
        self.curs.execute("""
             CREATE TABLE IF NOT EXISTS ways(
                  id        TEXT        PRIMARY KEY  NOT NULL,
                  ref       TEXT,
                  tags      TEXT
                )
            """)



    def createrelations(self):
        self.curs.execute("""
            CREATE TABLE IF NOT EXISTS relations(
                  id        TEXT        PRIMARY KEY  NOT NULL,
                  ref       TEXT,
                  tags      TEXT
                )
            """)

    def createOsmTable(self):
        # 用于访问所有的表的名称
        # query = 'select name from sqlite_master where type="table" order by name'
        # namelist = self.curs.execute(query).fetchall()
        # tmp = []
        # for p in namelist:
        #     tmp.extend(list(p))
        self.createnodestable()
        self.createwaystable()
        self.createrelations()
        self.conn.commit()


    def Istablecreated(self, tablename=None):
        query = 'SELECT name FROM sqlite_master WHERE type = "table" AND name = "%s"' % tablename
        return len(self.curs.execute(query).fetchall())
        pass

    """
    # InsertNodes向数据库的nodes表中插入node集合nodedic，
    # nodedic的结构为[id:[lon,lat], id:[lon,lat], ...]
    """
    def InsertNodes(self, nodedic):
        if self.Istablecreated('nodes'):
            data = []
            for k, v in nodedic.iteritems():
                data.append([k, v[0], v[1]])
            query = "INSERT OR IGNORE INTO nodes VALUES(?,?,?)"
            self.curs.executemany(query, data)
            self.conn.commit()
        else:
            print "nodes表格不存在！"
        pass



    """
    # waysdic的结构是[id:[ref tags],id:[ref tags].... ]
    # ref的结构是 ref == 'x0 y0 x1 y1 .... '(字符串最后有空格)
    # tags == '(k=keytype v=value) (k=keytype v=value)'
    """
    def Insertways(self, waysdic):
        if self.Istablecreated('ways'):
            data = []
            for k, v in waysdic.iteritems():
                strtmp = string.join(v[0], ' ')
                data.append([k, strtmp, v[1]])
            query = "INSERT OR IGNORE INTO ways VALUES(?,?,?)"
            self.curs.executemany(query, data)
            self.conn.commit()
        else:
            print "ways表格不存在！"
        pass



    """
    # rtdic的结构是[id:ref,id:ref.... ]
    # ref == 'type id type id ....'
    # tags == '(k=keytype v=value) (k=keytype v=value)'
    """
    def InsertRelations(self, rtdic):
        if self.Istablecreated('relations'):
            data = []
            for k, v in rtdic.iteritems():
                reftmp = ' '.join(v[0])
                data.append([k, reftmp, v[1]])
            query = "INSERT OR IGNORE INTO relations VALUES(?,?,?)"
            self.curs.executemany(query, data)
            self.conn.commit()
        else:
             print "relations表格不存在！"
        pass



    """
    #
    """
    def Readnodesfromdb(self, ID):
        if self.Istablecreated('nodes'):
            query = 'SELECT lon,lat from nodes WHERE id = %s' % ID
            point = self.curs.execute(query).fetchone()
            if point is not None:
                self.conn.commit()
                point = [float(point[0]), float(point[1])]
                # pprint.pprint(point)
                return point
            else:
                print "没有找到指定node！"
                return None
        else:
            print "nodes表格不存在,读取失败！"
        pass




    """
    #
    """

    def Readwaysfromdb(self, ID):
        if self.Istablecreated('ways'):
            query = 'SELECT ref FROM ways WHERE id = %s' % ID
            self.curs.execute(query)
            tmplist = self.curs.fetchone()
            tmp = []
            if tmplist is not None:
                tmplist = tmplist[0].split(' ')
                i = 0
                while(i < (len(tmplist)-2)):
                    point0 = [float(tmplist[i]), float(tmplist[i+1])]
                    point1 = [float(tmplist[i+2]), float(tmplist[i+3])]
                    point0 = dealfile.getXY(point0)
                    point1 = dealfile.getXY(point1)
                    tmp.append([point0, point1])
                    i += 2
            else:
                print "未找到指定way数据"
            return tmp
        else:
            print "ways表格未创建,读取错误！"
            return None

    """
    # nodetrans 用于将osm中某一node映射到点云坐标系中的node
    # nd = [lon, lat]
    """
    def nodetrans(self, nd):
        if nd is not None:
            return dealfile.getXY(nd)
        return []


    """
    # nodeAssembly 用于将某一list中的点组装起来，即相邻两点为一组，构成 "描绘点组集"
    # ndlist 是一个包含osm点的列表， 事实上mlist = [ [x,y], [x,y] ,[x,y] ....]
    # ndlist 中的点都是已经转换过的点
    """
    def nodeAssembly(self, ndlist):
        tmplist = []
        y = len(ndlist)
        if y > 0:
            c0 = self.nodetrans(ndlist[0])
            for i in range(y - 1):
                c1 = self.nodetrans(ndlist[i+1])
                tmplist.append([c0, c1])
                c0 = c1
        return tmplist

    """
    # parseRelation 用于解析osm文件的relation元素，得到它所引用的点的集合
    # mlist是需要解析的某一relation所引用的member列表，事实上mlist = [[Type,id], [Type,id] ....]
    # 返回的是该relation所引用的所有member包含的点的集合
    # 并不是所有的member都在一个文件中，所以parseRelation还不能很好的完成工作
    # 另外members之间有没有顺序关系，决定装配的位置：           !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1
        也就是说:应该先装配各个member,还是先求点集，最终一起装配
        1. 如果先装配member ,那么member中包含nodes，怎么办？？？？
        2. 如果同一装配，那么各个members 分界的点之间有没有联系？？？？？？
        3. 由于字典中k-v的顺序不是存储先后的顺序，所以如果members有顺序，使用字典会破坏这些
    """
    def parseRelations(self, mlist):        # 元素是[Type, id]形式的
        tmpnode = []
        linknodes = []
        nodetag = False

        for p in mlist:
            try:
                if 'node' == p[0]:
                    tmp = self.Readnodesfromdb(p[1])
                    if tmp: linknodes.append(tmp)
                    nodetag = True
                if 'way' == p[0]:
                    if True == nodetag:
                        tmpnode.extend(self.nodeAssembly(linknodes))
                        nodetag = False
                        linknodes = []
                    tmpnode.extend(self.Readwaysfromdb(p[1]))
                if 'relation' == p[0]:
                    if True == nodetag:
                        tmpnode.extend(self.nodeAssembly(linknodes))
                        nodetag = False
                        linknodes = []
                    tmpnode.extend(self.Readrelationsfromdb(p[1]))
            except KeyError, e:
                pass
                # print "not found key %s in dicOfWays! \n" % p[1]
                # if not findwayData(p[1]):
                #     flag = True
        return tmpnode  #, flag


    """
    #
    """
    def Readrelationsfromdb(self, ID):
        if self.Istablecreated('relations'):
            query = 'SELECT ref FROM relations WHERE id = %s' % ID
            self.curs.execute(query)
            tmplist = self.curs.fetchone()
            tmplist = tmplist[0].split(' ')
            tmplist = zip(*([iter(tmplist)] * 2))  # 压缩器 group_adjacent = lambda a, k: zip(*([iter(a)] * k))
            return self.parseRelations(tmplist)
        else:
            print "relations表格未创建！读取错误！"
            return None
        pass



if __name__ == '__main__':
    # tmplist = [1, 2, 3, 4, 5, 6]
    # tmp = tmplist.append([])
    # print tmplist
    # print [[p,V] for p, V in tmplist ]
    import visu
    handler = osmdbOperation("osmdb.db")
    # tmplist = handler.Readrelationsfromdb("200257")
    # # handler.Readwaysfromdb('28771749')
    # actor = visu.getlsactor(tmplist)
    # visu.showact(actor)
    ID = '200257'
    query = 'SELECT id FROM relations'  #  WHERE id = %s' % ID
    handler.curs.execute(query)
    tmplist = handler.curs.fetchall()
    for p in tmplist:
        try:
            q = handler.Readrelationsfromdb(p)
            actor = visu.getlsactor(q)
            visu.showact(actor)
        except TypeError, e:
            # print e
            continue
    pass

