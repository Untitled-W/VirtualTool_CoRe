from pyGameWorld import PGWorld, ToolPicker
from pyGameWorld.viewer import demonstrateTPPlacement, drawWorld, drawTool, drawPathSingleImage, drawWorldWithTools
from pyGameWorld.world import loadFromDict
import json
import pygame as pg
import cv2
import os
# os.chdir('..')

import numpy as np
def reward_function(path_dict, goal_verts):
    ball_path = path_dict['Ball']
    placed_path = path_dict['PLACED']
    ball_path = np.array(ball_path)
    placed_path = np.array(placed_path)
    #print(ball_path.shape, placed_path.shape)
    distance = np.zeros((ball_path.shape[0], 4), dtype=np.float32)
    x_min = goal_verts[0][0]
    x_max = goal_verts[0][0]
    y_min = goal_verts[0][1]
    y_max = goal_verts[0][1]
    for i in range(4):
        x_min = x_min if x_min < goal_verts[i][0] else goal_verts[i][0]
        x_max = x_max if x_max > goal_verts[i][0] else goal_verts[i][0]
        y_min = y_min if y_min < goal_verts[i][1] else goal_verts[i][1]
        y_max = y_max if y_max > goal_verts[i][1] else goal_verts[i][1]
        distance[:, i] = np.sqrt((ball_path[:, 0] - goal_verts[i][0]) ** 2 + (ball_path[:, 1] - goal_verts[i][1]) ** 2)
    distance = np.min(distance, axis=1)
    mask = np.logical_and(np.logical_and(ball_path[:, 0] > x_min, ball_path[:, 0] < x_max), np.logical_and(ball_path[:, 1] > y_min, ball_path[:, 1] < y_max))
    distance[mask] *= -1
    #distance = np.sqrt((ball_path[:, 0] - placed_path[:, 0]) ** 2 + (ball_path[:, 1] - placed_path[:, 1]) ** 2)
    #print(distance)
    orig_distance = distance[0]
    reward = 1 - np.min(distance) / orig_distance
    return reward


json_dir = "./tool-games/environment/Trials/"
modes = ['Original/','Validation/']


def vis():
    '''
    Trial 1: Visualize every task
    '''
    for mode in modes:
        for tnm in os.listdir(json_dir+mode):
            with open(json_dir+mode+tnm,'r') as f:
                btr = json.load(f)
            # goal_verts = btr['world']['objects']['Goal']['points']
            tp = ToolPicker(btr)
            pg.image.save(drawWorldWithTools(tp), 'images/'+mode+tnm[:-5]+'.png')


from multiprocessing import Pool, Lock
import time

lock = Lock()

def process_task(args):
    mode, tnm = args
    with open(json_dir + mode + tnm, 'r') as f:
        btr = json.load(f)
    tp = ToolPicker(btr)
    count = {'success': 0, 'fail': 0, 'None': 0}
    
    num = 20
    for i in range(num):
        for j in range(num):
            position = (tp.worldDims[0] // num * i + tp.worldDims[0] // num // 2, tp.worldDims[1] // num * j + tp.worldDims[1] // num // 2)
            path_dict, success, time_to_success = tp.observePlacementPath(toolname="obj1", position=position, maxtime=20.)
            if success:
                count['success'] += 1
            elif success is None:
                count['None'] += 1
            else:
                count['fail'] += 1
                
    # save into txt
    with lock:
        with open(f'results_{num:02}.txt', 'a') as f:
            f.write(f'{tnm[:-5]:20}' + str(count) + '\n')

def count_success_rate():
    '''
    Trial 2: Count success rate for every task if solve with brute force
    '''
    tasks = []
    for mode in modes:
        for tnm in os.listdir(json_dir + mode):
            tasks.append((mode, tnm))
    
    start_time = time.time()
    
    with Pool() as pool:
        for _ in pool.imap_unordered(process_task, tasks):
            print("A task has been completed.")
    
    end_time = time.time()
    total_time = end_time - start_time
    print(f"Total time taken: {total_time:.2f} seconds")

if __name__ == '__main__':
    count_success_rate()

# s = drawWorldWithTools(tp)
# pg.image.save(s, 'test.png')

# path_dict, success, time_to_success = tp.observePlacementPath(toolname="obj1", position=(80,500), maxtime=20.)
# print(success)
# s = drawPathSingleImage(btr['world'], path_dict, pathSize=10)
# pg.image.save(s, 'path.png')

# for i in range(20):
#     for j in range(20):
#         path_dict, success, time_to_success = tp.observePlacementPath(toolname="obj1", position=(600 // 20 * i + 600 // 20 // 2, 600 // 20 * j + 600 // 20 // 2), maxtime=20.)

# demonstrateTPPlacement(tp, 'obj1', (80, 400), hz=300)