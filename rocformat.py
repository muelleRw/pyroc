from construct import *
import crcmod

_CRC_FUNC = crcmod.mkCrcFun(0x18005, initCrc=0x0000, xorOut=0x0000)
message_crc = Struct('crc' / Int16ul)

op_167 = Struct( 
    #header
    'dest_addr' / Int8ul,
    'dest_group' / Int8ul,
    
    'src_addr' / Int8ul,
    'src_group' / Int8ul,
    
    'op_code' / Int8ul,
    'byte_count' / Int8ul,
    
    #body
    'point_type' / Int8ul,
    'point_number' / Int8ul,
    'parameter_count' / Int8ul,
    'parameter_start' / Int8ul,
    "crc" / Int16ul
)

op_0 = Struct( 
    #header
    'dest_addr' / Int8ul,
    'dest_group' / Int8ul,
    
    'src_addr' / Int8ul,
    'src_group' / Int8ul,
    
    'op_code' / Int8ul,
    'byte_count' / Int8ul,
    
    #body
    'block_number' / Int8ul,
    'selection' / Int8ul,
    "crc" / Int16ul
)

op_180_point = Struct(
    'point_type' / Int8ul,
    'point_number' / Int8ul,
    'parameter_number' / Int8ul
)

op_180 = Struct( 
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

qtr_format = Struct(
    'dest_addr' / Int8ul,
    'dest_group' / Int8ul,
    
    'src_addr' / Int8ul,
    'src_group' / Int8ul,
    
    'op_code' / Int8ul,

    'byte_count' / Int8ul,
    
    'parameter_count' / Int8ul,
    'unknown2' / Int8ul,
    'unknown3' / Int8ul,
    'unknown4' / Int8ul,
    'dp' / Float32n,
    'unknown5' / Int8ul,
    'unknown6' / Int8ul,
    'unknown7' / Int8ul,
    'sp' / Float32n,
    'unknown8' / Int8ul,
    'unknown9' / Int8ul,
    'unknown10' / Int8ul,
    'tf' / Float32n
)

op_126 = Struct( 
    #header
    'dest_addr' / Int8ul,
    'dest_group' / Int8ul,
    
    'src_addr' / Int8ul,
    'src_group' / Int8ul,
    
    'op_code' / Int8ul,
    'byte_count' / Int8ul,

    #body
    'history_point' / Int8ul,
    'crc' / Int16ul
)

op_126_response = Struct( 
    #header
    'dest_addr' / Int8ul,
    'dest_group' / Int8ul,
    
    'src_addr' / Int8ul,
    'src_group' / Int8ul,
    
    'op_code' / Int8ul,
    'byte_count' / Int8ul,

    #body
    'history_point' / Int8ul,
    'current_minute' / Int8ul,
    'history' / Float32l[60],#Array(60,  Float32l),
    'crc' / Int16ul
)