"""

Generate datafiles to test tRecs2.py

Not all cells of the number specified will be generated in the first frame. 

70% wil be generated in the first frame and the rest will be generated randomly as time proceeds.

Cells will divide with a cell cycle length of approx. 20 time frames.

Files will be generated in a format consistent with the imaris files


"""

import os
from pprint import pprint
from random import randint

def populate_directories(TEST_PATH):

    """_summary_

    Returns:
        _type_: _description_
    """

    iteration = 0

    if not os.path.isdir(TEST_PATH):

        os.makedirs(TEST_PATH)
        iterationFolder = os.path.join(TEST_PATH, f"testRecs{iteration}")
        os.makedirs(iterationFolder)
        os.makedirs(os.path.join(iterationFolder, "test_data"))
        return iteration
    
    while os.path.isdir(os.path.join(TEST_PATH, f"testRecs{iteration}")):
        iteration += 1

    iterationFolder = os.path.join(TEST_PATH, f"testRecs{iteration}")
    os.makedirs(iterationFolder)
    os.makedirs(os.path.join(iterationFolder, "test_data"))
    return iteration, os.path.join(iterationFolder, "test_data"), iterationFolder
    


def generate_cells(NUMBER_OF_CELLS:int, NUMBER_OF_TIMEPOINTS:int, grid_size:int =1024):
    cells_dic = {}
    perc70_cutoff = NUMBER_OF_CELLS * 0.7
    
    for cell in range(0, NUMBER_OF_CELLS):

        startTime:int = 0
        maxStart:int = int(NUMBER_OF_TIMEPOINTS * 0.8)

        if cell > perc70_cutoff:
            startTime = randint(0, maxStart)

        cells_dic[cell] = {"times":[startTime],
                           "positions":[(randint(0, grid_size), randint(0, grid_size))]}
        
    return cells_dic


def move_cell(cells_dic, cell, t, step_size):
    print(cell, cells_dic[cell])
    cells_dic[cell]["times"].append(t+1)
    currentPos = cells_dic[cell]['positions'][-1]
    cx, cy = currentPos
    new_x = cx+randint(-step_size, step_size)
    new_y = cy+randint(-step_size, step_size)
    cells_dic[cell]["positions"].append((new_x, new_y))

    return cells_dic


def divide_cell(cells_dic, cell, t, step_size, new_cells_dic, family_net):
    max_cells = max(list(cells_dic) +list(new_cells_dic))+ 1
    new_cell_count = 0
    for newCell in range(max_cells, max_cells+2):

        if randint(0, 8) == 8:
            continue

        currentPos = cells_dic[cell]['positions'][-1]
        cx, cy = currentPos
        new_x = cx+randint(-step_size, step_size)
        new_y = cy+randint(-step_size, step_size)
        new_cells_dic[newCell] = {"times":[t+1], "positions" : [(new_x, new_y)]}

        family_net.write(f"{cell}\t{newCell}\n")
        new_cell_count += 1
    if new_cell_count == 0:
        family_net.write(f"{cell}\tNone\n")
    return new_cells_dic


def cycle_cells(cells_dic,  NUMBER_OF_TIMEPOINTS:int, family_net, step_size = 6):

    div_pob = {18:10, 19:5, 20:3, 21:2, 22:1}
    new_cells_dic = {}
    for t in range(0, NUMBER_OF_TIMEPOINTS):

        cells_dic.update(new_cells_dic)

        for cell in cells_dic:
            currentT, minT = cells_dic[cell]['times'][-1], cells_dic[cell]['times'][0]
            if currentT == t:
                
                n_cyc = currentT - minT

                if minT == 0 and n_cyc < 18:
                    n_cyc = 18
                    cells_dic = move_cell(cells_dic, cell, t, step_size)
                    print(cell, t, "move")

                elif minT != 0 and n_cyc < 18:
                    cells_dic = move_cell(cells_dic, cell, t, step_size)
                    print(cell, t, "move")

                elif n_cyc >= 23:
                    new_cells_dic = divide_cell(cells_dic, cell, t, step_size, new_cells_dic, family_net)
                    print(cell, t, "divide")

                elif randint(0, div_pob[n_cyc]) == 0:
                    new_cells_dic = divide_cell(cells_dic, cell, t, step_size, new_cells_dic, family_net)
                    print(cell, t, "divide")
                
                else:
                    cells_dic = move_cell(cells_dic, cell, t, step_size)
                    print(cell, t, "move")
    cells_dic.update(new_cells_dic)
    return cells_dic

def make_imaris_positions(iteration, cells_dic, iterationPath):

    pos_file = f'testRecs{iteration}_Position.csv'
    top_text = "\nPosition\n ==================== \nPosition X,Position Y,Position Z,Unit,Category,Collection,Time,TrackID,ID,\n"

    with open(os.path.join(iterationPath, pos_file), "w") as open_pos_file:
        open_pos_file.write(top_text)
        for cell in cells_dic:
            for n, (time, position) in enumerate(zip(cells_dic[cell]['times'], cells_dic[cell]['positions'])):
                posX, posY = position
                open_pos_file.write(f"{posX},{posY},1,um,spot,position,{time},{cell},{n},\n")


    
if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("testPath", help="path where the data should be generated")
    parser.add_argument("-c", "--cells", default=20, type=int, help="Number of cells to be generated")
    parser.add_argument("-t", "--time", default=60, type=int, help="Number of timepoints")

    args = parser.parse_args()

    TEST_PATH = args.testPath
    NUMBER_OF_CELLS = args.cells
    NUMBER_OF_TIMEPOINTS = args.time

    cells_dic = generate_cells(NUMBER_OF_CELLS, NUMBER_OF_TIMEPOINTS)

    iteration, dataPath, iterationFolder = populate_directories(TEST_PATH)

    family_net_path = os.path.join(dataPath, "families.tsv")

    with open(family_net_path, "w") as family_net:
        family_net.write("mother\tdaughter\n")
        cells_dic = cycle_cells(cells_dic, NUMBER_OF_TIMEPOINTS, family_net)
    make_imaris_positions(iteration, cells_dic, iterationFolder)
    filesToGenerate = [f'testRecs{iteration}_Intensity_Mean_Ch=1_Img=1.csv', f'testRecs{iteration}_Position.csv', f'testRecs{iteration}_Time.csv', f'testRecs{iteration}_Intensity_Mean_Ch=2_Img=1.csv', f'testRecs{iteration}_Overall.csv', f'testRecs{iteration}_Intensity_Mean_Ch=3_Img=1.csv', f'testRecs{iteration}_Time_Index.csv']


    