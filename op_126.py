import time

import serial
from rocformat import message_crc, _CRC_FUNC, op_126, op_126_response
from construct import *

import pyodbc
from datetime import datetime

raw_dp=op_126.build(
    Container(
        dest_addr=240, dest_group=240,
        src_addr=3, src_group=1,
        op_code=126, 
        byte_count=1,
        history_point=1,
        crc=0
    )
)
raw_dp = raw_dp[:-2]
msg_crc = message_crc.build(Container(
    crc=_CRC_FUNC(raw_dp)
))
raw_dp += msg_crc

raw_sp=op_126.build(
    Container(
        dest_addr=240, dest_group=240,
        src_addr=3, src_group=1,
        op_code=126, 
        byte_count=1,
        history_point=2,
        crc=0
    )
)
raw_sp = raw_sp[:-2]
msg_crc = message_crc.build(Container(
    crc=_CRC_FUNC(raw_sp)
))
raw_sp += msg_crc

raw_tf=op_126.build(
    Container(
        dest_addr=240, dest_group=240,
        src_addr=3, src_group=1,
        op_code=126, 
        byte_count=1,
        history_point=3,
        crc=0
    )
)
raw_tf = raw_tf[:-2]
msg_crc = message_crc.build(Container(
    crc=_CRC_FUNC(raw_tf)
))
raw_tf += msg_crc


ser = serial.Serial('COM1', 9600, timeout = 1)

answer_dp = b''
while len(answer_dp) == 0:
    ser.write(raw_dp)
    time.sleep(0.5)
    answer_dp=ser.read(300)

answer_sp = b''
while len(answer_sp) == 0:
    ser.write(raw_sp)
    time.sleep(0.5)
    answer_sp=ser.read(300)

answer_tf = b''
while len(answer_tf) == 0:
    ser.write(raw_tf)
    time.sleep(0.5)
    answer_tf=ser.read(300)

ser.close()

#int_values = [x for x in answer]
tf_response = op_126_response.parse(answer_tf)
tf_sorted = op_126_response.parse(answer_tf).history[tf_response.current_minute+1:] + op_126_response.parse(answer_tf).history[:tf_response.current_minute+1]

cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=69.144.222.80;DATABASE=WMUtils;UID=wmueller;PWD=p5fm!lOWNw')
cursor = cnxn.cursor()
cursor.execute("INSERT INTO TempTest(Date, TF) VALUES (?, ?)", datetime.now(), qtr_format.parse(answer).tf)
cnxn.commit()
cursor.close()
cnxn.close()