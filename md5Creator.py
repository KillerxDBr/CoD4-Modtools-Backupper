import hashlib
import tempfile
import subprocess
from pathlib import Path
import sqlite3

if __name__ == '__main__':

    PADRAO = Path(__file__).parent.resolve()

    # git ls-files --other --exclude-standard

    with tempfile.TemporaryFile() as tempf:
        proc = subprocess.Popen(
            ['git', 'ls-files', '--other', '--exclude-standard'],
            stdout=tempf, cwd=PADRAO)
        proc.wait()
        tempf.seek(0)
        files = ''.join([chr(x) for x in tempf.read()]).splitlines()

    cx = sqlite3.connect('md5.db')
    c = cx.cursor()
    originalFiles:list[list] = c.execute('Select * from MD5').fetchall()
    cx.close()
    filesToAdd = []
    for file in files:
        file = file.replace('/','\\') #Remove after fix in database...
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
        # if existsOnDB:
        #     continue

    #     c.execute('select * from MD5 where Filename=? AND Fullpath=?',
    #               (p.name, str(p)))
    #     rst = c.fetchone()
    #     if rst and (rst[4] == p.stat().st_size == 0):
    #         continue
    #     if not rst or not rst[1] == hashlib.md5(open(file, 'rb').read()).hexdigest():
    #         # print('MD5 Missing')
    #         lst.append(file)
    #     else:
    #         print(f'MD5 True -> {file}')
    # cx.close()

    if filesToAdd:
        nl = '\n'
        if input(f'{"="*30}\nDo you want do add those files to the repository?\n\n{nl.join(filesToAdd)}\n\n[y]es or [n]o: ').lower() == 'y':
            for file in filesToAdd:
                proc = subprocess.Popen(['git', 'add', file], cwd=PADRAO)
                proc.wait()
            print('Use "git commit -a -m <message>" to commit all modifications')
    else:
        print('No new or modified files to be added!')
