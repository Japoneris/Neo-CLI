#!/usr/bin/python3

"""
Implementation of the recursive `tree` command.
Store a result into a file which is readable by baobab
"""

import argparse
import json
import os

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Folder size visualizer')
    parser.add_argument("--path", type=str, default=".",
                       help="where to start the tree command")
    
    parser.add_argument("--save_path", type=str, default="tree.json",
                       help="Where to save the information.")
    args = parser.parse_args()

    PATH = args.path
    n_rm = len(PATH)+1
    
    lst_results = []
    for ptx, _, files in os.walk(PATH):
        lst_results.append({"path": ptx[n_rm:], "is_directory": True})
        
        path = ptx + "/"
        for file in files:
            name = path + file
            lst_results.append({"path": path[n_rm:] + file, 
                                "is_directory": False,
                               "size": os.path.getsize(name)})
            
            
    # Remove Root
    lst_results.pop(0)
    
    print("Recovered {} items".format(len(lst_results)))
    
    # Save
    with open(args.save_path, "w") as fp:
        json.dump(lst_results, fp, indent=True)
            
    
