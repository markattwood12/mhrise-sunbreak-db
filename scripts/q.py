import sqlite3,sys
db=sqlite3.connect(sys.argv[1])
for q in sys.argv[2].split(';'):
    q=q.strip()
    if not q: continue
    cur=db.execute(q); cols=[d[0] for d in cur.description]
    print('\n'+' | '.join(cols))
    for r in cur.fetchall(): print(' | '.join(str(x) for x in r))
