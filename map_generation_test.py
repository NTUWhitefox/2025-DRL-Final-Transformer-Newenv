from map_generator import *
import random

def LHR2():
    map_generator = MapGenerator("LHR2.xml", 8, 8)
    map_generator.set_range(0, 0, 0)
    map_generator.set_range(1, 1, 0)
    map_generator.set_light(0, 2, 0)
    map_generator.set_heavy(1, 2, 0)
    map_generator.set_light(2, 0, 0)
    map_generator.set_heavy(2, 1, 0)
    
    map_generator.set_range(7, 7, 1)
    map_generator.set_range(6, 6, 1)
    map_generator.set_light(7, 5, 1)
    map_generator.set_heavy(6, 5, 1)
    map_generator.set_light(5, 7, 1)
    map_generator.set_heavy(5, 6, 1)

    map_generator.generate()

def LHR2_random():
    num_maps = 16 #generate 16 different light-only maps
    player_y_range = [0, 1]
    player_x_range = [0, 7]
    player_pos = []
    #place all possible player positions in a list
    for x in range(player_x_range[0], player_x_range[1]+1):
        for y in range(player_y_range[0], player_y_range[1]+1):
            player_pos.append((x, y))
    
    enemy_y_range = [6, 7]
    enemy_x_range = [0, 7]
    enemy_pos = []
    for x in range(enemy_x_range[0], enemy_x_range[1]+1):
        for y in range(enemy_y_range[0], enemy_y_range[1]+1):
            enemy_pos.append((x, y))

    for m in range(num_maps):
        map_generator = MapGenerator(f"LHR2_r{m}_test.xml", 8, 8)
        player_selected_pos = random.sample(player_pos, 6)
        enemy_selected_pos = random.sample(enemy_pos, 6)
        random.shuffle(player_selected_pos)
        random.shuffle(enemy_selected_pos)

        map_generator.set_light(player_selected_pos[0][0], player_selected_pos[0][1], 0)
        map_generator.set_light(player_selected_pos[1][0], player_selected_pos[1][1], 0)
        map_generator.set_heavy(player_selected_pos[2][0], player_selected_pos[2][1], 0)
        map_generator.set_heavy(player_selected_pos[3][0], player_selected_pos[3][1], 0)
        map_generator.set_range(player_selected_pos[4][0], player_selected_pos[4][1], 0)
        map_generator.set_range(player_selected_pos[5][0], player_selected_pos[5][1], 0)

        map_generator.set_light(enemy_selected_pos[0][0], enemy_selected_pos[0][1], 1)
        map_generator.set_light(enemy_selected_pos[1][0], enemy_selected_pos[1][1], 1)
        map_generator.set_heavy(enemy_selected_pos[2][0], enemy_selected_pos[2][1], 1)
        map_generator.set_heavy(enemy_selected_pos[3][0], enemy_selected_pos[3][1], 1)
        map_generator.set_range(enemy_selected_pos[4][0], enemy_selected_pos[4][1], 1)
        map_generator.set_range(enemy_selected_pos[5][0], enemy_selected_pos[5][1], 1)

        map_generator.generate()

def light_onlys():
    num_maps = 16 #generate 16 different light-only maps
    player_y_range = [0, 1]
    player_x_range = [0, 7]
    player_pos = []
    #place all possible player positions in a list
    for x in range(player_x_range[0], player_x_range[1]+1):
        for y in range(player_y_range[0], player_y_range[1]+1):
            player_pos.append((x, y))

    enemy_y_range = [6, 7]
    enemy_x_range = [0, 7]
    enemy_pos = []
    for x in range(enemy_x_range[0], enemy_x_range[1]+1):
        for y in range(enemy_y_range[0], enemy_y_range[1]+1):
            enemy_pos.append((x, y))
    
    print(player_pos)
    print(enemy_pos)
    num_lights = 4
    #randomly place 4 lights on the map for each side
    for m in range(num_maps):
        map_generator = MapGenerator(f"light_onlys_{m}.xml", 8, 8)
        player_lights_pos = random.sample(player_pos, num_lights)
        enemy_lights_pos = random.sample(enemy_pos, num_lights)
        for pos in player_lights_pos:
            map_generator.set_light(pos[0], pos[1], 0)
        for pos in enemy_lights_pos:
            map_generator.set_light(pos[0], pos[1], 1)
        map_generator.generate()
        
def light_corner():   
    map_name = "AllLight.xml"
    generator = MapGenerator(map_name, 8, 8)
    
    generator.clear()
    generator.set_light(7, 0, PLAYER)
    generator.set_light(7, 1, PLAYER)
    generator.set_light(7, 2, PLAYER)
    generator.set_light(7, 3, PLAYER)
    
    generator.set_light(0, 4, ENEMY)
    generator.set_light(0, 5, ENEMY)
    generator.set_light(0, 6, ENEMY)
    generator.set_light(0, 7, ENEMY)
    generator.generate()

def light_corner2():
    map_name = "AllLight2.xml"
    generator = MapGenerator(map_name, 8, 8)
    
    generator.clear()
    generator.set_light(7, 0, PLAYER)
    generator.set_light(7, 1, PLAYER)
    generator.set_light(6, 0, PLAYER)
    generator.set_light(6, 1, PLAYER)
    
    generator.set_light(1, 6, ENEMY)
    generator.set_light(1, 7, ENEMY)
    generator.set_light(0, 6, ENEMY)
    generator.set_light(0, 7, ENEMY)
    generator.generate()

def light_corner3():
    map_name = "AllLight3.xml"
    generator = MapGenerator(map_name, 8, 8)
    
    generator.clear()
    generator.set_light(7, 0, PLAYER)
    generator.set_light(6, 0, PLAYER)
    generator.set_light(5, 0, PLAYER)
    generator.set_light(4, 0, PLAYER)
    
    generator.set_light(0, 7, ENEMY)
    generator.set_light(1, 7, ENEMY)
    generator.set_light(2, 7, ENEMY)
    generator.set_light(3, 7, ENEMY)
    generator.generate()


if __name__ == "__main__":
    #LHR2_random()
    V = MapVisualizer(f"custom\\AllLight.xml")
    V.visualize()
    del V