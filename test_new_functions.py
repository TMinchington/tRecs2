"""

Working space to test new functions

"""
from random import randint
from pprint import pprint
import seaborn as sn
import matplotlib.pyplot as plt
from numba import jit
import pandas as pd


def make_daughter(parent, step_size, currentT, cell_dic):
    # print(parent)
    px, py, pz = cell_dic[parent]['coord'][-1]

    newX = randint(px-step_size, px+step_size)
    newY = randint(py-step_size, py+step_size)
    newZ = randint(pz-step_size, pz+step_size)

    newId = max(cell_dic) + 1

    cell_dic[newId] = {"time":[currentT], "coord":[(newX, newY, newZ)], "parent": parent, "last_div":currentT}
    
    return cell_dic


def move_cell(cell, cell_dic, step_size=6):
    x, y, z =  cell_dic[cell]['coord'][-1]

    # t= cell_dic[cell]['time'][-1] +1
    x = randint(x-step_size, x+step_size)
    y = randint(y-step_size, y+step_size)
    z = randint(z-step_size, z+step_size)

    cell_dic[cell]["time"].append(max(cell_dic[cell]["time"])+1)
    cell_dic[cell]['coord'].append((x, y, z))

    return cell_dic



def simulate_dividing_cells(cellN, 
                            nTime=5, 
                            space=500, 
                            step_size=6):
    
    # make start cells

    cell_dic = {}

    for cell in range(0, cellN):
        x, y, z = randint(0, space), randint(0, space), randint(0, space)

        # cells are represented as a tupel (time, cellID, x, y, z, parent)

        cell_dic[cell] = {"time":[0], "coord":[(x, y, z)], "parent": cell, "last_div":0}

    currentCellID = cellN + 1

    for t in range(1, nTime):

        cell_list_t = list(cell_dic)

        for cell in cell_list_t:

            print(t, cell)

            if t-cell_dic[cell]["last_div"] < 4:
                cell_dic = move_cell(cell, cell_dic)
                continue

            if randint(0, 4) == 0:
                cell_dic = make_daughter(cell, step_size, t, cell_dic)
                cell_dic = make_daughter(cell, step_size, t, cell_dic)
                
            
            else:
                cell_dic = move_cell(cell, cell_dic)

    return cell_dic


def plot_cell_division(cell_list, t, se_dic):
    print("------------------------------------")
    x_list=[]
    y_list=[]
    t_list=[]
    f_list=[]

    for cell in cell_list:
        ct, id, x, y, z, parentID = cell

        if t==se_dic[id][1] and t==ct:
            # print(t)
            x_list.append(x)
            y_list.append(y)
            t_list.append(ct)
            f_list.append(id)

            print(cell)

        if t+1==se_dic[id][0] and t+1 == ct:
            # print(t)
            x_list.append(x)
            y_list.append(y)
            t_list.append(ct)
            f_list.append(parentID)

            print(cell)

    # print(len(x_list))
    sn.scatterplot(x=x_list, y=y_list, hue=t_list)
    plt.show()
    plt.close()

    sn.scatterplot(x=x_list, y=y_list, c=f_list, style=t_list)
    plt.show()
    plt.close()


def get_starts_ends(cell_dic):

    se_dic = {}


    for cell in cell_dic:

        se_dic[cell] = [cell_dic[cell]["last_div"], cell_dic[cell]["time"][-1]]

    return se_dic


def starters_dic(se_dic):
    
    s_dic = {}

    for cell in se_dic:
        start = se_dic[cell][0]
        try:
            s_dic[start].append(cell)

        except:
            s_dic[start] = [cell]

    return s_dic

def enders_dic(se_dic):
    
    e_dic = {}

    for cell in se_dic:
        end = se_dic[cell][1]

        try:
            e_dic[end].append(cell)

        except:
            e_dic[end] = [cell]

    return e_dic

@jit
def get_distances(x1_ls, x2_ls, y1_ls, y2_ls, z1_ls, z2_ls):
    
    dis_ls = []

    for x1, x2, y1, y2, z1, z2 in zip(x1_ls, x2_ls, y1_ls, y2_ls, z1_ls, z2_ls):

        d = ((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)**0.5

        dis_ls.append(d)

    return dis_ls


def trim_net(c1, c2, d, se_dic, co):
    netFrame = pd.DataFrame({"end":c1, "start":c2, "dis":d})

    netFrame.sort_values("dis", inplace=True)

    print(netFrame)
    unique_starters = len(set(netFrame.start))
    netFrame = netFrame.loc[netFrame.dis < co].copy()
    print("CUT")
    print(netFrame)
    # for cell in netFrame.end:
    #     pprint(se_dic[cell])

    
    print(netFrame.end.value_counts())


    exit()



def assign_daughters(cell_dic, se_dic, co=50):
    s_dic = starters_dic(se_dic)
    e_dic = enders_dic(se_dic)

    pprint(s_dic)
    pprint(e_dic)

    for etime in e_dic:
        end_cells = e_dic[etime]
        start_cells = s_dic[etime]

        x1, x2, y1, y2, z1, z2, cell1, cell2 = [], [], [], [], [], [], [], []
        
        for eCell in end_cells:
            for sCell in start_cells:
                x1.append(cell_dic[eCell]["coord"][-1][0])
                y1.append(cell_dic[eCell]["coord"][-1][1])
                z1.append(cell_dic[eCell]["coord"][-1][2])
                cell1.append(eCell)

                x2.append(cell_dic[sCell]["coord"][0][0])
                y2.append(cell_dic[sCell]["coord"][0][1])
                z2.append(cell_dic[sCell]["coord"][0][2])
                cell2.append(sCell)


        dis = get_distances(x1, x2, y1, y2, z1, z2)

        trim_net(cell1, cell2, dis, se_dic, co)




if __name__ == "__main__":
    
    cells_list = simulate_dividing_cells(3, nTime=15)
    pprint(cells_list)
    se_dic = get_starts_ends(cells_list)
    assign_daughters(cells_list, se_dic)
