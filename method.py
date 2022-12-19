import binascii
import serial
import serial.tools.list_ports
import re


# 获取串口列表
def get_port_list():
    port_dict = {}
    port_list = []
    list_port = list(serial.tools.list_ports.comports())
    if len(list_port) != 0:
        for i in range(len(list_port)):
            port_dict[i] = re.findall(r'(.*)\(', str(list_port[i]))[-1]
        for key, value in port_dict.items():
            temps = value
            port_list.append(temps)
        return port_list
    print("无可用串口！")
    return port_list


# 波特率
def get_baud_rate():
    baud_rate_list = ['110', '300', '600', '1200', '2400', '4800', '9600', '14400', '19200', '38400', '56000',
                      '57600', '115200', '128000', '256000']
    return baud_rate_list


# 数据位
def get_byte_size():
    byte_size_list = ['5', '6', '7', '8']
    return byte_size_list


# 停止位
def get_stop_bits():
    stop_bits_list = ['1', '1.5', '2']
    return stop_bits_list


# 校验位
def get_parity():
    parity_list = ['NONE', 'EVEN', 'ODD', 'MARK', 'SPACE']
    return parity_list


# 流控制
def get_flow_ctr():
    flow_list = ['None', 'Software:xonxoff', 'Hardware:rtscts', 'Hardware:dsrdtr']
    return flow_list


# str转hex
def str_hex(str_data):
    hex_data = ''
    data_len = len(str_data)
    for i in range(data_len):
        h_vol = ord(str_data[i])
        h_hex = '%02x' % h_vol
        hex_data += h_hex + ' '
    return hex_data


# hex转str
def hex_str(hex_data):
    data_list = hex_data.split()
    data_str = "".join(data_list)
    m = data_str.encode('utf-8')
    str_data = binascii.unhexlify(m)
    return str_data.decode('utf-8')


# bytes转hex
def byte_hex(byte_data):
    hex_data = ''
    for item in byte_data:
        hex_data += str(hex(item))[2:].zfill(2).upper() + " "
    return hex_data


# hex转bytes
def hex_byte(hex_data):
    byte_data = []
    s_list = hex_data.split(' ')
    for i in s_list:
        b = int(i, 16)
        byte_data.append(b)
    return byte_data


# 检查hex格式
def check_hex(data):
    flag = True
    sub_data = []
    for i in range(len(data)):
        if (i+1) % 3 == 0:
            sub_data.append(data[i])
    for item in sub_data:
        if item != ' ':
            flag = False
    return flag