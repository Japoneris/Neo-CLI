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


## List 

### Most basic usage

`./neocli.py list` would list docs and folders available in the root directory.


### Filtering 

- `./neocli.py list --files_only` keeps the files.
- `./neocli.py list --dirs_only` keeps the directories.

### Knowing about the items


`./neocli.py list --date` gives you the information when has been the last update.

### Specific to the files


`./neocli.py list --size` gives you the size information about the files (sorry, don't have time to implement that)


`./neocli.py list --hash` if you are interested by the sha1 hash of your file.


### Getting info about a subdirectory

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

### Recursion

`./neocli.py list --path "src/" --rec`

would return 

```
src/doc1.html
src/doc2.html
src/styles/doc3.txt
``` 

## Update 

Suppose I want to send one image in a folder that may not exist.
Here is the command:

`./neocli.py update QR_stellar.png --remote_path="IMG/subfolder/"

You will endup with a structure like

```bash
index.html
IMG/
IMG/subfolder/
IMG/subfolder/QR_stellar.png
src/doc1.html
src/doc2.html
src/styles/doc3.txt
```

The ending "/" is not mandatory. In any case, we assume that you provide a folder.
Changing file names is not implemented.


### Adding folders

Suppose you have locally

```bash
fold/img0.png
fold/img1.png
fold/img2.png
img3.png
```

`./neocli.py update * --remote_path="IMG"`

would lead remotely to (folders are ignored): 

```bash
IMG/img3.png
```

Adding the recursion option:

`./neocli.py update * --remote_path="IMG" --rec`

gives you

```bash
IMG/fold/img0.png
IMG/fold/img1.png
IMG/fold/img2.png
IMG/img3.png
```

Which is different from:

`./neocli.py update * */* --remote_path="IMG"`

which gives you a flat structure:

```bash
IMG/img0.png
IMG/img1.png
IMG/img2.png
IMG/img3.png
```


## Deleting stuff

Suppose you have this initial config

```bash
fold/
fold/IMG/
fold/IMG/img0.png
fold/IMG/img1.png
fold/img2.png
img3.png
```

Then, you can delete some stuff:

 `./neocli.py delete fold/IMG/`

Would let 

```bash
fold/
fold/img2.png
img3.png
```


 `./neocli.py delete fold/*` Would not work as wild card are not implemented for remote.


 `./neocli.py delete img3.png` would remove only the given file.



# Todo 

## Listing

- [ ] Count files under a directory (so you know if it is interesting to dive into it)
- [ ] Check the size of a folder (for the same reason)


## Locate 

- [ ] When you search for a file ... Use grep with pattern matching is enough.


# Support 

If you want to donate, you can send me Stellars (XLM) at this address:

![My Stellar address](./QR_stellar.png)

Or more simply: `GDR4O45XDFV5J4N35OF2P2RMAMAM7FLT4AGOBB3OGDKTJPCMYUKU2D5G`
