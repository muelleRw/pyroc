import os
from flask import Flask
from celery import Celery
import json
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top-secret!'

# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_tasks(5.0, test.s(), name='Poll Roc and add to DB')

@celery.task
def poll_roc(self):
    con = sqlite3.connect(os.getenv("DB_PATH"))
    cur = con.cursor()

    insert_query = "INSERT INTO readings (date, type, value) VALUES (?, ?, ?)"
    points = [[10, 0, 0], [10, 0, 1], [10, 0, 2]]
    x = op_180(os.getenv("COM_PORT"), int(os.getenv("BAUD")))

    vals = x.poll(points)
    temp = vals["Temperature"][0]
    cur.execute(insert_query, (datetime.now(), "Temperature", temp))
    con.commit()


@app.route('/temp', methods=['GET'])
def get_temp():
    sql = """ SELECT date, ROUND(value,2) FROM readings WHERE date >= date('now', '-2 day')"""
    con = sqlite3.connect(os.getenv("DB_PATH"))
    cur = con.cursor()
    cur.execute(sql)
    data = cur.fetchall()
    return json.dumps(data)


if __name__ == '__main__':
    app.run(host="192.168.1.104", debug=True)
