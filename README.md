# checksum
Verifying the integrity of transmitted files by calculating and comparing Files hashes and checksums

## Usage

        checksum.py [action] [argument] --hashtype [type]
        
        [actions]
        --compare or -c [file1] [file2]    -   Calculate and compare the hashvalue of two files
                        [file] [hashvalue] -   Calculate the hashvalue of a file and compare to a hashvalue 
        --hash or -s [file]                -   Give the hashvalue of a file
        --lookup or -l [hashvalue]         -   Lookup a hashvalue in the database
        
        --hashtype or -t                   -   Preferred Hashing Algorithm (Default: SHA256)
                                               [sha2, sha1, md5] 
