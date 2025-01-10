import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import add_noise_catapult_vertical, add_noise_catapult_horizon, check

output_folder = "/home/guchenyang/Codes/tool-games/environment/Trials/Generated/Noise/catapult"

for i in range(1, 11):
    for j in range(1, 11):
        index = (i - 1) * 10 + j
        file_name = "/home/guchenyang/Codes/tool-games/environment/Trials/Generated/Noise/jsons/2.json"
        with open(file_name, "r") as file:
            bridge_data = json.load(file)
        output_file = os.path.join(output_folder, str(index) + ".json")
        with open(output_file, "w") as file:
            json.dump(bridge_data, file, indent=4)
        
        output_file = os.path.join(output_folder, str(index) + ".json")
        img = os.path.join(output_folder, str(index) + ".png")
        with open(output_file, "r") as file:
            bridge_data = json.load(file)
        
        offset_horizon = i * (-2)
        offset_vertical = j * 2
        data = add_noise_catapult_vertical(bridge_data, offset_horizon)
        data = add_noise_catapult_horizon(data, offset_vertical)
    
        check(data, img)
        
        with open(output_file, "w") as file:
            json.dump(data, file, indent=4)