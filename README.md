# git_storage
Distributed file system that keeps a customizable number of past file versions

---
### Set up
To run the filesystem, you must first run aws configure on your console and
enter your credential. https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html

Then you need to go to DynamoDB AWS Console and create a table called "root_pointers"
with "name" of type String as the key.

After that, you can run:
python set_up.py [namespace]

Then you can run:  
python merkle_fs.py [operation]  
where the [operation] can be any of the following:  
    PUT 	fs src_path dest_path  
    GET		fs src_path dest_path [version cksum]  
    CP		fs src_path dest_path  
    MKDIR	fs path  
    LS		fs path [version cksum]  
    RM		fs path  
    MV		fs orig_path dest_path  
---
### Notes
- Name of filesystem must contain only lowercase letters and hyphen(-)
---
### Hashing
Use Python built in hashlib, sha256, and exchange over network as hex string
