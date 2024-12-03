"""
tRecs2

Description: track Reconstruction tool for dividing cells in imaris

tRecs2 improves on the accuracy of tRecs to provide more reliable track joining. 

The purpose is to link daughter cells to their mothers when cells are tracked division to division in imaris

Author: Thomas Minchington
Date: 2024-11-13
Usage: python tRecs2.py [-h] [--time TIME] experiment_path


"""

import argparse
import os

from tRecs import get_start_and_end, make_start_and_ends_dics, get_children

def build_link_dic(link_ls):
     
    link_dic = {}

    for x in link_ls:
        x0, x1 = x

        try:
            link_dic[x0].append(x1)
        
        except KeyError:
            link_dic[x0] = [x1]
        
    return link_dic


def run_all(position_file):
     
    se_dic, pos_dic = get_start_and_end(position_file)
    start_dic, end_dic = make_start_and_ends_dics(se_dic)
    link_ls = get_children(start_dic, end_dic, pos_dic)
    # link_dic = build_link_dic(link_ls)
    big_list = make_lineage(se_dic, link_ls)
    family_dic = make_family_dic(big_list)

      

if __name__ == "__main__":

    # Get all arguments from the commandline

    parser = argparse.ArgumentParser()
    parser.add_argument('experiment_path', help="The location of the folder which contains all of the output csv files from Imaris")
    parser.add_argument('--time', '-t', default=10, type=float,  help="the time interval in mins for the imaging, the default value is 10 minutes")
    args = parser.parse_args()

    position_file = os.path.join(args.experiment_path, [x for x in os.listdir(args.experiment_path) if 'Position' in x and 'Track' not in x][0])

    run_all(position_file)

    