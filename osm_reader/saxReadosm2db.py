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
from osmdboperation import *
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
        # self.rlnodes = []
        self.wayeps = ''             # 记录每一个way的tag信息,即描述信息
        self.TypeDic = ["building", "highway", "Waterway"]






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




    def startDocument(self):
        pass


    """
     # 元素开始事件处理
    """
    def startElement(self, tag, attributes):
        if 'node' == tag:
            x = attributes['lon']
            y = attributes['lat']
            self.nodes[attributes["id"]] = [x, y]
        elif 'way' == tag:
            self.dicOfWays[attributes['id']] = []  # 将当前way元素id加入字典中
            self.parentId = attributes['id']
            self.parentTag = tag
        elif 'way' == self.parentTag:  # 当前进入了way元素的子元素
            if 'nd' == tag:            # 进入nd子元素　收集当前way对应建筑或设施的点信息
                self.features_wayNodes.extend(self.nodes[attributes['ref']])   # 这里还是以node-id为元素，因为relation中也可能包含node
            if 'tag' == tag:           # 收集每个way的描述信息
                # if attributes['k'] in self.TypeDic:
                self.wayeps += ('(k='+attributes['k']+' v='+attributes['v']+') ')  # way的每个tag 由括号和空格分开

        elif 'relation' == tag:
            self.dicOfRelations[attributes['id']] = []
            self.parentTag = 'relation'
            self.parentId = attributes['id']
        elif 'relation' == self.parentTag:
            if 'member' == tag:
                self.features_wayNodes.extend([attributes['type'], attributes['ref']])
            if 'tag' == tag:           # 收集每个relation的描述信息
                # if attributes['k'] in self.TypeDic:
                self.wayeps += ('(k='+attributes['k']+' v='+attributes['v']+'),')  # way的每个tag 由括号和空格分开
            pass

    """
    # 元素结束事件处理
    """
    def endElement(self, tag):
        # if 'way' == tag:
        if self.parentTag == tag:       # 不管parentTag是way,还是relation
            if 'way' == tag:
                self.dicOfWays[self.parentId] = [self.features_wayNodes, self.wayeps]
            if 'relation' == tag:
                self.dicOfRelations[self.parentId] = [self.features_wayNodes, self.wayeps]
                # self.parseRelations()
                pass
            self.features_wayNodes = []
            self.parentTag = ''
            self.parentId = ''
            self.wayeps = ''


    # 内容事件处理
    def characters(self, content):
        pass

    def endDocument(self):
        if len(self.noTypebdSets) > 0:
            self.gotObject = True

        dblocation = "osmdb.db"
        self.db = osmdbOperation(dblocation)
        self.db.createOsmTable()    # 创建表格d
        # pprint.pprint(self.nodes)
        self.db.InsertNodes(self.nodes)  # 将nodes集合插入数据库表
        # pprint.pprint(self.dicOfWays)
        self.db.Insertways(self.dicOfWays)
        self.db.InsertRelations(self.dicOfRelations)
        self.db.dbclose()   # 关闭数据库




def osmSaxReader(path, features):
    parser = xml.sax.make_parser()      # 创建一个 XMLReader
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)    # turn off namepsaces  ??????
    Handler = osmHandler(features)      # 重写 ContextHandler
    parser.setContentHandler(Handler)
    parser.parse(path)
    #
    # for p in Handler.dicOfRelations.itervalues():  # 这里要学习迭代遍历dic的方法
    #     tmplist = Handler.parseRelations(p)
    #     actor = visu.getlsactor(tmplist)
    #     visu.showact(actor)

    pass


if __name__ == "__main__":
    path = "../../lidar_osm/t2.osm"
    features = 'highway'
    osmSaxReader(path, features)
    pass
