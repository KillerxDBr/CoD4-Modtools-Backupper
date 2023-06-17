import hashlib
import tempfile
import subprocess
from pathlib import Path
import sqlite3

PADRAO = Path.cwd()


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
lst = []
for file in files:
    p = Path(file)
    c.execute('select * from MD5 where Filename=? AND Fullpath=?',(p.name, str(p)))
    rst = c.fetchone()
    if not rst or not rst[1] == hashlib.md5(open(file,'rb').read()).hexdigest():
        # print('MD5 Missing')
        lst.append(file)
    # else:
    #     print(f'MD5 True -> {rst[1]}')
cx.close()

if lst:
    for file in lst:
        proc = subprocess.Popen(
            ['git', 'add', file], cwd=PADRAO)
    proc.wait()
