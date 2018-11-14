# git_storage
Distributed file system that keeps a customizable number of past file versions

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
    - prev_version      (string)
    - next_version      (string)
    - is_dir            (boolean)
    - s3_ref            (list of lists)
    - dir_info          (list of lists)
    - mod_time          (string)
    - mod_user          (string)

---
### Hashing
Use Python built in hashlib, sha256, and exchange over network as hex string

### Operations

