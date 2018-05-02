import pandas as pd
import numpy as np
from random import randint as ri
from datetime import datetime as dt
from datetime import timedelta as td
from sqlalchemy import create_engine
import uuid


NUM_ROWS = 1000000

if __name__=='__main__':
     names = pd.read_csv('names.csv')
     start = dt(1900,1,1)
     all_birthdates = [start+td(ri(0,36523)) for i in range(NUM_ROWS)]
     random_vals = [ri(0,len(names)-1) for i in range(NUM_ROWS)]
     names=names.reset_index()
     db = pd.DataFrame({"index":random_vals})
     db = pd.merge(db, names, on='index')
     db['birthdate'] = all_birthdates
     db['id'] = [uuid.uuid4() for i in range(NUM_ROWS)]
     db['deathdate'] = db['birthdate'].apply(lambda x: x+td(ri(0,30000)))
     db = db[['id','name', 'sex','birthdate','deathdate']]
     db = db.sort_values('birthdate')
     engine = create_engine("mysql://root:@localhost/test")
     db.to_sql('table1',engine,if_exists='replace')
     print ('-------- SUCCESS -----------')
