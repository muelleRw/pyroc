import os
from flask import Flask, render_template
from celery import Celery
import json
import sqlite3
import pandas as pd
import numpy as np


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


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def dashboard():
    return render_template('temperature_48_hour.html')

@app.route('/historic_temp', methods=['GET'])
def get_historic_temp():
    con = sqlite3.connect(os.getenv("DB_PATH"))
    sql = """ SELECT date, ROUND(value,2) as temperature FROM readings """#WHERE date >= date('now', '-2 day')"""
    df = pd.read_sql(sql, con)
    df.replace({np.nan: None}, inplace=True)
    chart = line_chart(df)
    return chart

@app.route('/current_temp', methods=['GET'])
def get_current_temp():
    con = sqlite3.connect(os.getenv("DB_PATH"))
    cur = con.cursor()
    sql = """ SELECT ROUND(value,2) FROM readings WHERE date = (SELECT MAX(date) FROM readings) """
    cur.execute(""" SELECT ROUND(value,2) FROM readings WHERE date = (SELECT MAX(date) FROM readings) """)
    data = cur.fetchone()[0]
    print(data)
    chart = throttle_chart(data)
    return chart


def throttle_chart(data):
    mydict = {
        "data": [
            {
                "type": "indicator",
                "title": {
                    "text": "Current"
                },
                "value": data,
                "mode": "gauge+number",
                "gauge": {
                    "axis": {
                        "range": [-50, 150]
                    }
                }
                
            },
            
        ],
        "layout": {
            "height": 400,
            "width": 400,
            "paper_bgcolor": 'rgba(250,250,250,255)',
            "plot_bgcolor": 'rgba(250,250,250,255)'
        },
    }
    return mydict


def line_chart(data):
    if not data.empty:
        dates = data["date"].tolist()
    else:
        dates = []
    mydict = {
        "data": [
            {
                "type": "scatter",
                "x": dates,
                "y": data["temperature"].tolist(),
                "xaxis": "x",
                "yaxis": "y",
                "name": "Temp (F)",
                "line": {
                    "color": "#d62728"
                }
            },
            
        ],
        "layout": {
            "height": 400,
            "width": 800,
            "xaxis": {
                "anchor": "y",
                "domain": [0, 1],
                "type": "date"
            },
            "paper_bgcolor": 'rgba(250,250,250,255)',
            "plot_bgcolor": 'rgba(250,250,250,255)'
        },
    }
    return mydict

if __name__ == '__main__':
    app.run(host="192.168.1.104", debug=True)
