from pyGameWorld import PGWorld, ToolPicker
from pyGameWorld.viewer import *
from pyGameWorld.viewer import demonstrateTPPlacement, demonstrateTPPlacement_test
from pyGameWorld.world import *
import json
import pygame as pg
from model import PolicyNet, tool_transform, img_transform, reward_func
from model import DetectionModel, DetectionDataset, DataLoader

import torch
import os
import numpy as np
import cv2

def drawWorld(world, backgroundOnly=False, lightenPlaced=False):
    s = pg.Surface(world.dims)
    s.fill(world.bk_col)

    def makept(p):
        return [int(i) for i in world._invert(p)]

    for b in world.blockers.values():
        drawpts = [makept(p) for p in b.vertices]
        pg.draw.polygon(s, b.color, drawpts)

    for o in world.objects.values():
        if not backgroundOnly or o.isStatic():
            if lightenPlaced and o.name == 'PLACED':
                _draw_obj(o, s, makept, .5)
            else:
                _draw_obj(o, s, makept)

    return s

def generate_world_from_output(pred, index, detector):
    
    origin_json = os.path.join(origin_path, f'{index + 1}.json')
    with open(origin_json, 'r') as f:
        wd = json.load(f)
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    data_index = data[index]
    objects = data_index['objects']
    false_labels = []
    
    for i in range(len(pred)):
        if pred[i] == 0:
            false_labels.append(objects[i]['object'])
            
    # print(false_labels)
    objects_to_remove = []
    
    for key in wd['world']['objects'].keys():
        if key in ("_LeftWall", "_RightWall", "_TopWall", "_BottomWall", "Goal", "Ball"):
            continue
        
        elif key in false_labels:
            objects_to_remove.append(key)
            
    # print(objects_to_remove)
    
    for key in objects_to_remove:
        del wd['world']['objects'][key]
    
    output_json = os.path.join(detector_path, detector, f'{index + 1}.json')
    with open(output_json, 'w') as f:
        json.dump(wd, f, indent=4)
        
    return output_json

def detect_render(test_loader, detector, detector_name):
    
    for i in range(total_number):  
        x, y, z = next(iter(test_loader))
        x = x.to(device)
        logits = detector(x).squeeze()
        logits = torch.clamp(logits, -10., 10.)
        pred_label = (logits > 0).long()
        
        output_json = generate_world_from_output(pred_label.cpu().numpy().tolist(), i, detector_name)

        with open(output_json,'r') as f:
            wd = json.load(f)
        
        world = loadFromDict(wd['world'])

        s = drawWorld(world, backgroundOnly=False, lightenPlaced=False)
        
        output_image = os.path.join(detector_path, detector_name, f'{i + 1}.jpg')
        pg.image.save(s, output_image)
        
class SingleEnv:

    def __init__(self, env_name=str, index=int, tool_index=int):
        self.env_name = env_name
        self.tool_index = tool_index
        self.file = json.load(open(os.path.join(data_path, env_name, f'data/{index}.json'), 'r'))
        
    def get_state(self):
        images, tools = [], []
        pgw = loadFromDict(self.file['world'])
        img = pg.surfarray.array3d(drawWorld(pgw)).transpose(1, 0, 2)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        tool_points = self.file['tools'][f'obj{self.tool_index:d}'][0]
        tool_points = [[content[0]+45, content[1]+45] for content in tool_points]
        tool_image = np.zeros((90, 90, 1), dtype=np.uint8)
        cv2.fillPoly(tool_image, [np.array(tool_points)], 255)
        img = img_transform(img)
        tool_image = tool_transform(tool_image)
        
        images.append(img)
        tools.append(tool_image)
        
        return np.stack(images), np.stack(tools)
    
    def check_success(self, p):
    
        x, y = p[0]
        position = (int(600 * x), int(600 * y))
        # print(position)
        tp = ToolPicker(self.file)
        path_dict, success, time_to_success, wd = tp.observeFullPlacementPath(toolname=f"obj{self.tool_index}", position=position, maxtime=10.)
        # if wd != None:
        #     demonstrateTPPlacement_test(tp, toolname1=f"obj{self.tool_index}", position1=position)
        return 1 if success else 0

class TestEnv:    
    
    def __init__(self, env_name = "Compositional", index=int, tool_brigde=int, tool_catapult=int):
        self.file_bridge = json.load(open(f'/home/guchenyang/Codes/tool-games/environment/Detector/Bridge/{index}.json', 'r'))
        self.image_bridge = cv2.imread(f'/home/guchenyang/Codes/tool-games/environment/Detector/Bridge/{index}.jpg')        
        self.file_catapult = json.load(open(f'/home/guchenyang/Codes/tool-games/environment/Detector/Catapult/{index}.json', 'r'))
        self.image_catapult = cv2.imread(f'/home/guchenyang/Codes/tool-games/environment/Detector/Catapult/{index}.jpg')   
        self.tool_brigde = tool_brigde
        self.tool_catapult = tool_catapult
        self.file = json.load(open(os.path.join(data_path, env_name, f'data/{index}.json'), 'r'))
    
    def get_state_brigde(self):
        images, tools = [], []
        img = cv2.cvtColor(self.image_bridge, cv2.COLOR_RGB2BGR)
        tool_points = self.file_bridge['tools'][f'obj{self.tool_brigde}'][0]
        tool_points = [[content[0]+45, content[1]+45] for content in tool_points]
        tool_image = np.zeros((90, 90, 1), dtype=np.uint8)
        cv2.fillPoly(tool_image, [np.array(tool_points)], 255)
        img = img_transform(img)
        tool_image = tool_transform(tool_image)
        images.append(img)
        tools.append(tool_image)
        
        return np.stack(images), np.stack(tools)
    
    def get_state_catapult(self):
        images, tools = [], []
        img = cv2.cvtColor(self.image_catapult, cv2.COLOR_RGB2BGR)
        tool_points = self.file_bridge['tools'][f'obj{self.tool_catapult}'][0]
        tool_points = [[content[0]+45, content[1]+45] for content in tool_points]
        tool_image = np.zeros((90, 90, 1), dtype=np.uint8)
        cv2.fillPoly(tool_image, [np.array(tool_points)], 255)
        img = img_transform(img)
        tool_image = tool_transform(tool_image)
        images.append(img)
        tools.append(tool_image)
        
        return np.stack(images), np.stack(tools)
    
    def check_success(self, p1, p2):
    
        x1, y1 = p1[0]
        x2, y2 = p2[0]
        tp = ToolPicker(self.file)
        path_dict, success, time_to_success, wd = tp.observeFullPlacementPath_test(toolname1=f"obj{self.tool_brigde}", position1=(int(600 * x1), int(600 * y1)), toolname2=f"obj{self.tool_catapult}", position2=(int(600 * x2), int(600 * y2)))

        return 1 if success else 0

def Test_Single(env_name, model):
    
    success_rate = 0.0
    total = 10000
    success_num = 0
    for index in range(1, total + 1):
        success = 0
        for i in range(1, 4):
            env = SingleEnv(env_name, index, i)
            img, tool = env.get_state()
            img = torch.tensor(img).float().cuda()
            tool = torch.tensor(tool).float().cuda()
            # print(img.shape, tool.shape)
            action, mean, std = model(img, tool)
            # print(action)
            success += env.check_success(action)

        if success > 0:
            success_num += 1
            print(f'Index: {index}, Success: {success_num}')
        
        else:
            print(f'Index: {index}, Fail: {success_num}')

    success_rate = success_num / total
    return success_rate

def Test_Compositional(model_bridge, model_catapult):
    
    success_rate = 0.0
    total = 2500
    success_num = 0
    for index in range(1, total + 1):
        success = 0
        for i in range(1, 7):
            for j in range(1, 7):
                env = TestEnv("Compositional", index, i, j)
                img_bridge, tool_bridge = env.get_state_brigde()
                img_catapult, tool_catapult = env.get_state_catapult()
                img_bridge = torch.tensor(img_bridge).float().cuda()
                tool_bridge = torch.tensor(tool_bridge).float().cuda()
                img_catapult = torch.tensor(img_catapult).float().cuda()
                tool_catapult = torch.tensor(tool_catapult).float().cuda()

                action_bridge, mean, std = model_bridge(img_bridge, tool_bridge)
                action_catapult, mean, std = model_catapult(img_catapult, tool_catapult)
                
                success += env.check_success(action_bridge, action_catapult)

        if success > 0:
            success_num += 1
            print(f'Index: {index}, Success: {success_num}')
        
        else:
            print(f'Index: {index}, Fail: {success_num}')


    success_rate = success_num / total
    return success_rate

origin_path = '/home/guchenyang/Codes/tool-games/environment/Trials/Generated/Compositional/data'
file_path = '/home/guchenyang/Codes/tool-games/environment/Trials/Generated/Compositional/data.json'
detector_path = '/home/guchenyang/Codes/tool-games/environment/Detector'
data_path = '/home/guchenyang/Codes/tool-games/environment/Trials/Generated'
total_number = 2500
   
if __name__ == "__main__":

    device = 'cuda' 
    bridge_detector = DetectionModel(dim=256, in_dim=8, num_layers=6, num_heads=4, dropout=0.2).to(device)
    bridge_detector.load_state_dict(torch.load('/home/guchenyang/Codes/tool-games/environment/model/bridge_detector_1.pth'))
    bridge_detector.eval()
    
    catapult_detector = DetectionModel(dim=256, in_dim=8, num_layers=6, num_heads=4, dropout=0.2).to(device)
    catapult_detector.load_state_dict(torch.load('/home/guchenyang/Codes/tool-games/environment/model/catapult_detector_1.pth'))
    catapult_detector.eval()
    
    dataset = DetectionDataset(name='composition', file_path=file_path)
    test_loader = DataLoader(dataset, batch_size=1, drop_last=False)

    detect_render(test_loader, bridge_detector, 'Bridge')
    detect_render(test_loader, catapult_detector, 'Catapult')    
    
    bridge_ssup = PolicyNet().to(device)
    bridge_ssup.load_state_dict(torch.load('/home/guchenyang/Codes/tool-games/environment/model/bridge_ssup.pth'))
    bridge_ssup.eval()
    
    catapult_ssup = PolicyNet().to(device)
    catapult_ssup.load_state_dict(torch.load('/home/guchenyang/Codes/tool-games/environment/model/catapult_ssup.pth'))
    catapult_ssup.eval()
    
    success_bridge = Test_Single('Bridge', bridge_ssup)
    success_catapult = Test_Single('Catapult', catapult_ssup)
    
    print(f'Bridge success rate: {success_bridge}')
    print(f'Catapult success rate: {success_catapult}')
    
    success_compositional = Test_Compositional(bridge_ssup, catapult_ssup)  
    print(f'Compositional success rate: {success_compositional}')
    