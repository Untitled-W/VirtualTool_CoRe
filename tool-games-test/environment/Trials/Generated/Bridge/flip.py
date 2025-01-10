import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import flip, check

input_folder = "/home/guchenyang/Codes/tool-games/environment/Trials/Generated/Bridge/ball"
output_folder = "/home/guchenyang/Codes/tool-games/environment/Trials/Generated/Bridge/flip"

for i in range(1, 2501):
    input_file = os.path.join(input_folder, str(i) + ".json")
    with open(input_file, "r") as file:
        bridge_data = json.load(file)
    
    index = 2500 + i
    # index = i
    output_file = os.path.join(output_folder, str(index) + ".json")
    with open(output_file, "w") as file:
        json.dump(bridge_data, file, indent=4)
        
    output_file = os.path.join(output_folder, str(index) + ".json")
    img = os.path.join(output_folder, str(index) + ".png")
    with open(output_file, "r") as file:
        bridge_data = json.load(file)
    
    data = flip(bridge_data)
    check(data, img)
    with open(output_file, "w") as file:
        json.dump(data, file, indent=4)