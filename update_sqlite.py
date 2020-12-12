from op_180 import op_180
import os
import sqlite3
from datetime import datetime
import time
from dotenv import load_dotenv

load_dotenv()

con = sqlite3.connect(os.getenv("DB_PATH"))
cur = con.cursor()

insert_query = "INSERT INTO readings (date, type, value) VALUES (?, ?, ?)"

points = [[10, 0, 0], [10, 0, 1], [10, 0, 2]]
x = op_180(os.getenv("COM_PORT"), int(os.getenv("BAUD")))

vals = x.poll(points)
temp = vals["Temperature"][0]
print(vals)
cur.execute(insert_query, (datetime.now(), "Temperature", temp))
con.commit()