import argparse
import json
import os
import requests
import sys

PATH_API = "./API_KEY.txt"
URL_API = 'https://neocities.org/api/'

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
        print("\t{}{}/".format(
                file_info["updated_at"] + " \t" if date else "",
                file_info["path"][l_prune:])
                )

    else:
        print("\t{}{}\t{}\t{}".format(
                file_info["updated_at"] + " \t" if date else "",
                file_info["path"][l_prune:] + " " * (nmax + 2 - l_prune - len(file_info["path"])),
                file_info["size"] if size else "",
                file_info["sha1_hash"] if hs else "",
                )
             )

    return


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Neo-CLI, a CLI for Neocities website management.')
    

    subparsers = parser.add_subparsers()

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
    
    


    args = parser.parse_args()
    
    if args.cmd == "add_key":
        print("Saving key `{}` at {}".format(args.key, PATH_API))
        
        
        if os.path.exists(PATH_API) & (args.f == False):
            print("Error: A key already exist. Try `-f` to force replacing it")
        else:
            with open(PATH_API, "w") as fp:
                fp.write(args.key)


    elif args.cmd == "info":
        VERB = "info"
        resp = requests.get("{}{}".format(URL_API, VERB), data={"sitename": args.website})
        if resp.status_code == 200:
            print(resp.content.decode())
        else:
            print("Error")
            print(resp.content.decode())
    
    elif args.cmd in ["list"]:
        if os.path.exists(PATH_API) == False:
            print("No API Key registred.")
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
            print(website["result"]) # Must be "success"
            
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


        


    else:
        print("Not implemented")

