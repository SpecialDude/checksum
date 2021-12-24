# New Utility Script --> 	checksum.py
# Author:	ADETAYO
# Date:	Wednesday, December 22, 2021 11:01:22PM
# Program:	File Checksum

from genericpath import exists, isfile
import hashlib as ash
import os, sys
import sqlite3

HASHFUNCTION = {
    'md5': ash.md5,
    'sha1': ash.sha1,
    'sha2': ash.sha256
}

dbpath = "hashdb.db"

def createDatabase():    
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS hashtable(
        hashname VARCHAR(1024) PRIMARY KEY NOT NULL,
        filename VARCHAR(512) NOT NULL,
        hashvalue VARCHAR(256) NOT NULL,
        filepath VARCHAR(500) NOT NULL,
        hashtype VARCHAR(10) NOT NULL,
        datehashed DATE);

        ''')
    conn.commit()
    conn.close()

def insertIntoDatabase(data:dict):
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    filename = data["filename"]
    hashvalue = data["hashvalue"]
    hashname = hashvalue + filename
    filepath = data["filepath"]
    hashtype = data['hashtype']

    cursor.execute(f'''
        INSERT INTO hashtable (hashname, filename, hashvalue, filepath, datehashed, hashtype)
        VALUES ("{hashname}", "{filename}", "{hashvalue}", "{filepath}", DATE("now"), "{hashtype}");
    ''')

    conn.commit()
    conn.close()

    print("New Record Inserted!!!")

def fetchFromDatabaseByHashvalue(hashvalue):
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()

    cursor.execute(f'''
        SELECT * FROM hashtable WHERE hashvalue = "{hashvalue}";
    ''')
    data = cursor.fetchall()
    conn.close()
    return data

def gethash(filename, hashtype):
    with open(filename, 'rb') as file:
        try:
            hashvalue = HASHFUNCTION[hashtype](file.read()).hexdigest()
        except KeyError:
            hashvalue = None    
    return hashvalue

def isfilepath(text):
    return isfile(text)

def compare(file1, file2, hashtype):
    if not isfilepath(file1):
        print(f"({file1}) <-- first argument to compare action must be a file")
        raise SystemExit

    file1 = os.path.abspath(file1)
    hashvalue1 = gethash(file1, hashtype)
    if isfilepath(file2):
        file2 = os.path.abspath(file2)
        hashvalue2 = gethash(file2, hashtype)
    else:
        hashvalue2 = file2    
    
    print("A")
    print(f"Filename: {os.path.basename(file1)}")
    print(f"{hashtype} Hash Value: {hashvalue1}")
    print()

    print("B")
    print(f"Hash Value: {hashvalue2}")

    if hashvalue1 == hashvalue2:
        print("\nHash values are equivalent")
    else:
        print("\nHashes not equivalent")    

def hashit(file, hashtype):
    file = os.path.abspath(file)
    if not os.path.isfile(file):
        print(f"{file} Could not locate the file in the specifies path")
        raise SystemExit

    hashvalue = gethash(file, hashtype)
    print(f"File Hash Value: {hashvalue}")
    print(f"Hash Type: {hashtype.upper()}\n\n")

    records = fetchFromDatabaseByHashvalue(hashvalue)

    saved = False
    if not records:
        print("No Duplicate file found in the database")
    else:
        print("\tRecords Found!!!")
        for i in range(len(records)):
            rkey, rfilename, rhashvalue, rfilepath, rhashtype, date = records[i]

            print(f"\t\t{i + 1}")
            print(f"\tFilename: {rfilename}")
            print(f"\tFilepath: {rfilepath}")
            print(f"\tDate Hashed: {date}")
            print("\tStatus: " + ("Present" if os.path.exists(os.path.join(rfilepath, rfilename)) else "Removed"))
            if os.path.basename(file) == rfilename:
                saved = True
            print()


    if not saved:
        insertIntoDatabase(
            {
                "filename":os.path.basename(file),
                "filepath":os.path.dirname(file),
                "hashtype":hashtype,
                "hashvalue":hashvalue
            }
        )

def lookup(hashvalue, hashtype):
    records = fetchFromDatabaseByHashvalue(hashvalue)
    print("Looking up")
    print(f"Hash Value: {hashvalue}\n")

    if not records:
        print("No Record Found for the Hash Value")
    else:
        print("\tRecords Found!!!")
        for i in range(len(records)):
            rkey, rfilename, rhashvalue, rfilepath, rhashtype, date = records[i]

            print(f"\t\t{i + 1}")
            print(f"\tFilename: {rfilename}")
            print(f"\tFilepath: {rfilepath}")
            print(f"\tDate Hashed: {date}")
            print("\tStatus: " + ("Present" if os.path.exists(os.path.join(rfilepath, rfilename)) else "Removed"))
            
            print()

def parseArgument(arg:list[str]):
    data = {}
    noflag = []
    arguments = []
    flag = ""

    for a in arg:
        if a.startswith("--") or (a.startswith("-") and len(a) == 2):            
            if flag != "":
                data[flag] = arguments[:]
                arguments.clear()
            else:
                if arguments:
                    noflag += arguments
                    arguments.clear()
            flag = a
            
        else:
            arguments.append(a)
    data[flag] = arguments[:]

    return data    



def main():
    """
        checksum [action] [argument]

        actions
        --compare or -c [file1] [file2]    -   Compare the hashvalue of two files
                        [file] [hashvalue]
        --hash or -s [file]                -   Give the hashvalue of a file
        --lookup or -l [hashvalue]         -   Lookup a hashvalue in the database 
        --hashtype or -t                   -   Preferred Hashing Algorithm (Default: SHA256)

    """
    arg = sys.argv[1:]
    
    data = parseArgument(arg)

    compareArgs = data.get("--compare")
    compareArgs = data.get("-c") if not compareArgs else compareArgs

    hashArgs = data.get("--hash")
    hashArgs = data.get("-s") if not hashArgs else hashArgs

    lookupArgs = data.get("--lookup")
    lookupArgs = data.get("-l") if not lookupArgs else lookupArgs

    hashtype = data.get('--hashtype')
    hashtype = data.get("-t") if not hashtype else hashtype
    hashtype = "sha2" if hashtype == None else hashtype[0]

    if compareArgs == hashArgs == lookupArgs == None:
        print(main.__doc__)
        raise SystemExit

    if compareArgs:
        compare(*compareArgs[:2], hashtype)

    if hashArgs:
        hashit(hashArgs[0], hashtype)

    if lookupArgs:
        lookup(lookupArgs[0], hashtype)      

if __name__ == "__main__":
    createDatabase()
    main()