# coding=utf-8

"""
# 对osm文件的排版要求：
    1. node 数据块
    2. way　数据块
    3. relation　数据块
＃　
"""

import xml.sax
import visu
import dealfile
import pprint
from findata import findwayData



"""
# osmHandler 是封装sax技术读osm文件的接口
# osmHandler 目前是为了收集osm中的relation数据，并用于vtk显示
# osmHandler 维护了三个集合：
    1. nodes: 这是一个字典，包含了当前文件所有的点 (   {id:[x, y] ...}  )
    2. dicOfways: 这是一个字典，包含了当前文件所有way元素的引用的点(   {id:[nodes-id] ...}  ）
    3. dicOfRelations: 这是一个字典，包含了当前文件所有的relations引用的元素(  {id:[members-id ], ....}  )
# 由于relation的成员member并不在同一文件中，所以还无法实现relations的数据收集！！！！！！！！！！！！！
"""
class osmHandler(xml.sax.ContentHandler):

    def __init__(self, name="building"):
        self.objectName = name
        self.nodes = {}               # 当前osm文件中所有点的集合（id标识）
        self.parentTag = ''           # 用于保存当前元素的父元素Tag
        self.parentId = ''            # 用于保存当前元素父元素的Id
        self.features_wayNodes = []   # 用于临时存储某一way元素引用的点
        self.bdSets = []              # 用于存储所有building各自对应的点,事实上，它是features_wayNodes的集合
        self.noTypebdSets = []        # 将所有同一类型设施的“描绘点组集”放到一起，不按设施个体区分
        self.gotObject = False        # 指示有没有找到指定目标的数据
        self.dicOfWays = {}           # 储存所有way元素对应的“描绘点组集”的字典　（way-id : 点组集）
        self.dicOfRelations = {}      # 储存所有relation元素对应的 “描绘点组集”的字典　（relation-id : 点组集）
        self.rlnodes = []


    """
    # nodetrans 用于将osm中某一node映射到点云坐标系中的node
    # nd = [lon, lat]
    """
    def nodetrans(self, nd):
        return dealfile.getXY(nd)


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
    # parseWays 用于解析osm文件中某一way元素，得到它所引用的点的集合
    # mlist是储存某一way引用的node-id的列表，事实上mlist = [id0, id1, id2 ...]
    """
    def parseWays(self, mlist):             # 元素是　id形式
        tmpwaynodes = []
        for p in mlist:
            tmpwaynodes.append(self.nodes[p])
        return self.nodeAssembly(tmpwaynodes)
        pass


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
                    linknodes.append(self.nodes[p[1]])
                    nodetag = True
                if 'way' == p[0]:
                    if True == nodetag:
                        tmpnode.extend(self.nodeAssembly(linknodes))
                        nodetag = False
                        linknodes = []
                    tmpnode.extend(self.parseWays(self.dicOfWays[p[1]]))
                if 'relation' == p[0]:
                    if True == nodetag:
                        tmpnode.extend(self.nodeAssembly(linknodes))
                        nodetag = False
                        linknodes = []
                    tmpnode.extend(self.parseRelations(self.dicOfRelations[p[1]]))
            except KeyError, e:
                pass
                # print "not found key %s in dicOfWays! \n" % p[1]
                # if not findwayData(p[1]):
                #     flag = True
        return tmpnode  #, flag



    """
     # 元素开始事件处理
    """
    def startElement(self, tag, attributes):
        if tag == 'node':
            x = float(attributes['lon'])
            y = float(attributes['lat'])
            self.nodes[attributes["id"]] = [x, y]
        elif 'way' == tag:
            self.dicOfWays[attributes['id']] = []  # 将当前way元素id加入字典中
            self.parentId = attributes['id']
            self.parentTag = tag
        elif 'way' == self.parentTag:  # 当前进入了way元素的子元素
            if 'nd' == tag:            # 进入nd子元素　收集当前way对应建筑或设施的点信息
                self.features_wayNodes.append(attributes['ref'])   # 这里还是以node-id为元素，因为relation中也可能包含node
        elif 'relation' == tag:
            self.dicOfRelations[attributes['id']] = []
            self.parentTag = 'relation'
            self.parentId = attributes['id']
        elif 'relation' == self.parentTag:
            if 'member' == tag:
                self.features_wayNodes.append([attributes['type'], attributes['ref']])
            pass

    """
    # 元素结束事件处理
    """
    def endElement(self, tag):
        # if 'way' == tag:
        if self.parentTag == tag:       # 不管parentTag是way,还是relation
            if 'way' == tag:
                self.dicOfWays[self.parentId] = self.features_wayNodes
            if 'relation' == tag:
                self.dicOfRelations[self.parentId] = self.features_wayNodes
                # self.parseRelations()
                pass
            self.features_wayNodes = []
            self.parentTag = ''
            self.parentId = ''



    # 内容事件处理
    def characters(self, content):
        pass

    def endDocument(self):
        # pprint.pprint(self.dicOfRelations)
        # pprint.pprint(self.dicOfWays)
        # pprint.pprint(self.)
        if len(self.noTypebdSets) > 0:
            self.gotObject = True


    def osmReadWay(self):
        pass

    def osmReadRelation(self):
        pass


def osmSaxReader(path, features):
    parser = xml.sax.make_parser()      # 创建一个 XMLReader
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)    # turn off namepsaces  ??????
    Handler = osmHandler(features)      # 重写 ContextHandler
    parser.setContentHandler(Handler)
    parser.parse(path)

    for p in Handler.dicOfRelations.itervalues():  # 这里要学习迭代遍历dic的方法
        tmplist = Handler.parseRelations(p)
        # pprint.pprint(tmplist)
        # assemList = Handler.nodeAssembly(tmplist)  # 装配“描绘点集”
        # if res:
        #     print "not all member found!"
        # else:
        #     print "Find all members!"
        actor = visu.getlsactor(tmplist)
        visu.showact(actor)

    # if Handler.gotObject:
    #     actor = visu.getlsactor(Handler.noTypebdSets)
    #     visu.showact(actor)
    #     # for b in Handler.bdSets:
    #     #     actor = visu.getlsactor(b)
    #     #     visu.showact2(actor)
    # else:
    #     print "未找到目标设施数据"
    pass


if __name__ == "__main__":
    path = "../../lidar_osm/map.osm"
    features = 'highway'
    osmSaxReader(path, features)
    pass
