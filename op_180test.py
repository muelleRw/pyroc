import time

import serial
from rocformat import op_167, message_crc, _CRC_FUNC, op_180, op_180_point, qtr_format
from construct import *

#import pyodbc
from datetime import datetime

ser = serial.Serial('COM1', 9600, timeout = 1)
points = [
    op_180_point.build(Container(
        point_type=1, point_number=2, parameter_number=3
    )), 
    op_180_point.build(Container(
        point_type=4, point_number=5, parameter_number=6
    ))
]

points = [
    op_180_point.build(#DP
        Container(
            point_type=10, point_number=0, parameter_number=0
        )
    ),
    op_180_point.build(#PF
        Container(
            point_type=10, point_number=0, parameter_number=1
        )
    ),
    op_180_point.build(#TF
        Container(
            point_type=10, point_number=0, parameter_number=2
        )
    )
]

raw=op_180.build(
    Container(
        dest_addr=240, dest_group=240,
        src_addr=3, src_group=1,
        op_code=180, byte_count=len(points) * 3 + 1,
        parameter_count=len(points),
        points=b''.join(points), crc=0
    )
)
raw = raw[:-2]
msg_crc = message_crc.build(Container(
    crc=_CRC_FUNC(raw)
))
raw += msg_crc


answer = b''
while len(answer) == 0:
    ser.write(raw)
    time.sleep(0.5)
    answer=ser.read(240)

ser.close()

print(qtr_format.parse(answer).tf)
print(qtr_format.parse(answer).sp)
print(qtr_format.parse(answer).dp)

cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=69.144.222.80;DATABASE=WMUtils;UID=wmueller;PWD=p5fm!lOWNw')
cursor = cnxn.cursor()
cursor.execute("INSERT INTO TempTest(Date, TF) VALUES (?, ?)", datetime.now(), qtr_format.parse(answer).tf)
cnxn.commit()
cursor.close()
cnxn.close()