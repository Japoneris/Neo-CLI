#!/usr/bin/python3
"""


File format: list of items

items: dictionary with keys:

- "path": str
- 'is_directory': bool
- 'updated_at': str

if `is_directory` is False:

- 'size': int,
- 'sha1_hash': str

We only use keys:

- "path"
- "is_directory"
- "size"

"""


import argparse
import json
import os
import sys 

import numpy as np
from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource
from bokeh.palettes import Inferno256
  
    
    

def get_max_depth(files, verbose=False):
    """
    Search how many files there are per level.
    """
    lvl = 0
    while True:
        n = len(list(filter(lambda x: x["path"].count("/") == lvl, data)))

        if n == 0:
            break

        else:
            if verbose:
                print("Lvl {}: {} \tfiles / folder".format(lvl, n))
            lvl += 1
            
    return lvl


def print_size(size_tot):
    """
    Convert a number of octet into a readable unit.
    
    :param size_tot: octet size.
    :rparam: tuple (float size, unit)
    """
    
    lst = ["ko", "Mo", "Go"]
    label = "o"
    for lb in lst:
        if size_tot > 1024:
            label = lb
            size_tot /= 1024
        else:
            break
            
    return (float(size_tot), label)




# Tree functions 

def add_item(item, dico):
    """Update the dictionary
    """
    name = item["path"]
    if item['is_directory']:
        dico[name] = {
            "size": 0,
            "children": {}
        }
        
    else:
        dico[name] = {"size": item["size"]}

        
def add_to_dict_location(item, dico):
    name = item["path"]
    subpath = name.split("/")
    
    size = 0
    if "size" in item:
        size = item["size"]
    
    reco = subpath[0]
    cnt = 1
    dic = dico
    while cnt < len(subpath):
        dic[reco]["size"] += size
        dic = dic[reco]["children"]
        reco += "/" + subpath[cnt]
        cnt += 1
        
    add_item(item, dic)
    
    return 


# Annulus function

def get_size(dico, rg=(0, 1), lvl=0):
    """Compute annulus size / location
    
    
    :param dico: tree to iterate on
    :param range: bounds
    :rparam: list of:
        - name
        - range (v0, v1)
        - level / ring
    """
    
    tot = sum(map(lambda x: x["size"], dico.values()))
    
    
    lst = []
    r0, r1 = rg
    vi = r0
    dr = r1 - r0
    for name, dic in dico.items():
        dv = dic["size"] / tot * dr
        
        v0 = vi
        vi = vi + dv
        lst.append((name, [v0, vi], lvl, dic["size"]))
        
        if "children" in dic:
            lst.extend(get_size(dic["children"], (v0, vi), lvl+1))
            
    return lst
        

        

    
if __name__ == "__main__":

    os.makedirs("html", exist_ok=True)
        
    parser = argparse.ArgumentParser(description='Folder size visualizer')
    parser.add_argument("path", type=str,
                       help="File where size info is stored")
    
    parser.add_argument("--sub_path", type=str, default="",
                       help="To limit the memory map to a folder.")
    
    parser.add_argument("--lvl", type=int, default=-1,
                       help="Maximum recursion level. If -1, no limit.")
    args = parser.parse_args()

    
    # Load the content of the file
    data = None
    with open(args.path, "r") as fp:
        data = json.load(fp)
        
    print("Gathered info about {} files".format(len(data)))

    # Print number of files per level. Debug mode
    get_max_depth(data, verbose=True)
    
    # Construct the tree
    """
    
    {
    `name_folder`: {"size": xx, "children": {...}},
    `name_file`: {"size": xx}
    }
    """
    dic_tree = {}
    
    # Increment with the other levels
    lvl = 0

    while True:
        valid = list(filter(lambda x: x["path"].count("/") == lvl, data))

        if len(valid) == 0:
            break

        for item in valid:
            add_to_dict_location(item, dic_tree)

        lvl += 1

        
    if args.sub_path != "":
        words = args.sub_path.split("/")
        reco = ""
        for wd in words:
            reco += wd
            dic_tree = dic_tree[reco]["children"]
            reco += "/"
        
        
    # Get annulus information for files
    # Annulus get degrees as input
    lst_sizes = get_size(dic_tree, rg=(0, np.pi*2), lvl=0)
    # [Name, (r0, r1), lvl, size]

    
    if args.lvl >= 0:
        lst_sizes = list(filter(lambda x: x[2] <= args.lvl, lst_sizes))
        lvl = args.lvl
        
        
        
    size_name = []
    for xx in lst_sizes:
        s = xx[3]
        si, unit = print_size(s)
        size_name.append('{:.4} {}'.format(si, unit))
        
    
    dic_data = {
        "r0": list(map(lambda x: x[2]+1, lst_sizes)),
        "r1": list(map(lambda x: x[2]+2, lst_sizes)),
        "a0": list(map(lambda x: x[1][0], lst_sizes)),
        "a1": list(map(lambda x: x[1][1], lst_sizes)),
        "size": size_name,
        "name": list(map(lambda x: x[0], lst_sizes)),
        "color": [Inferno256[int(255 * (x[1][0] + x[1][1])/(4*np.pi))] for x in lst_sizes] 
               }
        
        
    # Prepare the figure
    
    source = ColumnDataSource(dic_data)
    
    TOOLTIPS = [
    ("name", "@name"),
    ("size", "@size"),
    ]


    # Configuration of ranges
    L2 = lvl + 2
              
        
    S_tot = sum(list(map(lambda x: x["size"], dic_tree.values())))
    si, unit = print_size(S_tot)
    
    
    p = figure(width = 700, height = 700, tooltips=TOOLTIPS,
              x_range=[-L2, L2],
              y_range=[-L2, L2],
              title="Memory map. {} elements, {:.4} {}".format(len(size_name), si, unit),
              )
    

    p.xaxis.major_tick_line_color = None  # turn off x-axis major ticks
    p.xaxis.minor_tick_line_color = None  # turn off x-axis minor ticks

    p.yaxis.major_tick_line_color = None  # turn off y-axis major ticks
    p.yaxis.minor_tick_line_color = None  # turn off y-axis minor ticks
    p.xaxis.major_label_text_font_size = '0pt'  # turn off x-axis tick labels
    p.yaxis.major_label_text_font_size = '0pt'  # turn off y-axis tick labels
    p.xgrid.visible = False
    p.ygrid.visible = False

    p.annular_wedge(x = 0, y = 0, inner_radius ="r0",
                       outer_radius ="r1", start_angle = "a0", 
                       end_angle = "a1", line_color = "black", 
                       source=source, line_alpha=0.3,
                       fill_color ="color")
    
    path_save = "html/Map_{}_{}.html".format(args.path.rsplit("/")[-1].rsplit(".", 1)[0], lvl)
    print("Saving the map at {}".format(path_save))
    output_file(path_save,
                title="Memory map /{}.".format(args.sub_path))
    
    show(p)
    

    