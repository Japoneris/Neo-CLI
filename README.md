# Neo-CLI: A Command Line Interface for Neocities

Neocities is great:

- IPFS
- Free website hosting up to 100 GB for free account

but Neocities is not programmer friendly:

- Poor GUI interface (major bugs when adding files)
- Poor CLI (missing basic commands)

This alternative CLI is here to provide the basic functions:

- listing files 
- adding / updating files
- removing elements

# Setup 

## API key 

You need to retrieve your API key using the official neocities CLI.
Then, add it in the file `API_file.txt`.

## Executable

`chmod +x neocity.py`


# Usage 


## Most basic usage

`./neocli.py list` would list docs and folders available in the root directory.


## Filtering 

- `./neocli.py list --files_only` keeps the files.
- `./neocli.py list --dirs_only` keeps the directories.

## Knowing about the items


`./neocli.py list --date` gives you the information when has been the last update.

## Specific to the files


`./neocli.py list --size` gives you the size information about the files (sorry, don't have time to implement that)


`./neocli.py list --hash` if you are interested by the sha1 hash of your file.


## Getting info about a subdirectory

Suppose I have:

```bash
index.html
src/doc1.html
src/doc2.html
src/styles/doc3.txt

```


`./neocli.py list --path "src/"`

would return

```
src/doc1.html
src/doc2.html
``` 

## Recursion

`./neocli.py list --path "src/" --rec`

would return 

```
src/doc1.html
src/doc2.html
src/styles/doc3.txt
``` 


# Todo 

## Listing

- [ ] Count files under a directory (so you know if it is interesting to dive into it)
- [ ] Check the size of a folder (for the same reason)


## Locate 

- [ ] When you search for a file ... Use grep with pattern matching is enough.



