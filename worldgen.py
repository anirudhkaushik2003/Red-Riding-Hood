import opensimplex
import random
import numpy as np
from collections import deque


def base_connect(data):
    test = np.array(data)
    row, col = test.shape
    height = 0
    for i in test[:, 8]:

        if i == 90:
            test[height][7] = 90
            height += 1
            if height > 16:
                height = 16
            test[height][7] = 60
            if height > 16:
                height = 16

            test[height][6] = 90
            height += 1
            if height > 16:
                height = 16
            test[height][6] = 60
            if height > 16:
                height = 16

            test[height][5] = 90
            height += 1
            if height > 16:
                height = 16
            test[height][5] = 60
            if height > 16:
                height = 16

            test[height][4] = 90
            height += 1
            if height > 16:
                height = 16
            test[height][4] = 60
            if height > 16:
                height = 16
            test[height][3] = 90
            height += 1
            if height > 16:
                height = 16
            test[height][3] = 60
            if height > 16:
                height = 16

            test[height][2] = 90
            height += 1
            if height > 16:
                height = 16
            test[height][2] = 60
            if height > 16:
                height = 16

            test[height][1] = 90
            height += 1
            if height > 16:
                height = 16
            test[height][1] = 60
            if height > 16:
                height = 16

            test[height][0] = 90
            height += 1
            if height > 16:
                height = 16
            test[height][0] = 60
            break
        height += 1
    return list(test)

    return data


def gen_new_world():
    arr = []
    r = range(80)
    for i in r:
        tmp = opensimplex.OpenSimplex(random.randint(0, 10000000))
        y = int(((tmp.noise2d(1, 2) + 1) ** 0.25) * random.randint(5, 8))
        arr.append(y)
    prev_y = 0

    world_data = [[0 for i in range((len(arr) * 5) + 5)] for j in range(17)]
    world_data[15][0] = 0
    world_data[15][1] = 0
    world_data[15][2] = 0
    world_data[15][3] = 0
    world_data[16][0] = 0
    world_data[16][1] = 0
    world_data[16][2] = 0
    world_data[16][3] = 0

    
    i = 8
    prev_y = arr[0]
    enemies_c = 7
    enemies_w = 13
    cooldo = 0
    cooldo1 = 0

    for y in arr:
        flatline = random.randint(2, 5)

        j = 0
        value = y
        val = prev_y

        while True:
            if abs(value - val) > 1:
                if value - val > 1:
                    val += 1
                if value - val < -1:
                    val -= 1
            else:
                val = value

            j += 1
            world_data[16 - val][i] = 60
            world_data[16 - val - 1][i] = 90
            if random.randint(0, 20) == 15 and cooldo == 0 and enemies_c > 0:
                world_data[16 - val - 4][i] = 25
                cooldo = 10
                enemies_c -= 1
            if random.randint(0, 20) == 15 and cooldo1 == 0 and enemies_w > 0:
                world_data[16 - val - 4][i] = random.choice([24,16])
                cooldo1 = 10
                enemies_w -= 1
            else:
                if random.randint(0, 10) == 5:
                    world_data[16 - val - 2][i] = 11
                if random.randint(0,50) == 5:
                    world_data[16 - val - 2][i] = 13
                if random.randint(0,18) == 5:
                    world_data[16 - val - 2][i] = 50
                if random.randint(0,20) == 7:
                    world_data[16 - val - 3][i] = random.choice([17,18,19])
                   

            if cooldo > 0:
                cooldo -= 1
            if cooldo1 > 0:
                cooldo1 -= 1
            i += 1
            if j >= flatline:
                break
        prev_y = val

    return world_data


def gen_chal_world():
    arr = []
    r = range(80)
    for i in r:
        tmp = opensimplex.OpenSimplex(random.randint(0, 10000000))
        y = int(((tmp.noise2d(1, 2) + 1) ** 0.25) * random.randint(5, 8))
        arr.append(y)
    print(max(arr), min(arr))
    prev_y = 0

    world_data = [[0 for i in range((len(arr) * 5) + 5)] for j in range(17)]
    world_data[15][0] = 0
    world_data[15][1] = 0
    world_data[15][2] = 0
    world_data[15][3] = 0
    world_data[16][0] = 0
    world_data[16][1] = 0
    world_data[16][2] = 0
    world_data[16][3] = 0
    i = 8
    prev_y = arr[0]
    enemies_c = 10
    cooldo = 0

    for y in arr:
        flatline = random.randint(2, 5)

        j = 0
        value = y
        val = prev_y

        while True:

            val = value

            j += 1
            world_data[16 - val][i] = 60
            world_data[16 - val - 1][i] = 90
            if random.randint(0, 20) == 15 and cooldo == 0 and enemies_c > 0:
                world_data[16 - val - 2][i] = 16
                cooldo = 10
                enemies_c -= 1
            else:
                if random.randint(0, 10) == 5:
                    world_data[16 - val - 2][i] = 11
                if random.randint(0,50) == 5:
                    world_data[16 - val - 2][i] = 13
                if random.randint(0,18) == 5:
                    world_data[16 - val - 2][i] = 50
                    
                    

            if cooldo > 0:
                cooldo -= 1
            i += 1
            if j >= flatline:
                break
        prev_y = val

    return world_data


def new_meth():
    world_data = np.array(gen_chal_world())
    p = 0
    height_list = []
    for i in world_data.T:
        height = 0
        for x in i:
            if x == 90:
                break
            if height == 16:
                break
            height += 1

        height_list.append((p, height))
        p += 1

    for i in range(len(height_list)):
        x = min(height_list, key=lambda x: x[1])
        if height_list[height_list.index(x)][1] > 0 and height_list.index(x) > 0:
            a = min(
                height_list[height_list.index(x) - 1][1],
                height_list[height_list.index(x)][1] + 1,
            )
            for k in range(a, height_list[height_list.index(x) - 1][1]):
                world_data[k][height_list[height_list.index(x) - 1][0]] = 90
            height_list[height_list.index(x) - 1] = (
                height_list[height_list.index(x) - 1][0],
                a,
            )

        if (
            height_list[height_list.index(x)][1] < 16
            and height_list.index(x) < len(height_list) - 1
        ):
            a = min(
                height_list[height_list.index(x) + 1][1],
                height_list[height_list.index(x)][1] + 1,
            )
            for k in range(a, height_list[height_list.index(x) + 1][1]):
                world_data[k][height_list[height_list.index(x) + 1][0]] = 90
            height_list[height_list.index(x) + 1] = (
                height_list[height_list.index(x) + 1][0],
                a,
            )

        height_list.remove(x)
    return list(world_data)


def place_items(world):
    world_data = np.array(world)
    final = []
    p = 0
    height_list = []
    q = deque()
    for i in world_data.T:
        height = 0
        for x in i:
            if x == 90:
                break
            if height == 16:
                break
            height += 1

        height_list.append((p, height))
        p += 1
    i = 0
    while i < len(height_list):
        if height_list[i][1] != 16:
            q.append(height_list[i])
            n = int(1)
            for j in range(i + 1, len(height_list)):
                temp = q.pop()
                q.append(temp)
                if temp[1] == height_list[j][1]:
                    q.append(height_list[j])
                    n += 1
                else:
                    if n == 4 or n == 5:
                        if random.random() >= 0.5:
                            temp = q.pop()
                            world[temp[1] - 1][i] = 70
                            world[temp[1] - 1][i + 1] = 80
                        elif random.random() <= 0.4:
                            temp = q.pop()
                            world[temp[1] - 1][i+1] = 14
                    elif n == 3:
                        if random.random() >= 0.2:
                            temp = q.pop()
                            world[temp[1] - 1][i] = 20
                            #final.append(i)
                    elif n == 2:
                        if random.random() >= 0.4:
                            temp = q.pop()
                            if random.choice([10,40]) == 10:
                                world[temp[1] - 1][i] = 10
                            else:
                                world[temp[1] - 1][i+1] = 40
                            #final.append(i)
                        else:
                            world[temp[1] - 1][i] = 22
                            world[temp[1]-1][i+1] = 23
                            
                        
                    elif n >= 6 and n < 8:
                        if random.random() >= 0.2:
                            temp = q.pop()
                            world[temp[1] - 1][i+1] = random.choice([12,21])
                            world[temp[1] - 1][i+2] = 15
                            world[temp[1] - 1][i+4] = random.choice([12,21])
                    elif n >= 8:
                        if random.random() >= 0.3:
                            temp = q.pop()
                            if temp[1] >= 5:
                                world[temp[1] - 1][i+1] = random.choice([60,90])
                                world[temp[1] - 1][i+2] = random.choice([60,90])
                                world[temp[1] - 2][i+2] = random.choice([60,90])
                                world[temp[1] - 1][i+3] = random.choice([60,90])
                                world[temp[1] - 2][i+3] = random.choice([60,90])
                                world[temp[1] - 3][i+3] = random.choice([60,90])
                                world[temp[1] - 3][i+4] = random.choice([60,90])
                                world[temp[1] - 4][i+4] = 50
                                
                                world[temp[1] - 3][i+5] = random.choice([60,90])
                            
                            
                            
                            
                            

                            
                    q.clear()
                    i = j - 1

                    break
        i += 1
    l = 0
    
    return world
