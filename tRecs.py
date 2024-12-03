"""
tRecs
"""

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


def get_start_and_end(position_file):

    track_SE_dictionary = {}
    pos_dic = {}
    
    dataStart = False

    with open(position_file) as o_track:

        for line in o_track:
            print(line)
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


def get_closest_end(enders, starters, end, pos_dic):

    """ finds the closest start cell to the supplied end cell
    
    Returns:
        str -- id of the mother cell
    """

    from pprint import pprint as pp
    dis_dic = {}
    # pp(pos_dic[end+1])

    # print(starters)
    # print(enders)

    for endCell in enders:
    
        stx, sty, stz = pos_dic[end+1][starters[0]]
        endx, endy, endz = pos_dic[end][endCell]

        dis = (stx-endx)**2 + (sty-endy)**2 + (stz-endz)**2

        dis_dic[dis] = [(endCell, starters[0])]

    return dis_dic[min(dis_dic)]


def optimise_smallest_distance(enders, starters, end, pos_dic):

    import itertools
    import numpy as np
    import pprint as pp

    if len(starters) == 1:
        return get_closest_end(enders, starters, end, pos_dic)

    if len(starters) > 2*len(enders):

        # exit(f'Too many daugters: {len(starters)} daughters for {len(enders)} parents')
        enders += ['blank']

    if len(starters) != 2*len(enders):
        starters += ['blank']*(2*len(enders)-len(starters))

    total_dis_dic = {}

    # print(list(itertools.permutations(starters, 4)), enders)
    loop= 0

    if len(starters) != 2*len(enders):
        # print(enders)
        # print(starters)
        exit('count error')

    # if "1000052577" in enders:
    #     print(starters)
    #     print(enders)

    for startCells in itertools.permutations(starters, len(enders)*2):
        tot_dis = 0
        loop += 1

        for endCell, stCellgroup in zip(enders, np.array_split(startCells, len(enders))):
            if len(stCellgroup) != 2:
                # print(endCell, stCellgroup, len(enders), len(startCells))
                # print(enders)
                # print(starters)
                exit('broken_start')
            for stC in stCellgroup:

                if stC == 'blank' or endCell == 'blank':
                    tot_dis += 10000
                    continue

                stx, sty, stz = pos_dic[end+1][stC]
                endx, endy, endz = pos_dic[end][endCell]

                dis = (stx-endx)**2 + (sty-endy)**2 + (stz-endz)**2

                tot_dis += dis
                # print(tot_dis)
        total_dis_dic[tot_dis] = (enders, startCells)
    # pp.pprint(total_dis_dic)

    min_dis = min(total_dis_dic)

    linked = []
    ender_Cells, start_Cells = total_dis_dic[min_dis]
    for endCell, stCellgroup in zip(ender_Cells, np.array_split(start_Cells, len(ender_Cells))):
        for stC in stCellgroup:
            linked.append((endCell, stC))

    # if "1000052577" in enders:
    #     print(linked)
    #     exit()

    return linked


def optimise_smallest_distance_with_intensity(enders, starters, end, intense):

    import itertools
    import numpy as np
    import pprint as pp

    if len(starters) > 2*len(enders):

        # exit(f'Too many daugters: {len(starters)} daughters for {len(enders)} parents')
        enders += ['blank']

    if len(starters) != 2*len(enders):
        starters += ['blank']*(2*len(enders)-len(starters))

    total_dis_dic = {}

    # print(list(itertools.permutations(starters, 4)), enders)
    loop= 0

    for startCells in itertools.permutations(starters, 4):
        tot_dis = 0
        loop += 1

        for endCell, stCellgroup in zip(enders, np.array_split(startCells, len(enders))):
            
            for stC in stCellgroup:

                if stC == 'blank' or endCell == 'blank':
                    tot_dis += 10000
                    continue

                stx, sty, stz = pos_dic[end+1][stC]
                endx, endy, endz = pos_dic[end][endCell]

                dis = (stx-endx)**2 + (sty-endy)**2 + (stz-endz)**2

                tot_dis += dis

        total_dis_dic[tot_dis] = (enders, startCells)
    # pp.pprint(total_dis_dic)

    min_dis = min(total_dis_dic)

    linked = []
    ender_Cells, start_Cells = total_dis_dic[min_dis]
    for endCell, stCellgroup in zip(ender_Cells, np.array_split(start_Cells, len(ender_Cells))):
        for stC in stCellgroup:
            linked.append((endCell, stC))

    return linked
        

def select_children(enders, starters, pos_dic, end):
    links = []
    if len(enders) > 1:
        
        # print(f'{len(enders)} enders | {len(starters)} starters')
        # links.append(f'{len(enders)} enders')
        links += optimise_smallest_distance(enders[:], starters[:], end, pos_dic)

    elif len(starters) > 2:

        # print(f'{len(starters)} new starter')

        # links.append(f'{len(enders)} enders')

        links += optimise_smallest_distance(enders[:], starters[:], end, pos_dic)
        

    else:

        for startCell in starters:

            links.append((enders[0], startCell))

    return links


def missing_links(link_list):

    """removes any links which are joined to a 'blank' cell
    
    Returns:
        list -- list of reall connections with the 'blanks' removed.
    """

    missing = [x for x in link_list if 'blank' in x]

    links = [x for x in link_list if not 'blank' in x]

    # print('missing: ', missing)
    # print('links: ', links)

    return links


def get_children(start_dic, end_dic, pos_dic):

    """ find the children of a cell base on the start and end positions of all cells
    
    Returns:
        list -- list of tuples linking one cell to another.
    """

    # pos_dic = 'temp'
    link_list = []

    for end in end_dic:

        if end+1 in start_dic:
            
            link_list += select_children(end_dic[end], start_dic[end+1], pos_dic, end)

        else:
            continue
            # print(end, 'end')

    return missing_links(link_list)


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
            print(x1, x0)
            lin_ls = recursive_lineage(x0, link_list, lin_ls[:])[:]
    
    return lin_ls[:]


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



def get_times(time, interval):

    mins = (time-1)*interval
    hours = mins/60
    days = hours/24

    return mins, hours, days


def trecs2():
    print("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWKkkxdxkxxxocccldXMMMMMMMMMMMMM")
    print("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWXOocloxddddc;,,'';dXMMMMMMMMMMMM")
    print("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMW0o;,;cllclc;,;'...'lONMMMMMMMMMMM")
    print("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNkc';lol:;c:'.','...':xXMMMMMMMMMMM")
    print("MMMMMMMMMMMMMMMWWMMMMWKkkxxkO0NWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMXx:,coo:;;;;'..,'...'';dXMMMMMMMMMMM")
    print("MMMMMMMMMMMMMM0coXMMM0,.;lll:,,oXMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWKo,,::;,,,;;,...,....',cxXMMMMMMMMMMM")
    print("MMMMMMMMMMMMN0: .dk0W0'.kMMMW0,.oWMMWX0OOKNMMMMMMWX0OO0XWMWKOO0XWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWNKOd:.',,,,;,,''..'.....';cd0NMMMMMMMMMMM")
    print("MMMMMMMMMMMMXd, .:lkN0'.kMMMW0,.dWMKo;clc;;kNMMXd;;clllkNO:;clcxNMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWXOdl;'....''',;:;,....;;...,cxKNWMMMMMMMMMMMM")
    print("MMMMMMMMMMMMMMd.,KMMM0' :ddoc,;xNMK:.dNMW0,.kWX:.cKWMMWWNl.:KWWWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMXx;.....''.;cc:;,,'........'lOXWMMMMMMMMMMMMMMM")
    print("MMMMMMMMMMMMMMx.,KMMM0' ;ool,.:0MMx..:lllc'.lNk.,0MMMMMMM0c,,:d0WMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM0:.....';:;clllc;.........,l0MMMMMMMMMMMMMMMMMM")
    print("MMMMMMMMMMMMMMx.,KMMM0'.kMMMXl.;KMx..dkkkkkOXWk..OMMMMMMMMWXOl..xWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM0c..',:cccccclc;..   ....';dXMMMMMMMMMMMMMMMMMM")
    print("MMMMMMMMMMMMMMk..d0XW0'.kMMMM0,.dWXc.:kKKK0KWMNo.'o0KK0KN0OKKk,.xWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM0:..';cc::c::::'     .....;dKMMMMMMMMMMMMMMMMMM")
    print("MMMMMMMMMMMMMMNk::ckWKl:0MMMMWk;oNMNOlcccllkNMMW0oc:cllOXxcccclkNMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMO;...',,;;:c;,;;.   ......,lONMMMMMMMMMMMMMMMMM")
    print("MMMMMMMMMMMMMMMMWWWWMMWWMMMMMMMWWMMMMMWWWWWMMMMMMMMWWWWMMMWWWWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMXd,....';;;,'.';:;.. .......,dXMMMMMMMMMMMMMMMMM")
    print("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNx,.....,,'....,:cc:. ........;xNMMMMMMMMMMMMMMMM")
    print("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNk:'....'......',::cc:........';oOKNWMMMMMMMMMMMMM")
    print("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWNkl,..........',;:cccccc,',::clodxOOO0NWMMMMMMMMMMM")
    print("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWNK0kdl:,.........''',:cc:;;::;;;;:oxxkOOOkkO0KNWMMMMMMM")
    print("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWWWWWWWWWWNNNNNNNNNNK0Oxdollc;,'...........''''''''.'',,''';:loxk0Okxddk0KNWMMM")
    print("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWNKOxddxxxxxddoooddxxxxdoool:;;;;;'..............''..........'',,;;:clloxdooolokNMM")
    print("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWNX0Oxooolclllc:::;;;;;:coddolcc;,',,,;;,'.......''...............''''',;;,',;;;;,'':0MM")
    print("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWWX0kdoolccccllllloolc:;,,;;;cllc;;;;;;;,,,,,''...   ...............''.',,;,,,,'.........;kMM")
    print("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWNX0OkxxxxdddxkOOkxxxoc:;clllcccclllccllolllc::clc:;,,;;;,',;;;,.....   ..  ................',,,''''.......'':OMM")
    print("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWNKOxol:;;;,,,'''',;:c:;;::::clolc:::::;;;;;;:cclc:;;:;;;,'...',,'......  ... ..     .............',;;:loddxxxkkkO0NMM")
    print("MMMMMMMMMMMMMMMMMMMMMMMMMMMWNK0kxo:,'',,;;;,,'''''',,;::::::;;:::;;;;::;,,,,;:;;::;,,,;;'...';,'..       ...         .......,;coxk0KXNWWMMMMMMMMMMMMMM")
    print("MMMMMMMMMMMMMMMMMMMMMMWXKOxoc:::;;,''',,;;;,,,','''..',,'''''',,;,,,;::;;;,,,,,'',,,''''''',,........       .....  .....,lx0XNWMMMMMMMMMMMMMMMMMMMMMMM")
    print("MMMMMMMMMMMMMMMWNXK0kxoc;;;;,,,;,,'''',,,,;::;,,;;,'.''''''...',;,,;'',,,;;;,'........''','......'...................':d0NWMMMMMMMMMMMMMMMMMMMMMMMMMMM")
    print("MMMMMMMMMWNXKOkxoll:;,,,'',,,,;;,'',,,,,;;,,;:;;;::;'''........'',;;,''...'','......',;;,,'....''............ .....:d0NWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")
    print("MMMWNXKOkdllc::::;;,,,,'..',,,;;,..',,,,;;,',;;;;;;,'............',,,,,'......'...',,,,,,,'.....................;oOXWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")
    print("MXxllc::;,,,,,,'''''''....',,'',,''''''',,,,;;;;;;'..............'''',',,'.............'','........'''''.'',;cdOXWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")
    print("MO:',,,',,,'''''''.........''..'.',,''''',,,,;;;;,'..............'..''.',,,,,'............''.........';codkKNWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")
    print("MO:',,,,,'''''.'''...'......'.....,;,'''',,',,,,'.....................'',''''.....  ................'oKNWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")
    print("MO:'.'''.........................'','..',;;;;,'''......................'...........................;kNMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")
    print("MO,................................''''',;;,,,,,'................................'.....   .......'c0WMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")
    print("Mk'............       ..   .......'',,,;;;,,'',,'.............................';;'...      .....,oKMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")
    print("Mk'.....................   .......'''',;;;,,'''................................'..        .....;xNMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")
    print("Mk'.......................  .......''.',,,,,''.............',,''..''''..........      ......',cOWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")
    print("Mk'..................    ...............'''.'.....   ...........',''............  ......''..;oKWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")
    print("Wk,.......'''''''''.............................    .  ............................';:cc:,.'oKWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")
    print("MXOkOOOOOO00000000000000d;.....................           ......................;cd0XN0o:'.cKMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")
    print("MMMMMMMMMMMMMMMMMMMMMMNOl:;;,''............              ....................:okKWMMWO;...:0WMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")
    print("MMMMMMMMMMMMMMMMMMMMWXxc:::;;,'............            ...................':dXWMMMMMWKOOO0XWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")
    print("MMMMMMMMMMMMMMMMMMMNOl::;,,,,''...........     .........',,........     .,kXWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")
    print("MMMMMMMMMMMMMMMMMWXxccc:'...................cdddddoodxk0KKd;.....       ,kWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")
    print("MMMMMMMMMMMMMMMMXkolc:;,..................,xNMMMMMMMMMMMNx:'....      .;OWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")
    print("MMMMMMMMMMMMMMN0dc:;,''''...........    .:0WMMMMMMMMMMMNx;'...',;:lodkOXWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")
    print("MMMMMMMMMMMMMNkl:;,'''','...........   .cKMMMMMMMMMMMMWOc:cldk0XNWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")


def get_header_dic(head_line):
    dicHead = {}
    for n, x in enumerate(head_line):
        dicHead[x] = n
    return dicHead


def cycle_files(experiment_path, family_dic, time_interval):

    import os
    import datetime

    today = datetime.date.today()
    d1 = today.strftime("%Y-%m-%d")

    outdir = os.path.join(experiment_path, os.path.split(experiment_path)[1]+f'_output_data')
    print(outdir)
    if not os.path.isdir(outdir):
        os.makedirs(outdir)

    outfile_path = os.path.join(outdir, f'{d1}-output_data.tsv')

    outfile = open(outfile_path, 'w')
    head_line = 'variable\tvalue\tunit\tchannel\timage\ttime\tmins\thours\tdays\ttrackID\tid\tfamily\tfull_track\tgeneration\tparent\n'
    outfile.write(head_line)

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
                    # if 'Position' not in variable:
                    #     print(variable)

    outfile.close()

    return outfile_path


def add_positions_to_output(pos_dic, outfile_path, time_interval):

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


def output_start_and_ends_file_for_plotting(se_dic, family_dic, position, experiment_path):
    
    outdir = os.path.join(experiment_path, os.path.split(experiment_path)[1]+f'_output_data')
    if not os.path.isdir(outdir):
        os.makedirs(outdir)

    outfile = open(os.path.join(outdir, "testPositions.tsv"),'w')
    outfile.write("cell\ttime\tfamily\tx\ty\tz\n")
    # pprint(family_dic)
    for key in se_dic:
        print(key)
        start, end = se_dic[key]    
        # key = '-'.join(sorted([]))
        try:
            family = family_dic[key][3]
        except KeyError:
            family = key
            print("missing cell", key)

        x, y, z = pos_dic[start][key]
        outfile.write(f"{key}\t{start}\t{family}\t{x}\t{y}\t{z}\n")

        x, y, z = pos_dic[end][key]
        outfile.write(f"{key}\t{end}\t{family}\t{x}\t{y}\t{z}\n")
    

    


if __name__ == "__main__":

    from pprint import pprint
    import os
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('experiment_path', help="The location of the folder which contains all of the output csv files from Imaris")
    parser.add_argument('--time', '-t', default=10, type=float,  help="the time interval in mins for the imaging, the default value is 10 minutes")

    args = parser.parse_args()

    position_file = os.path.join(args.experiment_path, [x for x in os.listdir(args.experiment_path) if 'Position' in x and 'Track' not in x][0])

    test_track = position_file

    se_dic, pos_dic = get_start_and_end(test_track)

    # pprint(se_dic)

    start_dic, end_dic = make_start_and_ends_dics(se_dic)

    # for track in se_dic:

    #     print(track, '\t'.join([str(x) for x in se_dic[track]]))

    # for start in start_dic:

    #     print('start', start, start_dic[start])

    # for end in end_dic:

    #     print('end', end, end_dic[end])

    link_ls = get_children(start_dic, end_dic, pos_dic)
    # pprint(link_ls)
    
    link_dic = {}

    for x in link_ls:
        try:
            link_dic[x[0]].append(x[1])
        
        except KeyError:

            link_dic[x[0]] = [x[1]]
    
    # exit()

    # pprint(link_dic)

    big_list = make_lineage(se_dic, link_ls)

    family_dic = make_family_dic(big_list)
    # print(big_list)
    # print('\n\nfamily dictionary:')
    # pprint(family_dic)
    # print('\n-----------------------')
    output_start_and_ends_file_for_plotting(se_dic, family_dic, pos_dic, args.experiment_path)
    outfile_path = cycle_files(args.experiment_path, family_dic, args.time)
    # outfile_path = outfile_path.replace(".tsv", "_debug.tsv") # enable when debugging
    add_positions_to_output(pos_dic, outfile_path, args.time)

    trecs2()

    # pprint(link_dic)