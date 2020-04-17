# 获取URL数据（北京地铁数据）：http://map.amap.com/service/subway?_1469083453978&srhdata=1100_drw_beijing.json
import requests
import re
import numpy as np

r = requests.get('http://map.amap.com/service/subway?_1469083453978&srhdata=1100_drw_beijing.json')

#获得每个地点和他的位置：
#{站点名称:(经度,纬度)}
places=re.findall('"n":"\w+"',r.text)
lat_lon=re.findall('"sl":"(\d+\.\d+,\d+\.\d+)"',r.text)
stations_info={}
for i in range(len(places)):
    place_name=re.findall('"n":"(\w+)"',places[i])[0]
    stations_info[place_name]=tuple(map(float,lat_lon[i].split(',')))

#获取{线路名称：站点名称}
kn=re.findall('"n":"(\w+)"|"kn":"(\w+)"',r.text)
kn.reverse()
lines_info={}
for i in kn:
    if i[0]=='':
        tem_key=i[1]
        lines_info[tem_key]=[]
    else:
        lines_info[tem_key]=lines_info[tem_key]+[i[0]]

#建立邻接链表dict   
neighbor_info={}
for i in lines_info:
    neighbor_info[i]=[]
    for j in range(len(lines_info[i])-1):
        neighbor_info[i]=neighbor_info[i]+\
                        [(lines_info[i][j],lines_info[i][j+1])]

import networkx as nx
import matplotlib.pyplot as plt
from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['SimHei'] # 指定默认字体
plt.figure(figsize=(30,30))
city_graph=nx.Graph()  #新建图类实例
city_graph.add_nodes_from(list(stations_info.keys())) #添加点

nx.draw_networkx_nodes(city_graph,stations_info,node_size=20,node_color='red')#绘制点，nodelist默认为G中的所有节点
nx.draw_networkx_labels(city_graph,stations_info,font_size=7)
col_list=['#b45b1f','#1fb4a6','#1f2db4','#b4a61f','#78b41f','#b41f78','#b41f78','#a61fb4','#b45b1f','#2db41f','#5b1fb4','#78b41f',\
'#b45b1f','#1fb4a6','#1f2db4','#b4a61f','#78b41f','#2aa930','#b41f78','#a61fb4','#b45b1f','#2db41f','#5b1fb4','#78b41f']
for i,index in enumerate(neighbor_info):
    nx.draw_networkx_edges(city_graph,stations_info,edgelist=neighbor_info[index],width=1.5,edge_color=col_list[i])
plt.show()

#起始点到目的地，BFS路径搜索
def get_path_BFS(lines_info, neighbor_info, from_station, to_station):
    a=False
    b=False
    for i in lines_info:
        if from_station in lines_info[i]:
            a=True
        if to_station in lines_info[i]:
            b=True
    if not (a and b):
        return print('从{}到{}的路径输入错误，无法查询！'.format(from_station, to_station))

    pathes=[[from_station]]    #用于存放所有扩展出的分支
    visited=set()  #存放已经扩展完全的端点
    while pathes:
        path=pathes.pop(0)  #选取所有的已扩展的树枝中选择第一个树枝，用于下面的扩展
        froniter=path[-1]   #选择一个小树枝的待扩展末端，准备扩展出与该末端相连的城市
        if froniter in visited: #避免扩展完全的端点再次进入扩展
            continue
        #提取与froniter相连接的城市
        successsors=[]
        for i in neighbor_info:
            for j in neighbor_info[i]:
                if froniter in j:
                    successsors=successsors+[jj for jj in j if not jj==froniter ]
        for city in successsors:   #遍历城市与froniter相连的城市
            if city in path:   #避免往回找
                continue
            new_path=path+[city] #从跟节点到city的小分支

            pathes.append(new_path)  #把从根节点到每层节点的单个小分支进行存储
            if city==to_station:
                return print('从{}到{}的路线为：'.format(from_station, to_station),'\n',
                    ('{}--->'*(len(new_path)-1)+'{}').format(*new_path[:-1],new_path[-1]))  #返回符合要求的小分支
        visited.add(froniter)    #存放已经扩展完全的端点

get_path_BFS(lines_info,neighbor_info,'南单','南锣鼓巷')
get_path_BFS(lines_info,neighbor_info,'西单','南锣鼓巷')
get_path_BFS(lines_info,neighbor_info,'北京南站','大兴机场')
