"""
tRecs2

Description: track Reconstruction tool for dividing cells in imaris

tRecs2 improves on the accuracy of tRecs to provide more reliable track joining. 

The purpose is to link daughter cells to their mothers when cells are tracked division to division in imaris 

Author: Thomas Minchington
Date: 2024-11-13
Usage: python tRecs2.py [-h] [--time TIME] experiment_path


"""

import seaborn as sns
from matplotlib import pyplot as plt
import datetime
import argparse
import os
from numba import jit
from pprint import pprint
from numpy import mean, std
import itertools
import pandas as pd


def update_SE(trackID, Time, track_SE_dictionary):

    """ updates the start and end dictionary with new times if the the current time is smaller
    than the start or greater than the end.

    Returns:
        updated_dictionary -- start and end dictionary with new times
    """

    try:

        current_start_t, current_end_t = track_SE_dictionary[trackID][:]

        if current_start_t > Time:
            current_start_t = Time

        if current_end_t < Time:
            current_end_t = Time

        if current_start_t > current_end_t:
            exit(f'end error')
        
        track_SE_dictionary[trackID] = list((current_start_t, current_end_t))

    except KeyError:
        
        track_SE_dictionary[trackID] = [Time, Time]

    return track_SE_dictionary


def make_start_and_ends_dics(track_dic):

    """
    
    Makes seperate dictionaries based on the tracks dictionary which contain lists of trackIDs under 
    Keys which are the start or end of the tracks.
    
    Returns:
        start_dic -- start_dic[start_time] = [list of trackIDS]
        end_dic -- end_dic[end_time] = [list of trackIDS]

    """

    start_dic = {}
    end_dic = {}

    for track in track_dic:
        start, end = track_dic[track]

        try:

            start_dic[start].append(track)

        except KeyError:

            start_dic[start] = [track]

        
        try:

            end_dic[end].append(track)

        except KeyError:

            end_dic[end] = [track]

    return start_dic, end_dic


def trecsNew():
    t2 = ["......................................................................................................................................................",
"......................................................................................................................................................",
"......................................................................................................................................................",
"......................................................................................................................................................",
"..........................................-=++-.......................................................................................................",
"......................................=*#%%%%##-......................................................................................................",
"................:=-:...:........:--=+####%%#*==-:.....................................................................................................",
"...............-%%%%%%@@@@%%%#%%%%%####**#*+=+--=:....................................................................................................",
"..............-%%%@@@@@@@@@@@@%%###**++=++=+===+#*-...................................................................................................",
".............-%%%%@@@@@@@@@@%%%###*+++*+=+*##%%%@%*=................========-:.........................................:-=-:.............-=-:.........",
"............-%#%%%@%@%%@@@@%%###**+=++**##%%%#%#%#%%*........=#@....@@@%%%%@@@%=.....................................=%@@%@@@+.........#@@%@@%-.......",
"............####%@@@%@%%@%%####**++***#%@%@*#*%%%%+@%-......-@@@--..@@@.....:@@@....:-===:......:====:.....-====-...:%%*...#@@-.......*@@-..%@@:......",
"...........#**###%%%###%%##*+**+***##%@@%*@+#%%@%%=%@+.....:%@@@%#..@@@::::-+@@%...*@@##@@#:..-%@@##@@#..-@@%##@@%.........%@@........@@@...+@@=......",
"..........-%**#######**#***+++++*##%@@@*#*@%%%%@%@=%@=.......%@@....@@@@@@@@%*=...*@@:...%@%.:@@%...:++-.*@@*=--==:......+@@%:........@@@...+@@+......",
".........:*#****#**+=+++*++****#%%@@@%#+*%@%%%%%@%+@%:.......%@@....@@@..:#@@#....@@@%%%%%%%:=@@*.........=#%@@@@%=....*@@*:..........@@@...+@@=......",
".........*#+****+++*#########%%@@@@#%%%#*@@@%%%%%*+%=........%@@....@@@....*@@@-..*@@-...+=-.:@@%...:%#+.+**...-@@@..=@@@+====:..==:..*@@-..%@@:......",
".........#**##%#%##%@@%%%@@@@@%@@%%++%%%%%@@@@@%**#=.........*@@##..@@@.....-@@@=..*@@%#@@#-..:#@@##@@*..-#@@##%@%-.-@@@@@@@@@=.-@@*...#@@%@@%-.......",
"........*##%%%%@@@%%#####%@%%%##@%*#+%%%%%@@@%#+--............:--:..:::.......:::....:---........:--:.......:---:....:::::::::...::......:--:.........",
"......-#%%%@@@@@%%#**###%*@@@@@%@@@@%@@@@@@%#*+:......................................................................................................",
"......:*##%%%%%%%%#******%@@@@@@@@@@@@@@@@%%+*:.......................................................................................................",
".......++***#%%%%###*****@@@@@@@@@@@@@@@@@%#=-........................................................................................................",
"......:+****+###%###*+***@@@@@@@@@@@@@@@@@%+-.........................................................................................................",
".......:*#****#%###%#***=@@@@@@@@@@@@@@@@%%*--+===-:..................................................................................................",
"........+%%%#*+*#%#%%#**+*@@@@@@@@@@@@@%%%#=-=*##****++=--::..........................................................................................",
"........=#%%%*****#**##**=%@@@@@@@@@@@@%%#*-=++%%#####**+****++==--::.................................................................................",
"........=####%%#*#%*++*#*++%%##%%%%%%%@%#*==**=%%%######**++++**###%#########***+==---:...............................................................",
"........:#%%%##%%%%*+=+*%##*###*++**+#%#**+%+=-##%%####***+=+=+**%#####%%%%%%%%%##*###+++=-...........................................................",
".........#%%%%%%%%%%##*+#%*##***+*++++##++*#-=+########***+=+===+*%%%%%%##%%%%%##*###*++=++++-:.......................................................",
".........:*%%@@@%%@%%%*+++****+*++#**++*=-*#-++*#*#**###++=======++*#%%%%#%%%%%####******++++++-:.....................................................",
"...........*%@@%@@@@@@%#%******+++*=#%##*=++-***#*+****+*=========+=+#%%%%%%%%###***+*+++++++====-:-::::..............................................",
"............=%@@@@@@@@@@%##*+*#++++:-+=#*+=-=++*##++++=====---========##%#@%##*##***+*+++====+=---=+*****=+++=::::....................................",
".............:#@@@@@@@@@%@%%#*##*++*=--=*=*+=:-*#***+**===--==----====*%%@%%##%*#*****#**+======-:-==++==*+==*#*+=#******+==-:........................",
"..............-%@@@%@@@@@@@%%%##**++**+==-+++-:***##**+===-======-=---*%%@%#%#%*#######****+==---:-==+++-++++++++=-++==++******++==--:................",
"...............-%@@@@@@@@@@@@@%##**++++*+++=+=-=**##***++======+=+=---=%%%@#@%@#%##*#*****+++=-:::---===--===+==--==-=====+*+==+=======-:.............",
"................#@@@@@@@@@%@@@@@%%##*******+*+---+++++++++++==++++=-:--#%@@@@%%%##**#*****+++=--:::----:.--==-==---======-==+=-------=--::::..........",
"................:%@@@@@@@@@@@@@@@@@@%%##%###*+==**++==+==-+===++=++=:--#@%@%%%%%##***#***+==----::--:-+-:-:=-----::-==--=+-=--::::...::-..............",
".................-#@@@@@@@@@@@@@@@@@@@@@@%%%#***##*+====++=++*+=+=++--=*%#@%%%%%######*****+=-:.:-=:=-=:--:-=-::::-::-::-+-+--:-----:--=:-:::.........",
"..................+%@@@%@@@@@@@@@@@@@@@@@@%%%#%###***+=**+=++=+*+===---*%#@%%%%%%%%###******=-:::==-+----=---+----===+==+*++=====-:-.::::.::::........",
"..................=%@@@@%@@@@@@@@@@@@@%######%%%%%##**###*++*#*==+**+==#@%%@@@@%%#%###*****+=-:::=--=**+++-==+=+**+++++++=+----::::-------===:........",
"..................-%@%@@@@@@@@@@@@@@@%#%%######%%%%%%%%%#*+=++=##+==--=#%%@@@%%###%%##**+++=-:::+--*#*#*=+++*=+==-==---+=-==--+===++=-::.:***#+.......",
"...................*@@%%%%%@@%@@@@@@@@@%%%%%%%##%%%@%%%%%##+=#*+==+*=-=#%%%%%#%#####**#****+-::==-+##**+=+====-=-:-+-+-+=++++---:.......-***#+:.......",
"...................=%@%%%%@@@@@%%@@@%%#%%%%%%%%%@@@##%@%%%*#*+=##*-=*=#%%%%@@%%#####*******=-:=-:=**++**==---+-===+**+==-:............=*###+-.........",
"....................=%%%%@@@@@@%%%%@@%%%%##%#######%#*%@@@%#*=+###*+=*%%%%#%@@@%%%##******++-==::++**+**=-+--***+=-:..............:=*###*=............",
".....................*@@@@@@@%%%%%%#%%%%%##%%#####=+*@@@@@%#==+*+==+*%@%%@%%@%%%#####*****+=-----+++++*+---==:.................:++*+-:................",
"......................#@@@@@@@@@%%%%%%@@%%%%%%%#*++==*%@@%##+-#**++*#%%@@%%%%@@@%%###***++=::----++#%@%%*-............................................",
".......................=%@@@@:-+%@@@@%%@@%%%%%%#*##+=*+*%%%%+=---=*###%@@@@%%@@%%######*+-:=++==-==::-:...............................................",
"........................-%@@@=..:=*%@@@%%@@%%%%%##*#=#%+*#%#*#*++*##%%#%%@@@%@@@%######*+=+*++==-::...................................................",
"........................:#%@@:......+%@@%%@%%%%%@%#+#**@%%%%*+*#%######%%%%@@@@@%%####*#*##**+=+=-:...................................................",
".........................%%%=........:#%%@@@@%%%%%%%%%@@%@@%###*####%%##%%%@@@@@%%######%###****+=-:..................................................",
"........................=%%+...........-=+#@@@@@%%@@@@%%%@%####%%%%%%%%%%%%@@@@@@%%#########**#**+=:..................................................",
"........................:%%%+..............:=%%%@@@@@@%@@%%%%%%%%%%%%%%%%%%@@@@@@@%%%%%###%%#####*+=-:................................................",
".........................-%#=.................:+--=+*##%%%%%##%%@@@%%%#%%%%@@@@#=*@@%%%##%%%%%###**+=-................................................",
"..........................=##:..................................:#@@%%%%%%%%#+-...:#@@%%%%###%%%%#*++-................................................",
"............................-#:................................+%@@@@@@%##*:........-=#@@%%%####%@%*+=:...............................................",
"..............................::............................-+%@@@@@@@%*+:..............-#@@%%%##**##*=:..............................................",
"...........................................................=@@@@@@@@@@*-..................:+#@@%%##+==++:.............................................",
"..........................................................*@@@@@@@%####......................:+%@%%%#*=-==:...........................................",
".........................................................*@@@@@@@#+**+-.........................-%@%%%#*====-:........................................",
"........................................................*@@@@@%%%*%#-:............................=%@%%%#++==-........................................",
"......................................................-#@@@@@%%%*=:................................-#@@%%%%*=-:.......................................",
"....................................................:#@@%@@@%%#+....................................:%@@%@%%#+-.......................................",
"....................................................*@@%@@@@%#-......................................=@@%%%##*=:......................................",
"..................................................:#@%%%#%%@%=.......................................+%%@@%%%#=.......................................",
".................................................:#%#*+=#*=:.........................................=%%@@%%#+-.......................................",
".................................................==:....+:...........................................=%%@%%##+:.......................................",
".................................................=:..................................................*%%@@%##=:.......................................",

]
    for x in t2:
        print(x)


def make_lineage(se_dic, link_list):

    big_list = []

    lineage_dic = {}

    x0 = []
    x1 = []

    for x in link_list:
        x0.append(x[0])
        x1.append(x[1])

    line_starters = list(set([x for x in x0 if not x in x1]))
    line_enders = list(set([x for x in x1 if not x in x0]))

    for end in line_enders:
        # print('>>>', end)
     
        big_list.append(recursive_lineage(end, link_list, []))

       

    for x in big_list:
        if x[-1] not in line_starters:
            exit(f'unknown start {x[-1]}')

    return big_list



def recursive_lineage(a, link_list, lin_ls):

    """ 
    recursively passes over the link list building families based on the starts and ends of the tuples
    in the link list. 
    
    Returns:
        list -- list of family lines
    """
    lin_ls.append(a)
    for xs in link_list:
        # print('>', xs)
        x0, x1 = xs
        
        if x1 == a:
            # print(x1, x0)
            lin_ls = recursive_lineage(x0, link_list, lin_ls[:])[:]
    
    return lin_ls[:]



def make_family_dic(big_list):

    family_dic = {}
    family_counter = 0

    for family in big_list:

        for track_count, track in enumerate(family):

            try:
                parent = family[track_count+1]
            except IndexError:
                parent = 'None'
            try:
                family_dic[track][1].append(family[0])

            except KeyError:
                family_dic[track] = [family[-1], [family[0]], len(family) - track_count-1, parent]

        family_counter+=1

    return family_dic


def get_header_dic(head_line):
    dicHead = {}
    for n, x in enumerate(head_line):
        dicHead[x] = n
    return dicHead



def get_times(time, interval):

    mins = (time-1)*interval
    hours = mins/60
    days = hours/24

    return mins, hours, days

def build_link_dic(link_ls):
     
    link_dic = {}

    for x in link_ls:
        x0, x1 = x

        try:
            link_dic[x0].append(x1)
        
        except KeyError:
            link_dic[x0] = [x1]
        
    return link_dic


@jit
def fast_distance(x1, y1, z1, x2, y2, z2):
    return ((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)**0.5


def get_step_cutoff(pos_dic, end_time):

    """
    Calcuate how far cell travel on average in the last 10 frames
    """
    end_time = int(end_time)
    # print(end_time)
    distances = []

    for timeEnd in range(max(end_time-10, 1), end_time-1): # defaults to zero on short tracks 

        for cell in pos_dic[timeEnd]:
            try:
                x2, y2, z2 = pos_dic[timeEnd+1][cell]
            except KeyError:
                continue

            x1, y1, z1 = pos_dic[timeEnd][cell]
            fast_dis = fast_distance(x1, y1, z1, x2, y2, z2)

            distances.append(fast_dis)


    cut_off = mean(distances) * 10 # This is increased to prevent rejections was originally 4
    # print("mean dis: ", mean(distances))
    # print("cut off: ", cut_off)
    return cut_off


def get_distance(end_cell, start_cell, pos_dic, times):
    stTime, enTime = times

    x1, y1, z1 = pos_dic[enTime][end_cell]
    x2, y2, z2 = pos_dic[stTime][start_cell]

    return fast_distance(x1, y1, z1, x2, y2, z2)

def assign_only_closest_daughters(endCell, start_cells, pos_dic, cutoff, enTime, stTime, se_dic):
    
    dis_dic = {}
    group_dic = {}
    
    x1, y1, z1 = pos_dic[enTime][endCell]


    distances = []
    track_lengths = {} # I added this a potential extra information piece to resolve disputes, but is contenscious 
    for startCell in start_cells:
        x2, y2, z2 = pos_dic[stTime][startCell]
        dis = fast_distance(x1, y1, z1, x2, y2, z2)
        distances.append((dis, startCell))
        track_lengths[startCell] = se_dic[startCell][1] - se_dic[startCell][0]

    distances.sort()
    # print(distances)
    # pprint(track_lengths)
    # exit()

    for n, dis in enumerate(distances):
        if n < 2 and dis[0] < cutoff:
            try:
                group_dic[endCell].append(dis[1])
            
            except KeyError:
                group_dic[endCell] = [dis[1]]

        else:
            try:
                group_dic["None"].append(dis[1])
            
            except KeyError:
                group_dic["None"] = [dis[1]]


    return group_dic

def label_maybe(end_cell, start_cells):
    group_dic = {}
    group_dic[f"maybe:{end_cell}"] = start_cells
    return group_dic


def here_there_be_monsters2(start_cells, end_cells, pos_dic, cutoff, enTime, stTime, se_dic):
    net_dic = {}
    group_dic = {}
    # matched_dic = {}
    # un_matched_dic = {}
    # print(end_cells)
    # print(start_cells)

    # add exception for mothers matched with 3 cells instead of two incases where daughters outnumber potential mothers.

    if len(end_cells) == 1 and len(start_cells) > 2:
        close_cells = [s for s in start_cells if fast_distance(*pos_dic[enTime][end_cells[0]], *pos_dic[stTime][s]) < cutoff]
        if len(close_cells) > 2:
            return label_maybe(end_cells[0], close_cells)
        else:
            return assign_only_closest_daughters(end_cells[0], close_cells, pos_dic, cutoff, enTime, stTime, se_dic)

    for endCell in end_cells:
        x1, y1, z1 = pos_dic[enTime][endCell]

        for startCell in start_cells:
            x2, y2, z2 = pos_dic[stTime][startCell]

            dis = fast_distance(x1, y1, z1, x2, y2, z2)
            # print("Debug:",  startCell, endCell, dis, cutoff)
            if dis < cutoff:
                try:
                    currentdis = net_dic[startCell][0] 

                    if dis < currentdis:
                        net_dic[startCell] = (dis, endCell)
                
                except KeyError:
                    net_dic[startCell] = (dis, endCell)
    # print("netdic:", pprint(net_dic))
    for daughter in net_dic:
        try:
            group_dic[net_dic[daughter][1]].append(daughter)

        except KeyError:
            group_dic[net_dic[daughter][1]] = [daughter]

    max_group = 0
    for key in group_dic:
        if len(group_dic[key]) > max_group:
            max_group = len(group_dic[key])
        
    if max_group == 2:
        return group_dic
    
    # print(f"MAX group: {max_group}")

    orphans = []
    spinsters = [x for x in end_cells if x not in list(group_dic)]
    kidnappers = []
    
    mother_count = {}
    daughter_count = {}
    # print("GD", group_dic)
    # print(spinsters)

    for mother in group_dic:
        for daughter in group_dic[mother]:
            try:
                mother_count[mother] += 1
            except KeyError:
                mother_count[mother] = 1

            try:
                daughter_count[daughter] += 1
            except KeyError:
                daughter_count[daughter] = 1

            if mother_count[mother] > 2:
                kidnappers.append(mother)
            
            elif daughter_count[daughter] > 1:
                orphans.append(daughter)
                kidnappers.append(mother)
    # print("kidnappers",kidnappers) 
    # print("spinsters",spinsters)
    # print("orphans",orphans)
    if len(kidnappers) != 0:
        for childSnatcher in kidnappers:
            spinsters.append(childSnatcher)
            orphans += group_dic[childSnatcher]

        for mother in mother_count:
            x1, y1, z1 = pos_dic[enTime][mother]
            if mother_count[mother] == 1:
                for childSnatcher in kidnappers:
                    x2, y2, z2 = pos_dic[enTime][childSnatcher]
                    if fast_distance(x1, y1, z1, x2, y2, z2) < cutoff:
                        spinsters.append(mother)
                        orphans += group_dic[mother]

    spinsters = list(set(spinsters))
    orphans = list(set(orphans))


    if len(orphans) == 1 and len(spinsters) == 0:
        return group_dic
    
    elif len(orphans) == 0 and len(spinsters) == 1:
        return group_dic



    if len(orphans) == 0 and len(spinsters) == 0:
        return group_dic
    else:
        new_group = try_closest_distance(orphans, spinsters, pos_dic, enTime, stTime, cutoff)
    
    group_dic.update(new_group)
    # print(group_dic)
 
    return group_dic


def try_closest_distance(orphans, spinsters, pos_dic, enTime, stTime, cutoff):
    mother_list = spinsters
    daughter_list = orphans
    # print("HELP!")
    # print(mother_list, daughter_list)
    loops = 0
    while len(daughter_list) != 2*len(mother_list):
        loops += 1
        daughter_list.append("x")
        pos_dic[stTime]["x"] = (100_000, 100_000, 100_000)
        # print("stuck", len(daughter_list), len(mother_list))

        if loops > 1000:
            exit("ERROR: Can't balance mother and daughter numbers")
    all_distance = {}
    perma_count = 0
    for d_perm in itertools.permutations(daughter_list, 2*len(mother_list)):
        distance = 0

        for n, mother in enumerate(mother_list):
            x1, y1, z1 = pos_dic[enTime][mother]
            grp = d_perm[n*2:(n*2)+2]

            for daughter in grp:
                x2, y2, z2 = pos_dic[stTime][daughter]

                distance += fast_distance(x1, y1, z1, x2, y2, z2)

                if distance > cutoff/2.5:
                    distance += 5

        all_distance[distance] = d_perm
    

    best_match = all_distance[min(all_distance)]
    new_group = {}

    for n, mother in enumerate(mother_list):

        daughters = best_match[n*2: (n*2)+2]

        for daughter in daughters:
            if daughter == "x":
                continue
            try:
                new_group[mother].append(daughter)
            except KeyError:
                new_group[mother] = [daughter]

    return new_group





def assign_daughters(start_dic, end_dic, pos_dic, se_dic):

    """
    Takes start_dic, end_dic and pos_dic

    Should return list of tupels 
    """

    # print(start_dic)
    # print(end_dic)
    links_ls = []

    matched_times = [x for x in start_dic if x-1 in end_dic]

    for time in matched_times:

        stTime = time
        enTime = time-1
        
        if len(start_dic[stTime]) == 2 and len(end_dic[enTime]) == 1:
            print("Classic dvision")
            cutt_off = get_step_cutoff(pos_dic, enTime)

            distance = get_distance(end_dic[enTime][0],start_dic[stTime][0], pos_dic, (stTime, enTime))
            cutt_off = get_step_cutoff(pos_dic, enTime)

            if distance < cutt_off:
                print("It's a girl: ", end_dic[enTime][0], start_dic[stTime][0], cutt_off, distance)
                links_ls.append(( end_dic[enTime][0], start_dic[stTime][0]))

            distance = get_distance(end_dic[enTime][0],start_dic[stTime][1], pos_dic, (stTime, enTime))
            cutt_off = get_step_cutoff(pos_dic, enTime)

            if distance < cutt_off:
                print("It's a girl: ", end_dic[enTime][0], start_dic[stTime][1], cutt_off, distance)
                links_ls.append(( end_dic[enTime][0], start_dic[stTime][1]))
            

        elif len(start_dic[stTime]) == 1 and len(end_dic[enTime]) == 1:

            print("Death in the family?")
            distance = get_distance(end_dic[enTime][0],start_dic[stTime][0], pos_dic, (stTime, enTime))
            cutt_off = get_step_cutoff(pos_dic, enTime)

            if distance < cutt_off:
                print("It's a girl: ", end_dic[enTime][0], start_dic[stTime][0], cutt_off, distance)
                links_ls.append(( end_dic[enTime][0], start_dic[stTime][0]))

        else:
            print("Something more complicated")
            cut_off = get_step_cutoff(pos_dic, enTime)

            # print(start_dic[stTime])
            # print(end_dic[enTime])

            matched_pairs = here_there_be_monsters2(start_dic[stTime], end_dic[enTime], pos_dic, cut_off, enTime, stTime, se_dic)

            for endCell in matched_pairs:
                for startCell in matched_pairs[endCell]:
                    print("It's a girl: ", endCell, startCell, cut_off)
                    links_ls.append((endCell, startCell))


        # unmatched_times1 = [x for x in start_dic if x-1 not in end_dic]

        # for x in unmatched_times1:
        #     for orphan in start_dic[x]:
        #         links_ls.append(("None", orphan))

        # unmatched_times2 = [x for x in end_dic if x+1 not in start_dic]

        # for x in unmatched_times2:
        #     for spinster in end_dic[x]:
        #         links_ls.append((spinster, "None"))


    return links_ls

def output_start_and_ends_file_for_plotting2(se_dic, family_dic, pos_dic, experiment_path):
    
    outdir = os.path.join(experiment_path, os.path.split(experiment_path)[1]+f'_output_data')
    if not os.path.isdir(outdir):
        os.makedirs(outdir)

    outfile = open(os.path.join(outdir, "trecs2Positions.tsv"),'w')
    outfile.write("cell\ttime\tfamily\tx\ty\tz\n")
    # pprint(family_dic)
    for key in se_dic:
        # print(key)
        start, end = se_dic[key]    
        # key = '-'.join(sorted([]))
        try:
            family = family_dic[key][3]
        except KeyError:
            family = key
            # print("missing cell", key)
            # x, y, z = pos_dic[start][key]
            # outfile.write(f"{key}\t{start}\tNone\t{x}\t{y}\t{z}\n")

        x, y, z = pos_dic[start][key]
        outfile.write(f"{key}\t{start}\t{family}\t{x}\t{y}\t{z}\n")

        x, y, z = pos_dic[end][key]
        outfile.write(f"{key}\t{end}\t{family}\t{x}\t{y}\t{z}\n")

def cycle_files(experiment_path, family_dic, time_interval):

    today = datetime.date.today()
    d1 = today.strftime("%Y-%m-%d")

    outdir = os.path.join(experiment_path, os.path.split(experiment_path)[1]+f'_output_data')
    # print(outdir)
    if not os.path.isdir(outdir):
        os.makedirs(outdir)

    outfile_path = os.path.join(outdir, f'{d1}-output_data-T2.tsv')

    outfile = open(outfile_path, 'w')
    head_line = 'variable\tvalue\tunit\tchannel\timage\ttime\tmins\thours\tdays\ttrackID\tid\tfamily\tfull_track\tgeneration\tparent\n'
    outfile.write(head_line)
    generation_list = []
    fam_ls = []
    files_to_import = [x for x in os.listdir(experiment_path) if '.csv' in x]
    # print(files_to_import)
    if len(files_to_import) == 0:
        exit('No files found')
    head_ls = head_line.strip().split('\t')[:5]
    for fileX in files_to_import:
        # print(f'Importing: {fileX}')

        in_data = False

        with open(os.path.join(experiment_path, fileX), errors='ignore') as open_fileX:

            for line in open_fileX:

                if 'TrackID,' in line:
                    
                    in_data = True
                    split_line = line.lower().strip().split(',')
                    variable = split_line[0]
                    dicHead = get_header_dic(split_line)
                    dicHead['value'] = 0
                    continue

                elif not in_data:
                    continue

                # print(line)
                
                # value, Unit, Category, Channel, Time, TrackID, ID, NA = line.strip().split(',')

                split_line = line.strip().split(',')

                temp_dic = {}

                for key in dicHead:
                    temp_dic[key] = split_line[dicHead[key]]
                temp_dic['variable'] = variable
                TrackID = temp_dic['trackid']
                ID = temp_dic['id']
                Time = temp_dic['time']

                try:

                    family, full_track_ls, generation, parent = family_dic[TrackID]

                except KeyError:

                    family, full_track_ls, generation, parent = [TrackID, [TrackID], 0, 'None']

                mins, hours, days = get_times(float(Time), time_interval)

                for full_track in set(full_track_ls):
                    outls1 = []
                    for x in head_ls:
                        # print(x, temp_dic)
                        try:
                            outls1.append(temp_dic[x])

                        except KeyError:
                            outls1.append('NA')

                    outstr = '\t'.join([str(x) for x in outls1])+'\t'+'\t'.join([str(x) for x in [Time, mins, hours, days, TrackID, ID, family, full_track, generation, parent]])+'\n'
                    outfile.write(outstr)
                    generation_list.append(generation)
                    fam_ls.append(family)
                    
                    
                    # if 'Position' not in variable:
                    #     print(variable)

    outfile.close()
    famNumber = len(list(set(fam_ls)))
    return outfile_path, generation_list, famNumber

def get_mean_track_length(se_dic):
    length_ls = []
    for cell in se_dic:
        length_ls.append(se_dic[cell][1]-se_dic[cell][0])

    return mean(length_ls)

def generate_summary_data(output_dir, start_dic, args, dataBits):
    print(output_dir)
    outputFrame = pd.read_csv(output_dir, header=0, sep='\t')
    
    pprint(outputFrame)

    outputFrameSub = outputFrame[["time", "trackID"]].copy()
    outputFrameSub.drop_duplicates(inplace=True)

    timeCounts = outputFrameSub['time'].value_counts()
    timeCounts.reindex()
    print(timeCounts)
    print(type(timeCounts))



    

    outputFrameSub = outputFrame[["time", "generation"]].copy()
    print(outputFrameSub)
    genGroups = outputFrameSub.groupby("time")["generation"].max()

    print(genGroups)
    

    ls1 = []
    ls2 = []

    for n, x in enumerate(start_dic):
        if n == 0:
            continue

        ls1.append(x)
        ls2.append(len(start_dic[x]))

    divisionFrame = pd.DataFrame({"time":ls1, "nDivision":ls2})
    divisionFrame['t_binned'] = pd.cut(divisionFrame['time'], bins=5)

    # sns.lineplot(data=timeCounts)
    # plt.xlabel("Time point")
    # plt.ylabel("Cell count (n)")
    # plt.show()
    # plt.close()

    # sns.lineplot(data=outputFrameSub, x="time", y="generation", label="Mean")
    # sns.lineplot(data=genGroups, label="Max")
    # plt.xlabel("Time point")
    # plt.ylabel("Number of generations (n)")
    # plt.show()
    # plt.close()

    # sns.boxplot(divisionFrame, x="t_binned", y="nDivision")
    # plt.xticks(rotation=45, ha="right")
    # plt.xlabel("Time (binned)")
    # plt.ylabel("Number of Divisions")
    # plt.tight_layout() 
    # plt.show()
    # plt.close()



    fig = plt.figure(figsize=(8.27, 11.69))
    gs = fig.add_gridspec(6, 2)

    # Title
    fig.suptitle(f"{os.path.split(args.experiment_path)[-1]} Summary", fontsize=16, fontweight='bold')

    # Plot 1: Cell count over time (Top Left)
    ax1 = fig.add_subplot(gs[0:2, 0])
    sns.lineplot(data=timeCounts, ax=ax1)
    ax1.set_xlabel("Time point")
    ax1.set_ylabel("Cell count (n)")
    ax1.set_title("Cell Count Over Time")

    # Plot 2: Generations over time (Top Right)
    ax2 = fig.add_subplot(gs[0:2, 1])
    sns.lineplot(data=outputFrameSub, x="time", y="generation", label="Mean", ax=ax2)
    sns.lineplot(x=genGroups.index, y=genGroups.values, label="Max", ax=ax2)
    ax2.set_xlabel("Time point")
    ax2.set_ylabel("Number of generations (n)")
    ax2.set_title("Generations Over Time")
    ax2.legend()

    # Plot 3: Number of divisions (Bottom)
    ax3 = fig.add_subplot(gs[2:4, :])
    sns.boxplot(data=divisionFrame, x="t_binned", y="nDivision", ax=ax3)
    ax3.set_xticklabels(ax3.get_xticklabels(), rotation=45, ha="right", va="top")
    ax3.set_xlabel("Time (binned)")
    ax3.set_ylabel("Number of Divisions")
    ax3.set_title("Number of Divisions by Time (Binned)")

    # Text Comments (Bottom Right)
    ax4 = fig.add_subplot(gs[4, :])
    ax4.axis("off")
    generations_list, numberOfCells, meanTrackLength, famNumber = dataBits

    today = datetime.date.today()
    d1 = today.strftime("%Y-%m-%d")

    part1 = f"""
    Summary
    
    """

    part2 = f"""
    No. Cells: {numberOfCells}             
    Mean Track length: {meanTrackLength}           
    Number of families: {famNumber}
    Max generations: {max(generations_list)}
    Mean generations: {mean(generations_list)}

    tRecs2.0 2024. TMinchington. https://github.com/TMinchington/tRecs {d1}
    """

    # Place the text parts in different positions on the subplot
    ax4.text(0, 1, part1, fontsize=12, ha='left', va='top')  # Top section
    ax4.text(0, 0.5, part2, fontsize=10, ha='left', va='top')  # Middle section
    


    # Adjust the layout
    plt.subplots_adjust(hspace=0.3, bottom=0.1, top=0.93)  # Adjust bottom to give space for footer
    plt.tight_layout(rect=[0, 0, 1, 0.96])  # Leave space for the title
    plt.savefig(os.path.join(output_dir.replace(".tsv", "-summary.pdf")), dpi=300)
    # plt.show()
    plt.close()

    
def run_all(position_file, time_interval, experiment_path):

    print(f"pos file: {position_file}")

    se_dic, pos_dic = get_start_and_end(position_file)
  
    start_dic, end_dic = make_start_and_ends_dics(se_dic)
    numberOfCells = len(set(list(se_dic)))
    links_ls = assign_daughters(start_dic, end_dic, pos_dic, se_dic)
    
    big_list = make_lineage(se_dic, links_ls)

    family_dic = make_family_dic(big_list)

    output_start_and_ends_file_for_plotting2(se_dic, family_dic, pos_dic, args.experiment_path)
    outfile_path, generations_list, famNumber = cycle_files(experiment_path, family_dic, time_interval)
    add_positions_to_output(pos_dic, outfile_path, args.time, family_dic)

    dataBits = (generations_list, numberOfCells, get_mean_track_length(se_dic), famNumber)
    generate_summary_data(outfile_path, start_dic, args, dataBits)

    return generations_list, numberOfCells, get_mean_track_length(se_dic), famNumber


def add_positions_to_output(pos_dic, outfile_path, time_interval, family_dic):

    outfile = open(outfile_path, 'a')
    'variable\tvalue\tunit\tchannel\timage\ttime\tmins\thours\tdays\ttrackID\tid\tfamily\tfull_track\tgeneration\tparent\n'
    Unit = 'µm'
    for Time in pos_dic:
        for track in pos_dic[Time]:
            for variable, value in zip(['position_x', 'position_y', 'position_z'], list(pos_dic[Time][track])):
                TrackID = track
                try:

                    family, full_track_ls, generation, parent = family_dic[TrackID]

                except KeyError:

                    family, full_track_ls, generation, parent = [TrackID, [TrackID], 0, 'None']

                mins, hours, days = get_times(float(Time), time_interval)

                for full_track in set(full_track_ls):
                    outstr = '\t'.join([str(x) for x in [variable, value, Unit, 'na', 'na', Time, mins, hours, days, TrackID, 'na', family, full_track, generation, parent]])+'\n'
                    outfile.write(outstr)

    outfile.close()


def get_start_and_end(position_file):

    track_SE_dictionary = {}
    pos_dic = {}
    
    dataStart = False
    # print("HELLO!")
    with open(position_file) as o_track:
        
        for line in o_track:
            # print(line)
            if not line.startswith('Position X') and not dataStart:
                continue
            elif line.startswith('Position X') and not dataStart:
                dataStart = True
                continue
            
            # print(line)
            split_line = line.strip().split(',')[:9]
            PositionX, PositionY, PositionZ, Unit, Category, Collection, Time, TrackID, ID = split_line


            track_SE_dictionary = update_SE(TrackID, float(Time), track_SE_dictionary)
            
            try:
                pos_dic[float(Time)][TrackID] = (float(PositionX), float(PositionY), float(PositionZ))

            except KeyError:
                pos_dic[float(Time)] = {TrackID: (float(PositionX), float(PositionY), float(PositionZ))}
                


    return track_SE_dictionary, pos_dic


def open_log(args, position_file, generations_list,
             numberOfCells, 
             mean_track_length, 
             famNumber):
    
    expPath = args.experiment_path
    outdir = os.path.join(expPath, os.path.split(expPath)[1]+f'_output_data')
    log_path = os.path.join(outdir, "logfile.tsv")

    today = datetime.date.today()
    d1 = today.strftime("%Y-%m-%d")

    if os.path.isfile(log_path):
        log_file = open(log_path, "a")

    else:
        log_file = open(log_path, "w")
        log_file.write("path\tfile\tdate\ttimeInterval\tnumberOfCells\tmeanTrackLength\tmaxNumberOfGenerations\tmeanNumberOfGenerations\tnumberOfFamilies\n")
    
    log_file.write(f"{expPath}\t{position_file}\t{d1}\t{args.time}\t{numberOfCells}\t{mean_track_length}" + 
                   f"\t{max(generations_list)}\t{mean(generations_list)}\t{famNumber}\n")

    log_file.close()


if __name__ == "__main__":

    # Get all arguments from the commandline
    
    parser = argparse.ArgumentParser()
    parser.add_argument('experiment_path', help="The location of the folder which contains all of the output csv files from Imaris")
    parser.add_argument('--time', '-t', default=10, type=float,  help="the time interval in mins for the imaging, the default value is 10 minutes")
    args = parser.parse_args()
    
    position_file = os.path.join(args.experiment_path, [x for x in os.listdir(args.experiment_path) if 'Position' in x and 'Track' not in x][0])
    generations_list, numberOfCells, mean_track_length, famNumber = run_all(position_file, args.time, args.experiment_path)

    open_log(args, position_file, generations_list, numberOfCells, mean_track_length, famNumber)
  
    trecsNew()



    