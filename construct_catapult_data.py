import numpy as np
import pygame as pg
import json
import cv2
from pyGameWorld.viewer import drawWorld, loadFromDict
from utils import list2array, random_move_original_catapult, add_noise_catapult, add_random_obj, build_catapult_data

file_dir = './tool-games/environment/Trials/Original/Catapult.json'

scenes = []

with open(file_dir, 'r') as f:
    file = json.load(f)

for index in range(10000):
    objects = []

    file = random_move_original_catapult(file)

    file, objects = add_noise_catapult(file, objects, 5)

    file, objects = add_random_obj(file, objects)


    objects = build_catapult_data(file, objects)

    scene = {
            "scene_id": index,
            "objects": objects
        }
    scenes.append(scene)

with open('./catapult_data_5.json', 'w') as f:
    json.dump(scenes, f)
