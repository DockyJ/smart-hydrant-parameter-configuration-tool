import serial


class COM:
    def __init__(self, port):
        self.ser = None
        self.port = port
        self.port_state = True

    # 检查串口是否可用
    def check_port_state(self):
        try:
            self.ser = serial.Serial(self.port, 115200)
            self.ser.close()
        except serial.SerialException as se:
            self.port_state = False
            print(se)
        return self.port_state

    # 打开串口
    def open_port(self):
        try:
            if self.check_port_state():
                self.ser.open()
        except Exception as e:
            print(e)

    # 关闭串口
    def close_port(self):
        try:
            if self.port_state and self.ser.isOpen():
                self.ser.close()
        except serial.SerialException as se:
            print(se)

    # 设置波特率
    def set_baud_rate(self, baud_rate):
        try:
            self.ser.baudrate = int(baud_rate)
        except ValueError as ve:
            print(ve)

    # 设置数据位
    def set_byte_size(self, byte_size):
        try:
            if int(byte_size) == 5:
                self.ser.bytesize = serial.FIVEBITS
                return None
            if int(byte_size) == 6:
                self.ser.bytesize = serial.SIXBITS
                return None
            if int(byte_size) == 7:
                self.ser.bytesize = serial.SEVENBITS
                return None
            self.ser.bytesize = serial.EIGHTBITS
        except ValueError as e:
            print(e)

    # 设置停止位
    def set_stop_bits(self, stop_bits):
        try:
            if stop_bits == '1.5':
                self.ser.stopbits = serial.STOPBITS_ONE_POINT_FIVE
                return None
            if stop_bits == '2':
                self.ser.stopbits = serial.STOPBITS_TWO
                return None
            self.ser.stopbits = serial.STOPBITS_ONE
        except ValueError as e:
            print(e)

    # 设置校验位
    def set_parity(self, parity):
        try:
            if parity == 'EVEN':
                self.ser.parity = serial.PARITY_EVEN
                return None
            if parity == 'ODD':
                self.ser.parity = serial.PARITY_ODD
                return None
            if parity == 'MARK':
                self.ser.parity = serial.PARITY_MARK
                return None
            if parity == 'SPACE':
                self.ser.parity = serial.PARITY_SPACE
                return None
            self.ser.parity = serial.PARITY_NONE
        except ValueError as e:
            print(e)

    # 获取流控制状态
    def set_flow_ctr(self, flow_ctr):
        try:
            if flow_ctr == 'None':
                return None
            if flow_ctr == 'Software:xonxoff':
                self.ser.rtscts = False
                self.ser.dsrdtr = False
                self.ser.xonxoff = True
                return None
            if flow_ctr == 'Hardware:rtscts':
                self.ser.xonxoff = False
                self.ser.dsrdtr = False
                self.ser.rtscts = True
                return None
            if flow_ctr == 'Hardware:dsrdtr':
                self.ser.xonxoff = False
                self.ser.rtscts = False
                self.ser.dsrdtr = True
                return None
        except Exception as e:
            print(e)

    # 设置 DTR
    def set_dtr(self, dtr):
        try:
            if dtr:
                self.ser.setDTR(True)
                return None
            self.ser.setDTR(False)
        except Exception as e:
            print(e)

    # 设置 RTS
    def set_rts(self, rts):
        try:
            if rts:
                self.ser.setRTS(True)
                return None
            self.ser.setRTS(False)
        except Exception as e:
            print(e)

    # 发送数据
    def send_data(self, data):
        send_bytes = 0
        if self.ser is None:
            self.open_port()
        try:
            send_bytes = self.ser.write(data)
        except Exception as e:
            print(e)
        return send_bytes

    # 读取串口数据
    def get_data(self):
        data = ''
        try:
            if self.ser is None:
                self.open_port()
            data = self.ser.read(self.ser.inWaiting()).decode()
        except Exception as e:
            print(e)
        if data != '':
            return data