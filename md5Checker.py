import hashlib
import tempfile
import subprocess
from pathlib import Path
import sqlite3
from time import perf_counter
import sys

if __name__ == '__main__':
    startTime = perf_counter()
    if len(sys.argv) > 1:
        cwd = Path(sys.argv[1]).resolve()
        # print("Using ARGV")
    else:
        cwd = Path(__file__).parent.resolve()
        # print("Using File Path")

    # git ls-files --other --exclude-standard

    with tempfile.TemporaryFile() as tempf:
        proc = subprocess.Popen(
            ['git', 'ls-files', '--other', '--exclude-standard'],
            stdout=tempf, cwd=cwd)
        if proc.wait() != 0:
            print(f"{proc.returncode = }")
            tempf.close()
            exit(1)
        tempf.seek(0)
        files = ''.join([chr(x) for x in tempf.read()]).splitlines()

    con = sqlite3.connect(f'{cwd}/md5.db')
    cur = con.cursor()
    originalFiles:list[list] = cur.execute('Select * from MD5').fetchall()
    cur.close()
    con.close()
    filesToAdd = []
    for file in files:
        file = file.replace('/','\\') # TODO Remove after fix in database...
        existsOnDB: bool = False
        
        for originalFile in originalFiles:
            if originalFile[3] != file:
                continue
            existsOnDB = True
            if originalFile[4] == Path(file).stat().st_size == 0:
                print(f'\33[0;33mFile size = 0, skipping -> {file}\033[0;0m')
                break
            if originalFile[1] == hashlib.md5(open(file, 'rb').read()).hexdigest():
                print(f'\33[0;32mMD5 True -> {file}\033[0;0m')
                break
            print(f'\33[0;31mMD5 False -> {file}\033[0;0m')
            filesToAdd.append(file)

        if not existsOnDB:
            print(f'Adding new File -> {file}')
            filesToAdd.append(file)

    if filesToAdd:
        nl = '\n'
        if input(f'{"="*30}\nDo you want do add those files to the repository?\n\n{nl.join(filesToAdd)}\n\n[y]es or [n]o: ').lower() == 'y':
            for file in filesToAdd:
                proc = subprocess.Popen(['git', 'add', file], cwd=cwd)
                proc.wait()
            print('Use "git commit -a -m <message>" to commit all modifications')
    else:
        print('No new or modified files to be added!')

    print("Execution time: ",perf_counter() - startTime)
