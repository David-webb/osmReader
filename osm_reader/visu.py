# coding=utf-8
__author__ = 'wlw'

import vtk


def getpsactor(ps):   # ps 是点云映射到Grid的空间坐标
    # create source
    """
    # vtkPointSource用来创建围绕特定中心点，特定直径的和特定数量点集合组成的球体。
    # 默认点是随机分布在球体里面。也可以生产的点只分布在球面上。
    # 基本用法：
    # SetRadius()设置球体半径
    # SetCenter()设置球体中心点
    # SetNumberOfPoints()设置球中的点的个数
    # SetDistributionToUniform()设置点的分布在球体内
    # SetDistributionToShell()设置点分布在球面上。

    """
    src = vtk.vtkPointSource()
    src.SetCenter(0, 0, 0)       # 设置圆心
    src.SetNumberOfPoints(50)    # 设置点的个数
    src.SetRadius(5)             # 设置半径
    src.Update()                 # ???????
    # ps = [[1,1,1],[2,2,2]]
    # print src.GetOutput()
    points = vtk.vtkPoints()
    vertices = vtk.vtkCellArray()  # 创建一个cell对象
    for p in ps:
    # Create the topology of the point (a vertex)
        id = points.InsertNextPoint(p)
        vertices.InsertNextCell(1)  # 将cell的容量增加1
        vertices.InsertCellPoint(id)  # 将 id所指的点插入cell

    # Create a polydata object  # polydata : 多边形数据
    point = vtk.vtkPolyData()

    # vertex ： 顶点  topology：拓扑
    # Set the points and vertices we created as the geometry and topology of the polydata
    point.SetPoints(points)
    point.SetVerts(vertices)
    # mapper
    # mapper = vtk.vtkPolyDataMapper()
    # Visualize
    mapper = vtk.vtkPolyDataMapper()
    if vtk.VTK_MAJOR_VERSION <= 5:
        mapper.SetInput(point)
    else:
        mapper.SetInputData(point)

    # actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    # actor.GetProperty().SetPointSize(2)
    # assign actor to the renderer
    return actor

def getlsactor(ls):
    #
    # import pprint
    # pprint.pprint(ls)
    # Create a vtkPoints object and store the points in it
    points = vtk.vtkPoints()

    for l in ls:
        points.InsertNextPoint(l[0])
        points.InsertNextPoint(l[1])

    # Create a cell array to store the lines in and add the lines to it
    lines = vtk.vtkCellArray()

    for i in range(len(ls)):  # 长度为线段的条数
      line = vtk.vtkLine()
      line.GetPointIds().SetId(0, 2*i)  # ？？？？？？？？？？？
      line.GetPointIds().SetId(1, 2*i+1)
      lines.InsertNextCell(line)


    # Create a polydata to store everything in
    linesPolyData = vtk.vtkPolyData()

    # Add the points to the dataset
    linesPolyData.SetPoints(points)

    # Add the lines to the dataset
    linesPolyData.SetLines(lines)

    # Setup actor and mapper
    mapper = vtk.vtkPolyDataMapper()
    if vtk.VTK_MAJOR_VERSION <= 5:
        mapper.SetInput(linesPolyData)
    else:
        mapper.SetInputData(linesPolyData)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    return actor

def visups(ps):
    showact([getpsactor(ps)])

# renderer 渲染器；描绘器
def showact(actors):
    renderer = vtk.vtkRenderer()
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)
    try:
        for a in actors:
            renderer.AddActor(a)
    except:
        renderer.AddActor(actors)

    renderWindow.Render()
    renderWindowInteractor.Start()

# def showact2(actors):
#     renderer = vtk.vtkRenderer()
#     renderWindow = vtk.vtkRenderWindow()
#     renderWindow.AddRenderer(renderer)
#     renderWindowInteractor = vtk.vtkRenderWindowInteractor()
#     renderWindowInteractor.SetRenderWindow(renderWindow)
#     for a in actors:
#         renderer.AddActor(a)
#     renderer.AddActor(actors)
#
#     renderWindow.Render()
#     renderWindowInteractor.Start()