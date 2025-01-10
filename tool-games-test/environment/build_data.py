import numpy as np
import json
import pygame as pg
from pyGameWorld.viewer import *
from pyGameWorld.world import *

def build_data(file, objects):
    for data in file['world']['objects']:
        item = {}

        if data == 'Strut':
            item["item"] = list2array(0, file['world']['objects'][data]['vertices'], 0)
            item["label"] = 1
        elif data == 'Cradle':
            item["item"] = list2array(0, file['world']['objects'][data]['vertices'], 0)
            item["label"] = 1
        elif data == 'Goal':
            item["item"] = list2array(4, file['world']['objects'][data]['points'], 0)
            item["label"] = 0
        elif data == 'Catapult':
            item["item"] = list2array(2, file['world']['objects'][data]['polys'], 0)
            item["label"] = 1
        elif data == 'Ball':
            item["item"] = list2array(3, [file['world']['objects'][data]['position'][0], file['world']['objects'][data]['position'][1], file['world']['objects'][data]['radius']], 1)
            item["label"] = 0
        elif data == "_LeftWall" or data == "_RightWall" or data == "_TopWall" or data == "_BottomWall":
            info = list2array(0, file['world']['objects'][data]['vertices'], 0)
            item["item"] = info
            item["label"] = 0
        elif data == 'BridgeL' or data == 'BridgeR':
            info = list2array(0, file['world']['objects'][data]['vertices'], 1)
            item["item"] = info
            item["label"] = 1
        elif data == 'LeftWall1' or data == 'LeftWall2' or data == 'RightWall1':
            info = list2array(0, file['world']['objects'][data]['vertices'], 0)
            item["item"] = info
            item["label"] = 1
        elif data == 'RightWall2':
            info = list2array(1, file['world']['objects'][data]['vertices'], 0)
            item["item"] = info
            item["label"] = 1
        else:
            continue
        item["object"] = data
        
        objects.append(item)
    return objects

def list2array(classtype, vertices, dynamictype):
    # 0: 矩形 1：梯形 2：compound 3:球 4: Goal
    if classtype == 0:
        # 返回形状类型，中心点坐标，长，宽，动态类型，标签
        return np.array([0, (vertices[0][0] + vertices[2][0])/2, (vertices[0][1] + vertices[2][1])/2, (-vertices[0][0] + vertices[2][0]), (-vertices[0][1] + vertices[2][1]), 0, 0, dynamictype]).tolist()
    elif classtype == 1:
        # 返回形状类型，左下角点坐标，长，长边宽，短边宽，动态类型，标签
        return np.array([1, vertices[0][0], vertices[0][1], (-vertices[0][0] + vertices[2][0]), (-vertices[0][1] + vertices[1][1]), (-vertices[0][1] + vertices[2][1]), 0, dynamictype]).tolist()
    elif classtype == 2:
        # 返回形状类型，左下角顶点坐标，两个长，两个宽，动态类型，标签
        return np.array([2, vertices[0][0][0], vertices[0][0][1], vertices[0][2][0] - vertices[0][0][0], vertices[2][2][0] - vertices[0][0][0], vertices[1][1][1] - vertices[0][0][1], vertices[2][1][1] - vertices[0][0][1], dynamictype]).tolist()
    elif classtype == 3:
        # 返回形状类型，中心点坐标，半径，动态类型，标签
        return np.array([3, vertices[0], vertices[1], vertices[2], 0, 0, 0, dynamictype]).tolist()
    elif classtype == 4:
        # 返回形状类型，左下角顶点坐标，高，长边宽，短边宽，动态类型，标签
        return np.array([4, vertices[0][0], vertices[0][1], (vertices[0][1] - vertices[1][1]), (vertices[0][0] - vertices[3][0]), (-vertices[1][0] + vertices[2][0]), 0, dynamictype]).tolist()

def main(data_path, output_path):
    
    scenes = []
    for i in range(2500):
        with open(data_path + str(i + 1) + ".json", 'r') as f:
            file = json.load(f)
        
        objects = []
        objects = build_data(file, objects)
        scene = {
            "scene_id": i,
            "objects": objects
        }
        scenes.append(scene)
        
    with open(output_path, 'w') as f:
        json.dump(scenes, f, indent=4)

if __name__ == "__main__":
    
    data_path = "/home/guchenyang/Codes/tool-games/environment/Trials/Generated/Compositional/data/"
    output_path = "/home/guchenyang/Codes/tool-games/environment/Trials/Generated/Compositional/data.json"
    main(data_path, output_path)