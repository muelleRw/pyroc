import time

import serial
from rocformat import op_0, message_crc, _CRC_FUNC
from construct import *

import pyodbc
from datetime import datetime

ser = serial.Serial('COM1', 9600, timeout = 1)
#ser.open()
raw = op_0.build(
    Container(
        dest_addr=240,
        dest_group=240, 
        src_addr=3, 
        src_group=1, 
        op_code=0, 
        byte_count=2,

        block_number=0,
        selection=0,
        crc=0
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

op_0_format = Struct(
    'dest_addr' / Int8ul,
    'dest_group' / Int8ul,
    
    'src_addr' / Int8ul,
    'src_group' / Int8ul,
    
    'op_code' / Int8ul,
    'byte_count' / Int8ul,
    
    'discrete_inputs_configured' / Int8ul,
    'timed_inputs_configured' / Int8ul,
    'analog_inputs_count' / Int8ul,
    'meter_runs_configured' / Int8ul,
    'pulse_inputs_configured' / Int8ul,
    'pids_configured' / Int8ul,
    'tanks_configured' / Int8ul,
    'ao_configured' / Int8ul,
    'tdo_configured' / Float32n,
    'discrete_outputes_configured' / Int8ul,
    'alarm_pointer' / Int16ul,
    'event_pointer' / Int16ul,
    'hourly_pointer' / Int16ul,
    'diagnostic_1' / Float32n,
    'diagnostic_2' / Float32n,
    'diagnostic_3' / Float32n,
    'diagnostic_4' / Float32n,
    
)