import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import random_ball_size, check

input_folder = "/home/guchenyang/Codes/tool-games/environment/Trials/Generated/Bridge/move"
output_folder = "/home/guchenyang/Codes/tool-games/environment/Trials/Generated/Bridge/ball"

for i in range(1, 2501):
    input_file = os.path.join(input_folder, str(i) + ".json")
    with open(input_file, "r") as file:
        bridge_data = json.load(file)
    
    output_file = os.path.join(output_folder, str(i) + ".json")
    with open(output_file, "w") as file:
        json.dump(bridge_data, file, indent=4)
        
    output_file = os.path.join(output_folder, str(i) + ".json")
    img = os.path.join(output_folder, str(i) + ".png")
    with open(output_file, "r") as file:
        bridge_data = json.load(file)
    
    data = random_ball_size(bridge_data)
    check(data, img)
    with open(output_file, "w") as file:
        json.dump(data, file, indent=4)
    