# git_storage
Distributed file system that keeps a customizable number of past file versions

---
### Notes
- Name of filesystem must contain only lowercase letters and hyphen(-)

---
### DB Schema

##### root_pointers
- key
    - name
- values
    - cksum             (string)
    - bucket_name       (string)

##### Namespace
- key
    - cksum
- values
    - name              (string)
    - is_dir            (boolean)
    - s3_ref            (list of lists) / if we set cksum to be file name, then
      we don't need this, can keep track of versions I suppose
    - dir_info          (list of lists) - (name, cksum) - first is (abspath, None)
    - mod_time          (string)
    - mod_user          (string)

---
### Hashing
Use Python built in hashlib, sha256, and exchange over network as hex string

---
### Operations

*(Note: on all of the below if an invalid filepath is entered, return an error)*

- PUT
    - traverse through merkle tree to identify node
    - check if node mod_user was self
        - if yes:
            - calculate checksum of new file
            - add file to s3 (use s3 versioning)
            - create new node for file
            - bubble up and make new nodes for all ancestors
        - if no:
            - ask if user wants to review newest version of file or overwrite directly
                - if yes:
                    - fetch "newest version"
                - if no:
                    - overwrite directly with procedure similar to yes above
- GET
    - traverse through merkle tree to identify node
    - fetch file and save to local

- MKDIR
    - traverse through merkle tree to find the parent node for the new directory
    - calculate checksum of new directory
    - create new node for the new directory
    - bubble up and make new nodes for all ancestors

- LS
    - traverse through merkle tree to find node (should be a directory node)
    - check if is_dir
        - if yes:
            - go through dir_info, collect all filenames, and return
        - if no:
            - return the name of the file
- CP
    - traverse through merkle tree to find node of source file
    - traverse through merkle tree to find node of destination directory
    - steps to add file to new directory:
        - calculate checksum of new file
        - duplicate the file in s3 and properly name it
        - create new node for file
        - bubble up and make new nodes for all ancestors
- RM
    - traverse through merkle tree to identify the node
    - generate a new checksum for the new parent node
    - create a new node for the parent directory without the target file in it
    - bubble up and make new nodes for all ancestors
- MV
    - traverse through merkle tree to find node of source file and store in memory
    - traverse through merkle tree to find node of destination directory
    - perform a RM on the source file
    - steps to add file to new directory
        - calculate checksum of new file 
        - create new node for file (even though it's the same file, need to create new node for versioning)
        - bubble up and make new nodes for all ancestors
        
