import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import bridge_horizon_move, bridge_vertical_move, catapult_horizon_move, catapult_vertical_move, check

output_folder = "/home/guchenyang/Codes/tool-games/environment/Trials/Generated/Compositional/move"

for i in range(1, 6):
    for j in range(1, 6):
        for k in range(1, 6):
            for w in range(1, 6):
                index = (((i - 1) * 5 + j - 1) * 5 + k - 1) * 5 + w
                file_name = "/home/guchenyang/Codes/tool-games/environment/Trials/Generated/Compositional/jsons/1.json"
                with open(file_name, "r") as file:
                    bridge_data = json.load(file)
                output_file = os.path.join(output_folder, str(index) + ".json")
                with open(output_file, "w") as file:
                    json.dump(bridge_data, file, indent=4)
                
                output_file = os.path.join(output_folder, str(index) + ".json")
                img = os.path.join(output_folder, str(index) + ".png")
                with open(output_file, "r") as file:
                    bridge_data = json.load(file)
                
                offset_horizon_bridge = (i - 2) * 6
                offset_vertical_bridge = (j - 2) * 6
                offset_horizon_catapult = (k - 2) * 6
                offset_vertical_catapult = (w - 2) * 6
                data = bridge_horizon_move(bridge_data, offset_horizon_bridge)
                data = bridge_vertical_move(data, offset_horizon_bridge)
                data = catapult_horizon_move(data, offset_horizon_catapult)
                data = catapult_vertical_move(data, offset_vertical_catapult)
                
                check(data, img)
                
                with open(output_file, "w") as file:
                    json.dump(data, file, indent=4)
        