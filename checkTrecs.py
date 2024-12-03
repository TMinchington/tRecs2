"""
Check tRecs
"""

import os
from pprint import pprint
import pandas as pd
import numpy as np

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("test_path")

    args = parser.parse_args()

    TEST_PATH = args.test_path

    family_path = os.path.join(os.path.join(TEST_PATH, "test_data"), "families.tsv")
    print(TEST_PATH)
    
    data_path = os.path.join(TEST_PATH, os.path.split(TEST_PATH)[-1]+"_output_data")
    try:
        trecsoutput = [x for x in os.listdir(data_path) if x.endswith("output_data.tsv")][-1]
    except IndexError:
        trecsoutput  = []
    trecs2output = [x for x in os.listdir(data_path) if x.endswith("output_data-T2.tsv")][-1]

    
    parent_list = []
    daughter_list = []

    with open(family_path) as open_fam:
        for n, line in enumerate(open_fam):
            if n==0:
                continue
            parent = line.strip("\n").split('\t')[0]
            trackID = line.strip("\n").split('\t')[-1]

            parent_list.append(parent)
            daughter_list.append(trackID)

    check_frame = pd.DataFrame({"mother": parent_list, "daughter": daughter_list})



    if trecsoutput:
        pass
                
                # print("match", parent, trackID, mama) 

    print("CHECKING T-2")
    parent_list = []
    daughter_list = []

    with open(os.path.join(data_path, trecs2output)) as open_trecs:
        for n, line in enumerate(open_trecs):
            if n==0:
                continue
            parent = line.strip("\n").split('\t')[-1]
            trackID = line.split('\t')[9]

            parent_list.append(parent)
            daughter_list.append(trackID)

    T2_frame = pd.DataFrame({"mother": parent_list, "daughter": daughter_list})
    T2_frame = T2_frame[T2_frame.mother != "None"]
    T2_frame.drop_duplicates(inplace=True)
    T2_frame.reset_index(inplace=True)
    del T2_frame['index']

    T2_frame.mother = [str(x) for x in T2_frame.mother]
    T2_frame.daughter = [str(x) for x in T2_frame.daughter]

    check_frame = check_frame[check_frame.daughter != "None"]
    check_frame.mother = [str(x) for x in check_frame.mother]
    check_frame.daughter = [str(x).replace(".0", "") for x in check_frame.daughter]

    check_frame['joined'] = check_frame.mother + " " + check_frame.daughter
    T2_frame['joined'] = T2_frame.mother + " " + T2_frame.daughter
    ls1 = list(check_frame['joined'])
    ls1.sort()
    ls2 = list(T2_frame['joined'])
    ls2.sort()
    true_list = []
    for x, y in zip(ls1, ls2):
        
        true_list.append(x==y)

        if not x==y:
            print(x, y, x==y)

    print("all correct:", all(true_list))