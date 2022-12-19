import os
import re
import sys
import time

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon, QPainter, QColor, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox

import method
import port
from sscom import Ui_MainWindow


class MyMainForm(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyMainForm, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("智能消火栓配置软件")                 # 设置窗体标题
        self.setWindowIcon(QIcon(r'.\imgs\title2.ico'))         # 设置窗体图标
        self.loopSendBox.setEnabled(False)                      # 锁定定时发送
        self.init_port()                                        # 初始化调用init_port()函数
        self.init_config()                                      # 初始化调用init_config()函数
        self.init_send_show()                                   # 初始化调用init_send_show()函数
        # self.init_file()                                        # 初始化调用init_file()函数

    # 串口开关控件初始化
    def init_port(self):
        self.myCOM = None
        self.get_port_list_loop = QTimer(self)                                        # 定义一个定时串口刷新器
        self.get_port_list_loop.timeout.connect(self.get_port_list_btn)               # 定时串口刷新器绑定get_port_list_btn函数
        self.portItemsBox.addItems(method.get_port_list())                            # 获取可以串口列表并添加到串口号下拉框
        self.get_port_list_loop.start(2000)                                           # 打开定时串口刷新器，设置每隔2000毫秒接收一次
        self.getPortBtn.clicked.connect(self.get_port_list_btn)                       # 刷新串口按钮绑定get_port_list_btn函数
        self.openPortBtn.setChecked(False)                                            # 设置打开串口按钮初始值为关闭
        self.openPortBtn.toggled.connect(lambda: self.btn_port(self.openPortBtn))     # 打开串口按钮绑定槽函数
        self.closePortBtn.setChecked(True)                                            # 设置关闭串口按钮初始值为打开
        self.closePortBtn.toggled.connect(lambda: self.btn_port(self.closePortBtn))   # 关闭串口按钮绑定槽函数

    # 串口配置控件初始化
    def init_config(self):
        self.baudBox.addItems(method.get_baud_rate())           # 波特率下拉框添加选项
        self.baudBox.setCurrentIndex(12)                        # 波特率下拉框设置初始索引
        self.baudBox.activated.connect(self.config_port)        # 波特率下拉框绑定config_port函数
        self.byteBox.addItems(method.get_byte_size())           # 数据位下拉框添加选项
        self.byteBox.setCurrentIndex(3)                         # 数据位下拉框设置初始索引
        self.byteBox.activated.connect(self.config_port)        # 数据位下拉框绑定config_port函数
        self.stopBitBox.addItems(method.get_stop_bits())        # 停止位下拉框添加选项
        self.stopBitBox.activated.connect(self.config_port)     # 停止位下拉框绑定config_port函数
        self.parityBox.addItems(method.get_parity())            # 校验位下拉框添加选项
        self.parityBox.activated.connect(self.config_port)      # 校验位下拉框绑定config_port函数
        self.flowCtrBox.addItems(method.get_flow_ctr())         # 流控制下拉框添加选项
        self.flowCtrBox.activated.connect(self.config_port)     # 流控制下拉框绑定config_port函数
        self.DTRBox.stateChanged.connect(self.set_dtr)          # DTR复选框绑定set_dtr函数
        self.RTSBox.stateChanged.connect(self.set_rts)          # RTS复选框绑定set_rts函数

    # 收发数据控件初始化
    def init_send_show(self):
        self.showDataEdit.setReadOnly(True)                               # 设置显示数据文本框为只读
        self.timer_show = QTimer(self)                                    # 定义一个定时接收器
        self.timer_show.timeout.connect(self.show_data)                   # 定时接收器绑定show_data函数
        self.HEXShowBox.setChecked(False)                                 # HEX显示复选框设置为不选中
        self.HEXShowBox.stateChanged.connect(lambda: self.show_type())    # HEX显示复选框绑定show_type函数
        self.HEXShowBox.setEnabled(False)                                 # 锁定HEX显示复选框
        self.HEXSendBox.setEnabled(False)                                 # 锁定HEX发送复选框
        self.timer_send = QTimer(self)                                    # 定义一个定时发送器
        self.timer_send.timeout.connect(self.send_data_loop)              # 定时发送器绑定send_data_loop函数
        self.loopSendBox.toggled.connect(self.send_data_loop)             # 定时发送复选框绑定send_data_loop函数
        self.sendDataBtn.clicked.connect(self.send_data)                  # 发送数据按钮绑定send_data函数
        self.clearWinBtn.clicked.connect(self.clear_win)                  # 清除窗口按钮绑定clear_win函数
        self.all_send_bytes = 0                                           # 定义一个总发送字节数
        self.all_get_bytes = 0                                            # 定义一个总接收字节数
        self.getConfigBtn.clicked.connect(self.get_config)                # 获取参数按钮绑定get_config函数
        self.setConfigBtn.clicked.connect(self.set_config)                # 写入参数按钮绑定set_config函数

    # 获取和写入参数控件初始化
    def init_file(self):
        self.getConfigBtn.clicked.connect(self.get_config)    # 获取参数按钮绑定get_config函数
        # self.fileDialog = QFileDialog                           # 定义一个打开文件弹窗
        self.setConfigBtn.clicked.connect(self.set_config)    # 写入参数按钮绑定set_config函数

    # 更新串口列表按钮
    def get_port_list_btn(self):
        port_list_temp = method.get_port_list()
        num = len(port_list_temp)
        current_port_list = self.portItemsBox.count()
        if num != current_port_list:
            self.portItemsBox.clear()
            self.portItemsBox.addItems(port_list_temp)                # 获取可以串口列表并添加到串口号下拉框
            # self.closePortBtn.setChecked(True)                        # 设置关闭串口按钮初始值为打开

    # 打开串口
    def open_port(self):
        try:
            currentport = re.findall(r"(\d+)", self.portItemsBox.currentText())
            self.myCOM = port.COM("COM" + currentport[0])             # 实例化一个自定义的port类
            self.myCOM.open_port()                                    # 打开串口
            self.portItemsBox.setEnabled(False)                       # 锁定串口下拉框
            # self.baudBox.setEnabled(False)                            # 锁定波特率下拉框
            # self.byteBox.setEnabled(False)                            # 锁定数据位下拉框
            # self.stopBitBox.setEnabled(False)                         # 锁定停止位下拉框
            # self.parityBox.setEnabled(False)                          # 锁定校验位下拉框
            # self.flowCtrBox.setEnabled(False)                         # 锁定流控制下拉框
            if not self.myCOM.port_state:                             # 如果串口不可用，弹窗报错
                port_error_msgBox = QMessageBox(QMessageBox.Information, '串口打开错误', '串口无法打开，当前串口已被占用或其他错误！！'
                                                                                   '请选择其他串口或检查串口设置是否正确。')
                port_error_msgBox.setWindowIcon(QIcon(r'.\imgs\error.ico'))
                port_error_msgBox.exec_()
                self.closePortBtn.setChecked(True)                    # 选择关闭按钮
                self.portItemsBox.setEnabled(True)                    # 解除串口下拉框锁定
                # self.baudBox.setEnabled(True)                         # 解除波特率下拉框锁定
                # self.byteBox.setEnabled(True)                         # 解除数据位下拉框锁定
                # self.stopBitBox.setEnabled(True)                      # 解除停止位下拉框锁定
                # self.parityBox.setEnabled(True)                       # 解除校验位下拉框锁定
                # self.flowCtrBox.setEnabled(True)                      # 解除流控制下拉框锁定
            self.DTRBox.setChecked(self.myCOM.ser.dtr)                # 获取DTR
            self.RTSBox.setChecked(self.myCOM.ser.rts)                # 获取RTS
            self.timer_show.start(2)                                  # 打开接收定时器，设置每隔2毫秒接收一次
            port_info1 = self.myCOM.ser.port + '已打开' + ' [' + str(self.myCOM.ser.baudrate) + '-' + str(self.myCOM.ser.bytesize) + \
                        '-' + str(self.myCOM.ser.stopbits) + '-' + self.myCOM.ser.parity + ']'
            port_info2 = ' [CTS=' + str(self.myCOM.ser.getCTS()) + ' DSR=' + str(self.myCOM.ser.getDSR()) + ' RI=' + \
                         str(self.myCOM.ser.getRI()) + ' CD=' + str(self.myCOM.ser.getCD()) + ']'
            self.portInfolabel.setText(port_info1 + port_info2)       # 显示已打开串口信息
        except Exception as e:
            print(e)

    # 关闭串口
    def close_port(self):
        try:
            self.timer_show.stop()                                      # 关闭接收定时器
            self.myCOM.close_port()                                     # 关闭串口
            self.DTRBox.setChecked(False)
            self.RTSBox.setChecked(False)
            self.portItemsBox.setEnabled(True)                          # 解除串口下拉框锁定
            # self.baudBox.setEnabled(True)                               # 解除波特率下拉框锁定
            # self.byteBox.setEnabled(True)                               # 解除数据位下拉框锁定
            # self.stopBitBox.setEnabled(True)                            # 解除停止位下拉框锁定
            # self.parityBox.setEnabled(True)                             # 解除校验位下拉框锁定
            # self.flowCtrBox.setEnabled(True)                            # 解除流控制下拉框锁定
            self.portInfolabel.setText(self.myCOM.ser.port + '已关闭')
        except Exception as e:
            print(e)

    # 打开还是关闭串口
    def btn_port(self, btn):
        if btn.text() != '打开串口':
            return None
        if btn.isChecked():
            self.open_port()                     # 打开串口
            self.loopSendBox.setEnabled(True)    # 解除定时发送复选框锁定
            return None
        self.close_port()                    # 关闭串口
        self.loopSendBox.setEnabled(False)   # 锁定定时发送复选框

    # 配置串口
    def config_port(self):
        try:
            self.myCOM.set_baud_rate(self.baudBox.currentText())       # 设置波特率
            self.myCOM.set_byte_size(self.byteBox.currentText())       # 设置数据位
            self.myCOM.set_stop_bits(self.stopBitBox.currentText())    # 设置停止位
            self.myCOM.set_parity(self.parityBox.currentText())        # 设置校验位
            self.myCOM.set_flow_ctr(self.flowCtrBox.currentText())     # 设置流控制
            port_info1 = self.myCOM.ser.port + '已打开' + ' [' + str(self.myCOM.ser.baudrate) + '-' + str(self.myCOM.ser.bytesize) + \
                        '-' + str(self.myCOM.ser.stopbits) + '-' + self.myCOM.ser.parity + ']'
            port_info2 = ' [CTS=' + str(self.myCOM.ser.getCTS()) + ' DSR=' + str(self.myCOM.ser.getDSR()) + ' RI=' + \
                         str(self.myCOM.ser.getRI()) + ' CD=' + str(self.myCOM.ser.getCD()) + ']'
            self.portInfolabel.setText(port_info1 + port_info2)       # 显示已打开串口信息
        except Exception as e:
            print(e)

    # 设置 DTR
    def set_dtr(self):
        try:
            self.myCOM.set_dtr(self.DTRBox.isChecked())
        except Exception as e:
            print(e)

    # 设置 RTS
    def set_rts(self):
        try:
            self.myCOM.set_rts(self.RTSBox.isChecked())
        except Exception as e:
            print(e)

    # 发送数据
    def send_data(self):
        try:
            if self.closePortBtn.isChecked():    # 如果关闭串口按钮选定，不能发送数据
                send_data_error_msgBox = QMessageBox(QMessageBox.Information, '发送数据错误', '无法发送数据，请先打开串口！')
                send_data_error_msgBox.setWindowIcon(QIcon(r'.\imgs\error.ico'))
                send_data_error_msgBox.exec_()
                return None
            data = self.sendDataEdit.text()  + "\r\n"      # 从发送数据输入框获取要发送的数据
            send_bytes = 0                       # 定义一个发送字节数
            # if self.HEXSendBox.isChecked():  # 如果HEX发送复选框选定，发送HEX格式数据
            #     if not method.check_hex(data) or len(''.join(data.split())) % 2 != 0:
            #         hex_error_msgBox = QMessageBox(QMessageBox.Information, '发送数据错误', '输入hex格式错误! '
            #                                                                             '请按照如“01 23 .. ..” 格式输入')
            #         hex_error_msgBox.setWindowIcon(QIcon(r'.\imgs\error.ico'))
            #         hex_error_msgBox.exec_()
            #     else:
            #         send_bytes = self.myCOM.send_data(method.hex_byte(data))  # 获取发送字节数
            # else:
            send_bytes = self.myCOM.send_data(data.encode())                  # 获取发送字节数
            self.all_send_bytes += send_bytes                                 # 统计发送总字节数
            self.sendBytelabel.setText('S:' + str(self.all_send_bytes))
        except Exception as e:
            print(e)

    # 定时发送
    def send_data_loop(self):
        if self.loopSendBox.isChecked():                             # 如果定时发送复选框被选定，定时发送数据
            self.setTimeEdit.setReadOnly(True)                       # 定时发送输入框设置只读
            if self.setTimeEdit.text() == '':                        
                return None
            self.timer_send.start(int(self.setTimeEdit.text()))      # 如果定时发送输入框输入不为空，设置间隔时间
            self.send_data()
            return None
        self.timer_send.stop()                                       # 停止定时发送定时器
        self.setTimeEdit.setReadOnly(False)                          # 取消定时发送输入框设置只读

    # 读取并显示数据
    def show_data(self):
        data = self.myCOM.get_data()                   # 获取接收到的数据
        try:
            if data is not None:                       # 如果接收到的数据不为空，选择字符串显示还是HEX显示
                # if self.HEXShowBox.isChecked():
                #     self.showDataEdit.insertPlainText(method.str_hex(data))
                # else:
                self.showDataEdit.insertPlainText(data)
                self.all_get_bytes += len(data)        # 统计接收总字节数
                self.getBytelabel.setText('R:' + str(self.all_get_bytes))
                text_cursor = self.showDataEdit.textCursor()   # 获取光标位置
                text_cursor.movePosition(text_cursor.End)
                self.showDataEdit.setTextCursor(text_cursor)   # 设置光标位置
        except Exception as e:
            print(e)

    # 读取（更新）参数
    def get_config(self):
        try:
            if self.closePortBtn.isChecked():    # 如果关闭串口按钮选定，则要先打开串口
                get_config_open_error_msgBox = QMessageBox(QMessageBox.Information, '获取参数失败', '无法获取参数，请先打开串口！')
                get_config_open_error_msgBox.setWindowIcon(QIcon(r'.\imgs\error.ico'))
                get_config_open_error_msgBox.exec_()
                return None
            current_data = self.showDataEdit.toPlainText()
            data_sn = re.findall(r'data\ sn\ =\ (.*)', current_data)
            data_sample_duty = re.findall(r'data\ sample_duty\ =\ (.*)', current_data)
            data_upload_duty = re.findall(r'data\ upload_duty\ =\ (.*)', current_data)            
            data_ip = re.findall(r'mqtt\ address:(.*)', current_data)
            data_port = re.findall(r'mqtt\ port:(.*)', current_data)
            if len(data_sn[-1]) < 6 or len(data_ip[-1]) < 7 or len(data_ip[-1]) > 15 or int(data_port[-1]) < 0 or int(data_port[-1]) > 65536:
                get_config_error_msgBox = QMessageBox(QMessageBox.Information, '获取参数异常', '请检查接收的数据是否完整或正常，可尝试复位或者重启板子后再次获取！')
                get_config_error_msgBox.setWindowIcon(QIcon(r'.\imgs\error.ico'))
                get_config_error_msgBox.exec_()
            # 将接收框内经过筛选后的信息分别写入对应输入框内
            self.snNameEdit.setText(data_sn[-1])
            self.IPaddressEdit.setText(data_ip[-1])
            self.portNumberEdit.setText(data_port[-1])
            self.sampleDutyEdit.setText(data_sample_duty[-1])
            self.uploadDutyEdit.setText(data_upload_duty[-1])
        except Exception as e:
            print(e)
    
    # 写入参数
    def set_config(self):
        try:
            # 判断哪个框是否为空以及按照要求输入
            if self.closePortBtn.isChecked():    # 如果关闭串口按钮选定，则要先打开串口
                set_config_open_error_msgBox = QMessageBox(QMessageBox.Information, '写入参数失败', '无法写入参数，请先打开串口！')
                set_config_open_error_msgBox.setWindowIcon(QIcon(r'.\imgs\error.ico'))
                set_config_open_error_msgBox.exec_()
                return None
            data_sn_input = self.snNameEdit.text() if len(self.snNameEdit.text()) != 0 else self.snNameEdit.placeholderText()
            data_ip_input = self.IPaddressEdit.text() if len(self.IPaddressEdit.text()) != 0 else self.IPaddressEdit.placeholderText()
            data_port_input = self.portNumberEdit.text() if len(self.portNumberEdit.text()) != 0 else self.portNumberEdit.placeholderText()
            data_sampleDuty_input = self.sampleDutyEdit.text() if len(self.sampleDutyEdit.text()) != 0 else self.sampleDutyEdit.placeholderText()
            data_uploadDuty_input = self.uploadDutyEdit.text() if len(self.uploadDutyEdit.text()) != 0 else self.uploadDutyEdit.placeholderText()
            if len(data_sn_input) < 6 or len(data_ip_input) < 7 or len(data_ip_input) > 15 or int(data_port_input) < 0 or int(data_port_input) > 65535 or int(data_sampleDuty_input) < 20 or int(data_sampleDuty_input) > 65535 or int(data_uploadDuty_input) < 20 or int(data_uploadDuty_input) > 4294967295:
                set_config_error_msgBox = QMessageBox(QMessageBox.Information, '参数异常', '请检查输入框内所需要写入的参数是否完整或符合框内提示的要求，然后再次尝试！')
                set_config_error_msgBox.setWindowIcon(QIcon(r'.\imgs\error.ico'))
                set_config_error_msgBox.exec_()
                return None
            # 拼接成所要的格式之后 TODO 要在收到相应信号时再发送
            set_config_todo_msgBox = QMessageBox.question(self.centralwidget, '写入参数', '请先对板子进行复位或者重启！然后请确认是否开始写入！',
                                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if set_config_todo_msgBox == QMessageBox.No:
                return None
            config_setting_msgBox = QMessageBox(QMessageBox.Information, '写入中', '写入参数中，请勿关闭，稍后会返回写入结果...')
            config_setting_msgBox.setWindowIcon(QIcon(r'.\imgs\title1.ico'))
            config_setting_msgBox.setStandardButtons(QMessageBox.Ok)
            config_setting_msgBox.button(QMessageBox.Ok).setVisible(False)
            config_setting_msgBox.button(QMessageBox.Ok).animateClick(2500)
            config_setting_msgBox.exec_()
            self.clear_win()
            config_flag = self.myCOM.send_data("S".encode())
            time.sleep(0.5)
            data_config = "Y@" + data_sn_input + "@" + data_ip_input + ":" + data_port_input + "," + data_sampleDuty_input + "," + data_uploadDuty_input
            print("data_config: " + data_config)
            send_bytes = self.myCOM.send_data(data_config.encode())
            self.all_send_bytes += send_bytes + config_flag
            self.sendBytelabel.setText('S:' + str(self.all_send_bytes))
            time.sleep(0.5)
            self.show_data()
            current_data = self.showDataEdit.toPlainText()
            print("current_data = " + current_data)
            if current_data.find("First power on") == -1:
                config_success_msgBox = QMessageBox(QMessageBox.Information, '写入失败', '写入参数失败！请检查上一步是否对板子进行复位或重启后及时点击yes开始写入！')
                config_success_msgBox.setWindowIcon(QIcon(r'.\imgs\error.ico'))
                config_success_msgBox.exec_()
                return None
            config_success_msgBox = QMessageBox(QMessageBox.Information, '写入成功', '写入参数成功！可重启板子或者触发事件唤醒板子之后再点获取参数进行验证！')
            config_success_msgBox.setWindowIcon(QIcon(r'.\imgs\title1.ico'))
            config_success_msgBox.exec_()
        except Exception as e:
            print(e)

    # 选择显示类型，str 还是 hex
    def show_type(self):
        # if self.HEXShowBox.isChecked():
        #     text_data = self.showDataEdit.toPlainText()
        #     hex_data = method.str_hex(text_data)
        #     self.showDataEdit.setPlainText(hex_data)
        # else:
        text_data = self.showDataEdit.toPlainText()
        data = method.hex_str(text_data)
        self.showDataEdit.setPlainText(data)
        text_cursor = self.showDataEdit.textCursor()
        text_cursor.movePosition(text_cursor.End)
        self.showDataEdit.setTextCursor(text_cursor)

    # 打开文件
    def open_file(self):
        try:
            file_name, file_type = self.fileDialog.getOpenFileName(self, '打开文件', os.getcwd(),
                                                                   'All Files(*);;Text Files(*.txt)')
            if file_name != '':
                self.fileNameEdit.setText(file_name)
                with open(file_name, 'r', encoding='utf-8') as f:
                    for line in f:
                        self.showDataEdit.insertPlainText(line)
        except Exception as e:
            print(e)

    # 发送文件
    def send_file(self):
        if self.closePortBtn.isChecked():
            send_file_error_msgBox = QMessageBox(QMessageBox.Information, '发送文件错误', '无法发送文件，请先打开串口！')
            send_file_error_msgBox.setWindowIcon(QIcon(r'.\imgs\error.ico'))
            send_file_error_msgBox.exec_()
        try:
            if self.fileNameEdit.text() != '':
                file_data = self.showDataEdit.toPlainText()
                send_bytes = self.myCOM.send_data(file_data.encode())
        except Exception as e:
            print(e)

    # 清除窗口
    def clear_win(self):
        self.showDataEdit.clear()
        self.sendBytelabel.setText('S:0')
        self.getBytelabel.setText('R:0')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = MyMainForm()
    myWin.show()
    sys.exit(app.exec_())