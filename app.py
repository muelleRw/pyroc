import os
from flask import Flask, render_template, request
import json
import sqlite3
import pandas as pd
import numpy as np


app = Flask(__name__)
app.config['SECRET_KEY'] = 'top-secret!'

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def dashboard():
    return render_template('temperature_48_hour.html')

@app.route('/historic_temp', methods=['GET'])
def get_historic_temp():
    con = sqlite3.connect(os.getenv("DB_PATH"))
    sql = """ SELECT date, ROUND(value,2) as temperature FROM readings WHERE date BETWEEN :start AND :end"""
    df = pd.read_sql(sql, con, params={"start": request.args.get("start"), "end": request.args.get("end")})
    print(df)
    df.replace({np.nan: None}, inplace=True)
    chart = line_chart(df)
    return chart

@app.route('/current_temp', methods=['GET'])
def get_current_temp():
    con = sqlite3.connect(os.getenv("DB_PATH"))
    cur = con.cursor()
    cur.execute(""" SELECT ROUND(value,2) FROM readings WHERE date = (SELECT MAX(date) FROM readings) """)
    data = cur.fetchone()[0]
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
            "paper_bgcolor": 'rgba(250,250,250,255)',
            "plot_bgcolor": 'rgba(250,250,250,255)'
        },
        "config": {
            "responsive": True
        }
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
            "xaxis": {
                "anchor": "y",
                "domain": [0, 1],
                "type": "date",
                "fixedrange": True,
            },
            "yaxis": {
                "fixedrange": True
            },
            "paper_bgcolor": 'rgba(250,250,250,255)',
            "plot_bgcolor": 'rgba(250,250,250,255)'
        },
        "config": {
            "responsive": True
        }
    }
    return mydict

if __name__ == '__main__':
    app.run(host="192.168.1.106", debug=True)
