import serial
import time
from construct import *
from collections import namedtuple
import pandas as pd
import struct
import crcmod
class op_180:
    header_message = "<6ii"
    header_names = (
        "dest_addr "
        "dest_group "
        "src_addr "
        "src_group "
        "op_code "
        "byte_count "
        "parameter_count "
    )
    request_point_struct = Struct(
        'point_type' / Int8ul,
        'point_number' / Int8ul,
        'parameter_number' / Int8ul
    )
    request_struct = Struct( 
        #header
        'dest_addr' / Int8ul,
        'dest_group' / Int8ul,
        
        'src_addr' / Int8ul,
        'src_group' / Int8ul,
        
        'op_code' / Int8ul,
        'byte_count' / Int8ul,

        #body
        'parameter_count' / Int8ul,
        'points' / Array(this.parameter_count * 3,  Byte),
        'crc' / Int16ul
    )
    _CRC_FUNC = crcmod.mkCrcFun(0x18005, initCrc=0x0000, xorOut=0x0000)
    message_crc = Struct('crc' / Int16ul)

    def __init__(self, serial_com, serial_baud, serial_timeout=1):
        self.ser = serial.Serial()
        self.ser.baudrate = serial_baud
        self.ser.port = serial_com
        self.ser.timeout = serial_timeout

        self.tags = pd.read_csv("points.csv")
        self._CRC_FUNC = crcmod.mkCrcFun(0x18005, initCrc=0x0000, xorOut=0x0000)
        self.message_crc = Struct('crc' / Int16ul)

    def create_points(self, points):
        points_array = []
        for i in points:
            point = self.request_point_struct.build(
                Container(
                    point_type=i[0], point_number=i[1], parameter_number=i[2]
                )
            )
            points_array.append(point)
        return points_array
    def create_request(self, points):
        points_array = self.create_points(points)
        request = self.request_struct.build(
            Container(
                dest_addr=240, dest_group=240,
                src_addr=3, src_group=1,
                op_code=180, byte_count=len(points_array) * 3 + 1,
                parameter_count=len(points_array),
                points=b''.join(points_array), crc=0
            )
        )
        request = request[:-2]
        msg_crc = self.message_crc.build(
            Container(
                crc=self._CRC_FUNC(request)
            )
        )
        return request + msg_crc

    def parse_request(self, response):
        parsed_values = {}
        vals = response[7:-2]
        while len(vals) > 0:
            point_type = vals[0]
            #point_number = vals[1]
            param_number = vals[2]
            tag = self.tags.loc[(self.tags['PointType'] == point_type) & (self.tags['Parameter'] == param_number)]
            if tag['DataType'].values[0] == 'FL':
                parsed_values[tag['Name'].values[0]] = struct.unpack('<f', vals[3:7])
                rem_chars = 4
            vals = vals[rem_chars + 3:]
        return parsed_values

    def poll(self, points, timeout=0.5):
        request = self.create_request(points)
        response = b''
        try:
            self.ser.open()
            while len(response) == 0:
                print("attempt")
                self.ser.write(request)
                time.sleep(timeout)
                response=self.ser.read(248)#248 max message len w 240 bytes of data
            self.ser.close()
            return self.parse_request(response)
        except Exception as e:
            print(e)
            self.ser.close()
            
#from op_180 import op_180
#points = [[10, 0, 0], [10, 0, 1], [10, 0, 2]]
#x = op_180("COM1", 9600)