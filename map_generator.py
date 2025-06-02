from gym_microrts.envs.vec_env import MicroRTSGridModeVecEnv
import numpy as np
import time
from gym_microrts import microrts_ai
from collections import namedtuple

NONE = 0
RESOURCE = 1
BASE = 2
BARRACK = 3
WORKER = 4
LIGHT = 5
HEAVY = 6
RANGED = 7

PLAYER = 0
ENEMY = 1

save_path = "C:\\Users\\User\\anaconda3\\envs\\drl-transformer-newenv\\Lib\\site-packages\\gym_microrts\\microrts\\maps\\custom\\"

class MapVisualizer:
    def __init__(self, path):
        self.path = "maps/" + path
        print(self.path)
        self.env = MicroRTSGridModeVecEnv(
            num_selfplay_envs=0,
            num_bot_envs=1,
            max_steps=2000,
            render_theme=2,
            ai2s=[microrts_ai.coacAI for _ in range(1)],
            map_paths=[self.path],
            reward_weight=np.array([10.0, 1.0, 1.0, 0.2, 1.0, 4.0]),
        )
        obs = self.env.reset()
    def visualize(self):
        self.env.render()
        time.sleep(10)
        self.env.close()

grid_data = namedtuple("grid_data", "hit_points, resources, owner, unit_types, terrain")    

class MapGenerator:
    unit_type_dict = {0: "None", 1: "Resource", 2: "Base", 3: "Barracks", 4: "Worker", 5: "Light", 6: "Heavy", 7: "ranged"}
    def __init__(self, name, H, W):
        self.saved_path = save_path + name #save path
        self.map_data = [[grid_data(0, 0, 0, 0, 0) for _ in range(W)] for _ in range(H)]
        self.H = H
        self.W = W
    
    def set_grid(self, x, y, hit_points, resources, owner, unit_types, terrain):
        data = grid_data(hit_points, resources, owner, unit_types, terrain)
        if terrain == 1:
            data = grid_data(0, 0, -1, 0, 1)
        elif unit_types == RESOURCE:
            data = grid_data(1, resources, -1, unit_types, 0)
        self.map_data[y][x] = data
    
    def set_light(self, x, y, owner):
        self.set_grid(x, y, 4, 0, owner, LIGHT, 0)
    def set_heavy(self, x, y, owner):
        self.set_grid(x, y, 4, 0, owner, HEAVY, 0)
    def set_range(self, x, y, owner):
        self.set_grid(x, y, 1, 0, owner, RANGED, 0)
    
    def remove(self, x, y):
        self.map_data[y][x] = grid_data(0, 0, 0, 0, 0)
    
    def clear(self):
        self.map_data = [[grid_data(0, 0, 0, 0, 0) for _ in range(self.W)] for _ in range(self.H)]
    
    def generate(self):
        # Generate terrain string (row-major order)
        terrain_str = ''.join(str(self.map_data[y][x].terrain) for y in range(self.H) for x in range(self.W))

        # Players section (assuming always 2 players, each with 5 resources)
        players_xml = (
            '  <players>\n'
            '    <rts.Player ID="0" resources="5">\n'
            '    </rts.Player>\n'
            '    <rts.Player ID="1" resources="5">\n'
            '    </rts.Player>\n'
            '  </players>\n'
        )

        # Units section
        units_xml = '  <units>\n'
        unit_id = 16  # Start from 16 as in your example
        for y in range(self.H):
            for x in range(self.W):
                cell = self.map_data[y][x]
                # Skip empty cells and terrain-only cells
                if cell.unit_types == 0 and cell.terrain != 1:
                    continue
                # Only add units/resources, not terrain
                if cell.unit_types == RESOURCE:
                    units_xml += f'    <rts.units.Unit type="Resource" ID="{unit_id}" player="-1" x="{x}" y="{y}" resources="{cell.resources}" hitpoints="{cell.hit_points}" >\n    </rts.units.Unit>\n'
                    unit_id += 1
                elif cell.unit_types == BASE:
                    units_xml += f'    <rts.units.Unit type="Base" ID="{unit_id}" player="{cell.owner}" x="{x}" y="{y}" resources="{cell.resources}" hitpoints="{cell.hit_points}" >\n    </rts.units.Unit>\n'
                    unit_id += 1
                elif cell.unit_types == BARRACK:
                    units_xml += f'    <rts.units.Unit type="Barracks" ID="{unit_id}" player="{cell.owner}" x="{x}" y="{y}" resources="{cell.resources}" hitpoints="{cell.hit_points}" >\n    </rts.units.Unit>\n'
                    unit_id += 1
                elif cell.unit_types == WORKER:
                    units_xml += f'    <rts.units.Unit type="Worker" ID="{unit_id}" player="{cell.owner}" x="{x}" y="{y}" resources="{cell.resources}" hitpoints="{cell.hit_points}" >\n    </rts.units.Unit>\n'
                    unit_id += 1
                elif cell.unit_types == LIGHT:
                    units_xml += f'    <rts.units.Unit type="Light" ID="{unit_id}" player="{cell.owner}" x="{x}" y="{y}" resources="{cell.resources}" hitpoints="{cell.hit_points}" >\n    </rts.units.Unit>\n'
                    unit_id += 1
                elif cell.unit_types == HEAVY:
                    units_xml += f'    <rts.units.Unit type="Heavy" ID="{unit_id}" player="{cell.owner}" x="{x}" y="{y}" resources="{cell.resources}" hitpoints="{cell.hit_points}" >\n    </rts.units.Unit>\n'
                    unit_id += 1
                elif cell.unit_types == RANGED:
                    units_xml += f'    <rts.units.Unit type="Ranged" ID="{unit_id}" player="{cell.owner}" x="{x}" y="{y}" resources="{cell.resources}" hitpoints="{cell.hit_points}" >\n    </rts.units.Unit>\n'
                    unit_id += 1
        units_xml += '  </units>\n'

        # Compose XML
        xml = (
            f'<rts.PhysicalGameState width="{self.W}" height="{self.H}">\n'
            f'  <terrain>{terrain_str}</terrain>\n'
            f'{players_xml}'
            f'{units_xml}'
            f'</rts.PhysicalGameState>\n'
        )

        # Write to file create if not exists
        with open(self.saved_path, 'x') as f:
            f.write(xml)


    
