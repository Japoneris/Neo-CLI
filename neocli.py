#!/usr/bin/python3

import argparse
import getpass
import hashlib
import json
import os
import requests
import sys

PATH_API = "./API_KEY.txt"
URL_API = 'https://neocities.org/api/'

COLOR_DEFAULT = "\033[0;37;40m"
COLOR_DIR  = "\033[1;34;40m"
COLOR_FILE = "\033[1;32;40m"

"""
Format received from "list"


For a file:

{'path': 'README.md',
  'is_directory': False,
  'size': 695,
  'updated_at': 'Mon, 22 May 2017 21:16:30 -0000',
  'sha1_hash': '6a170acefaeffed4a82b5ed096b8d6e105c12d01'},

For a directory:

{'path': 'blg/page2',
  'is_directory': True,
  'updated_at': 'Sat, 09 Apr 2022 12:15:43 -0000'},

"""

def recursively_search_files(base, d=6):
    
    if d == 0: # Security
        return []

    base = base.rstrip("/") + "/" # Be sure you have the ending slash.

    lst = []
    for filename in os.listdir(base):
        if os.path.isdir(base + filename):
            lst.extend(recursively_search_files(base+filename, d-1))

        else:
            lst.append(base + filename)
    
    return lst

def display_item(file_info, l_prune=0, date=False, size=False, hs=False, nmax=20):
    """Items' printer

    :param file_info: json dictionnary
    :param l_prune: integer, number of characters to drop corresponding to the base name.
    :param data: True to print date
    :param size: True to print document size
    :param hs: True to print document hash.
    :param nmax: size of the path column
    """

    if file_info["is_directory"]:
        print("\t{}{}{}/{}".format(
                COLOR_DIR,
                file_info["updated_at"] + " \t" if date else "",
                file_info["path"][l_prune:],
                COLOR_DEFAULT)
                )

    else:
        print("\t{}{}{}\t{}\t{}{}".format(
                COLOR_FILE,
                file_info["updated_at"] + " \t" if date else "",
                file_info["path"][l_prune:] + " " * (nmax + 2 - l_prune - len(file_info["path"])),
                file_info["size"] if size else "",
                file_info["sha1_hash"] if hs else "",
                COLOR_DEFAULT,
                )
             )

    return

def get_tree(path):
    """Allows to list all the files recursively in a folder
    """
    if os.path.isdir(path):
        path = path.rstrip("/") + "/"
        lst = []
        for file in os.listdir(path):
            lst.extend(get_tree(path + file))
        return lst

    else:
        return [path]


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Neo-CLI, a CLI for Neocities website management.')
    #parser.add_argument("cmd", type=str, help="Option.")
    

    subparsers = parser.add_subparsers()

    # Retrieve key
    parser_auth = subparsers.add_parser('auth', help="Authentication.")
    parser_auth.set_defaults(cmd='auth')

    # Key storage
    parser_key = subparsers.add_parser('add_key', help="Would save the provided key into a file.")
    parser_key.set_defaults(cmd='add_key')
    parser_key.add_argument("key", type=str, help="Neocities API key.")
    parser_key.add_argument("-f", action="store_true", help="Replace an existing key.")


    # Info
    parser_info = subparsers.add_parser('info', help="Allows to get information about another website. Does not require API key.")
    
    parser_info.set_defaults(cmd='info')
    parser_info.add_argument("website", type=str, help="The website you want info about. Return JSON info.")
    

    # Listing
    parser_list = subparsers.add_parser('list', help="Help you to list documents/folders of your website.")
    
    parser_list.set_defaults(cmd='list', help="List the documents you have on your website.")
    parser_list.add_argument("--path", default="", type=str,
            help="Filter according to the path.")
    parser_list.add_argument("--files_only", action="store_true",
            help="If activated, do not list directories.")
    parser_list.add_argument("--dirs_only", action="store_true",
            help="If activated, do not list files.")
    parser_list.add_argument("-r", "--rec", action="store_true",
            help="Recursive. Show alls items that can be reached from here.")
    parser_list.add_argument("-d", "--date", action="store_true",
            help="Display modificatio date.")
    parser_list.add_argument("--hash", action="store_true",
            help="Display hash.")
    parser_list.add_argument("--size", action="store_true",
            help="Display document size.")
 
    # Update files that have been modified and new files (uncomplete)
    parser_opti = subparsers.add_parser('opti', help="Make an optimal update of all the files that changed.")
    parser_opti.set_defaults(cmd='opti', help="Compare your website to your repo.")
    parser_opti.add_argument("path", type=str,
            help="Location of your site content.")
    parser_opti.add_argument("--debug", action="store_true",
            help="Only list what will be updated.")


    # Size of a folder
    parser_size = subparsers.add_parser('size', help="Get the size of a folder.")
    
    parser_size.set_defaults(cmd='size', help="Count the total size.")
    
    parser_size.add_argument("--path", default="", type=str, help="Folder to investigate.")
    parser_size.add_argument("--save", default=False,action="store_true",
            help="Save file information into a default file `size.txt`.")


    # Adding files
    parser_update = subparsers.add_parser('update', help="Push files to your website")
    
    parser_update.set_defaults(cmd='update', help="Update command.")
    parser_update.add_argument('local_files',  type=str, nargs='+',
                    help='Files to upload.')
    parser_update.add_argument("--remote_path", default="", type=str,
            help="Where to push documents.")

    parser_update.add_argument("--rec", action="store_true",
            help="Would recursively add the content of a folder.")

    # Delete documents / folders
    parser_delete = subparsers.add_parser('delete', help="Delete files or directory.")
    
    parser_delete.set_defaults(cmd='delete', help="Remove items.")
    parser_delete.add_argument('remote_files',  type=str, nargs='+',
                    help='Remote files or dir to remove.')

    args = parser.parse_args()
    
    if args.cmd == "auth":
        print("== Authentication ==")
        user = input("Input username (lowercase): ")
        password = getpass.getpass("Input password: ")
        
        resp = requests.get("{}key".format(URL_API), auth=(user, password))
        
        if resp.status_code == 200:
            api_key = json.loads(resp.content.decode())["api_key"]
            print("Success !")
            print("Storing you API key at {}".format(PATH_API))
            with open(PATH_API, "w") as fp:
                fp.write(api_key)

        else:
            print("Error code: {}".format(resp.status_code))
            print(resp.content.decode())


    elif args.cmd == "add_key":
        print("== Manually add the key ==")
        print("Saving key `{}` at {}".format(args.key, PATH_API))
        
        
        if os.path.exists(PATH_API) & (args.f == False):
            print("Error: A key already exist. Try `-f` to force replacing it")
        else:
            with open(PATH_API, "w") as fp:
                fp.write(args.key)


    elif args.cmd == "info":
        print("== Get website info ==")
        VERB = "info"
        resp = requests.get("{}{}".format(URL_API, VERB), data={"sitename": args.website})
        if resp.status_code == 200:
            print(resp.content.decode())
        else:
            print("Error")
            print(resp.content.decode())
    
    elif args.cmd in ["list", "size", "update", "delete", "opti"]:
        if os.path.exists(PATH_API) == False:
            print("No API Key registred. \n== Exit ==")
            sys.exit(1)
        
        # Load the API
        API_KEY = ""
        with open(PATH_API, "r") as fp:
            API_KEY = fp.readline().strip()
        
        # Create the standard authentication payload
        payload = {'Authorization': "Bearer {}".format(API_KEY)}

        if args.cmd == "list":
            VERB = "list"
            resp = requests.get("{}{}".format(URL_API, VERB), headers=payload)
            
            if resp.status_code != 200:
                print("Error: {}".format(resp.status_code))
                print(resp.content)
                sys.exit(1)

            website = json.loads(resp.content.decode())
            
            path = args.path 
            if len(args.path) > 0:
                path = path.rstrip("/") + "/"
                
            website_items = website["files"]
            website_items = list(filter(lambda x: x["path"].startswith(args.path), website_items))
            
            if args.files_only:
                website_items = list(filter(lambda x: x["is_directory"] == False, website_items))
            
            if args.dirs_only:
                website_items = list(filter(lambda x: x["is_directory"] == True, website_items))
            
            if args.rec == False: # If true, recursive, if false, remove all documents with one "/".
                # If not provided, as if max 0
                # If first directory, depend if end by "/" or not.
                l = 0
                if len(args.path) > 0:
                    l = args.path.rstrip("/").count("/") + 1
                
                website_items = list(filter(lambda x: x["path"].count("/") == l, website_items))
            
            # Sort items
            tmp = sorted(map(lambda x: (x["path"], x), website_items))
            website_items = list(map(lambda x: x[1], tmp))
            
            n = max(map(lambda x: len(x["path"]), website_items))

            if args.path != "":
                l = len(args.path)
                print("Under `{}` folder, files/doc:".format(args.path))
                for items in website_items:
                    display_item(items, l, args.date, args.size, args.hash, n)

            else:
                print("Under the root, files/doc:")
                for items in website_items:
                    display_item(items, 0, args.date, args.size, args.hash, n)

        elif args.cmd == "opti":
            print("Compare states.")
            resp = requests.get("{}list".format(URL_API), headers=payload)
            if resp.status_code != 200:
                print("Error: {}".format(resp.status_code))
                print(resp.content)
                sys.exit(1)
            
            website = json.loads(resp.content.decode())
            list_files = website["files"]
            list_files = list(filter(lambda x: x["is_directory"] == False, list_files))
            
            # Get the website hash
            dico = {}
            for item in list_files:
                dico[item["path"]] = item["sha1_hash"]

            all_files = get_tree(args.path)
            
            l0 = len(args.path)
            new_file = set(list(map(lambda x: x[l0:], all_files))) - set(dico)
            mis_file = set(dico) - set(list(map(lambda x: x[l0:], all_files))) 
            old_file = set(list(map(lambda x: x[l0:], all_files))) & set(dico)
            print("{} new files".format(len(new_file)))
            print("{} old files".format(len(old_file)))
            print("{} missing files".format(len(mis_file)))

            print("="*40)
            lst_to_update = []
            l_old = len(old_file)
            for idx, f in enumerate(old_file):
                hs = dico[f]
                print("Checking {} / {}\t{}".format(idx, l_old, f))
                with open("{}{}".format(args.path, f), "rb") as fp:
                    m = hashlib.sha1()
                    m.update(fp.read())
                    hs1 = m.hexdigest()
                    if hs1 != hs:
                        lst_to_update.append(f)
            print("==> {} modified files".format(len(lst_to_update)))
            print("="*40)
            print("== New files ==")
            for f in sorted(new_file):
                print(f)

            print("== To update ==")
            for f in sorted(lst_to_update):
                print(f)
            
            if args.debug:
                print("Debug mode: exiting.")
            else:
                print("== Updating the distant repository ==")
                for remote_name in sorted(list(new_file) + lst_to_update):

                    filename = args.path + remote_name
                    print("Opening {}".format(filename), end="")
                    with open(filename, "rb") as fp:
                        data = fp.read()
                        print("\tRead ok", end="")
                    
                        resp = requests.post("{}upload".format(URL_API), 
                                headers=payload, 
                                files={"{}".format(remote_name): data})
                        print("\tSend: {}".format(resp.status_code))



            
        elif args.cmd == "size":
            print("Check the size of a folder")

            resp = requests.get("{}list".format(URL_API), headers=payload)
            
            if resp.status_code != 200:
                print("Error: {}".format(resp.status_code))
                print(resp.content)
                sys.exit(1)

            website = json.loads(resp.content.decode())
            
            folder = args.path 
            if len(folder) > 0:
                folder = folder.rstrip("/") + "/"
            
            website_items = list(filter(lambda x: x["path"].startswith(args.path), website["files"]))
            website_items = list(filter(lambda x: x["is_directory"] == False, website_items))
            size_tot = sum(map(lambda x: x["size"], website_items))

            lst = ["ko", "Mo", "Go"]
            label = "o"
            for lb in lst:
                if size_tot > 1024:
                    label = lb
                    size_tot /= 1024
                else:
                    break

            print("Found {} files".format(len(website_items)))
            print("Total size: {:.5} {}".format(size_tot, label))
            
            if args.save:
                os.makedirs("snapshots", exist_ok=True)
                
                print("Saving information into the folder `snapshots`")
                with open("snapshots/latest.json", "w") as fp:
                    json.dump(website["files"], fp, indent=True)
                    
                import time
                with open("snapshots/T_{}.json".format(int(time.time())), "w") as fp:
                    json.dump(website["files"], fp, indent=True)
                    
                


        elif args.cmd == "update":
            print("UPLOAD")
            print("path to send everything", args.remote_path)
            print("things to put there", args.local_files)
            # If we list a directory, we assume we push everything bellow.
            # If we push a file, we add everything under.

            VERB = "upload"
            send_path = args.remote_path.rstrip('/')

            lst = [] # (local location, future name)
            for filename in args.local_files:     

                if os.path.isdir(filename) == False:
                    keep_name = filename.rsplit("/", 1)[-1]
                    lst.append([filename, keep_name])
                
                elif args.rec:
                    subfiles = recursively_search_files(filename)
                    l0 = len(filename.rstrip('/'))
                    l1 = len(filename.rstrip("/").rsplit("/", 1)[-1])
                    lst.extend(list(map(lambda x: (x, x[l0-l1:]), subfiles)))

                    
            # When debbugging
            #print(lst)
            
            # send {"filename": "string content"}
            for (filename, remote_name) in lst:

                print("Opening {}".format(filename), end="")
                with open(filename, "rb") as fp:
                    data = fp.read()
                    print("\tRead ok", end="")
                    
                    resp = requests.post("{}{}".format(URL_API, VERB), 
                            headers=payload, 
                            files={"{}/{}".format(send_path, remote_name): data})
                    print("\tSend: {}".format(resp.status_code))


            
        elif args.cmd == "delete":
            print("Would remove stuff remotely.")
            
            VERB = "delete"
            
            for filename in args.remote_files:
                #file_list = { # Multiple files
                #    "filenames[]": ["test/third.md", "test/second.txt"],
                #}

                file_list = {"filenames[]": filename} # One file
                print("Removing {}".format(filename), end="\t")
                resp = requests.post("{}{}".format(URL_API, VERB), headers=payload, data=file_list)
                print(resp.status_code)



    else:
        print("Not implemented")

