# Form implementation generated from reading ui file 'AuguryUi3_7.ui'
#
# Created by: PyQt6 UI code generator 6.6.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(952, 883)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton_2 = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.cmdline = QtWidgets.QTextEdit(parent=self.centralwidget)
        self.cmdline.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setPointSize(18)
        self.cmdline.setFont(font)
        self.cmdline.setObjectName("cmdline")
        self.horizontalLayout.addWidget(self.cmdline)
        self.pushButton_3 = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout.addWidget(self.pushButton_3)
        self.pushButton_4 = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton_4.setObjectName("pushButton_4")
        self.horizontalLayout.addWidget(self.pushButton_4)
        self.pushButton_5 = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton_5.setObjectName("pushButton_5")
        self.horizontalLayout.addWidget(self.pushButton_5)
        self.pushButton_6 = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton_6.setObjectName("pushButton_6")
        self.horizontalLayout.addWidget(self.pushButton_6)
        self.pushButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.radioButton = QtWidgets.QRadioButton(parent=self.centralwidget)
        self.radioButton.setObjectName("radioButton")
        self.horizontalLayout_8.addWidget(self.radioButton)
        self.pushButton_1_test = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton_1_test.setObjectName("pushButton_1_test")
        self.horizontalLayout_8.addWidget(self.pushButton_1_test)
        self.pushButton_2_test = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton_2_test.setObjectName("pushButton_2_test")
        self.horizontalLayout_8.addWidget(self.pushButton_2_test)
        self.pushButton_3_test = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton_3_test.setObjectName("pushButton_3_test")
        self.horizontalLayout_8.addWidget(self.pushButton_3_test)
        self.pushButton_4_test = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton_4_test.setObjectName("pushButton_4_test")
        self.horizontalLayout_8.addWidget(self.pushButton_4_test)
        self.comboBox_Cbor = QtWidgets.QComboBox(parent=self.centralwidget)
        self.comboBox_Cbor.setObjectName("comboBox_Cbor")
        self.horizontalLayout_8.addWidget(self.comboBox_Cbor)
        self.gridLayout.addLayout(self.horizontalLayout_8, 7, 0, 1, 1)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setContentsMargins(-1, 1, -1, 1)
        self.horizontalLayout_3.setSpacing(1)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_console = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_console.setObjectName("label_console")
        self.horizontalLayout_3.addWidget(self.label_console)
        self.gridLayout.addLayout(self.horizontalLayout_3, 10, 0, 1, 1)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_3 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_7.addWidget(self.label_3)
        self.comboBox_2 = QtWidgets.QComboBox(parent=self.centralwidget)
        self.comboBox_2.setObjectName("comboBox_2")
        self.horizontalLayout_7.addWidget(self.comboBox_2)
        self.pb_plot = QtWidgets.QPushButton(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pb_plot.sizePolicy().hasHeightForWidth())
        self.pb_plot.setSizePolicy(sizePolicy)
        self.pb_plot.setMaximumSize(QtCore.QSize(300, 16777215))
        self.pb_plot.setCheckable(False)
        self.pb_plot.setObjectName("pb_plot")
        self.horizontalLayout_7.addWidget(self.pb_plot)
        self.horizontalLayout_7.setStretch(0, 1)
        self.horizontalLayout_7.setStretch(1, 4)
        self.horizontalLayout_7.setStretch(2, 2)
        self.gridLayout.addLayout(self.horizontalLayout_7, 8, 0, 1, 1)
        self.horizontalLayout_9_console = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9_console.setContentsMargins(-1, 0, -1, 0)
        self.horizontalLayout_9_console.setSpacing(0)
        self.horizontalLayout_9_console.setObjectName("horizontalLayout_9_console")
        self.listView = QtWidgets.QListView(parent=self.centralwidget)
        self.listView.setMinimumSize(QtCore.QSize(0, 100))
        self.listView.setMaximumSize(QtCore.QSize(16777215, 200))
        self.listView.setObjectName("listView")
        self.horizontalLayout_9_console.addWidget(self.listView)
        self.gridLayout.addLayout(self.horizontalLayout_9_console, 11, 0, 1, 1)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.pb_start_sample = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pb_start_sample.setObjectName("pb_start_sample")
        self.horizontalLayout_5.addWidget(self.pb_start_sample)
        self.pb_stop_sample = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pb_stop_sample.setObjectName("pb_stop_sample")
        self.horizontalLayout_5.addWidget(self.pb_stop_sample)
        self.lable_progress = QtWidgets.QLabel(parent=self.centralwidget)
        self.lable_progress.setObjectName("lable_progress")
        self.horizontalLayout_5.addWidget(self.lable_progress)
        self.progressBar = QtWidgets.QProgressBar(parent=self.centralwidget)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.horizontalLayout_5.addWidget(self.progressBar)
        self.gridLayout.addLayout(self.horizontalLayout_5, 3, 0, 1, 1)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.Webwidget = QtWebEngineWidgets.QWebEngineView(parent=self.centralwidget)
        self.Webwidget.setMinimumSize(QtCore.QSize(0, 270))
        self.Webwidget.setObjectName("Webwidget")
        self.horizontalLayout_6.addWidget(self.Webwidget)
        self.gridLayout.addLayout(self.horizontalLayout_6, 9, 0, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pb_scan = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pb_scan.setObjectName("pb_scan")
        self.horizontalLayout_2.addWidget(self.pb_scan)
        self.comboBox = QtWidgets.QComboBox(parent=self.centralwidget)
        self.comboBox.setObjectName("comboBox")
        self.horizontalLayout_2.addWidget(self.comboBox)
        self.pb_connect = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pb_connect.setObjectName("pb_connect")
        self.horizontalLayout_2.addWidget(self.pb_connect)
        self.pb_disconnect = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pb_disconnect.setObjectName("pb_disconnect")
        self.horizontalLayout_2.addWidget(self.pb_disconnect)
        self.gridLayout.addLayout(self.horizontalLayout_2, 2, 0, 1, 1)
        self.horizontalLayout_1_header = QtWidgets.QHBoxLayout()
        self.horizontalLayout_1_header.setContentsMargins(0, -1, 0, 0)
        self.horizontalLayout_1_header.setSpacing(0)
        self.horizontalLayout_1_header.setObjectName("horizontalLayout_1_header")
        self.logo = QtWidgets.QLabel(parent=self.centralwidget)
        self.logo.setMinimumSize(QtCore.QSize(150, 70))
        self.logo.setMaximumSize(QtCore.QSize(200, 90))
        self.logo.setLineWidth(0)
        self.logo.setMidLineWidth(-1)
        self.logo.setText("")
        self.logo.setPixmap(QtGui.QPixmap("../pythonThermalPlate/Alogo.png"))
        self.logo.setScaledContents(True)
        self.logo.setObjectName("logo")
        self.horizontalLayout_1_header.addWidget(self.logo)
        self.label_6 = QtWidgets.QLabel(parent=self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(34)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setAutoFillBackground(False)
        self.label_6.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_1_header.addWidget(self.label_6)
        self.gridLayout.addLayout(self.horizontalLayout_1_header, 1, 0, 1, 1)
        self.horizontalLayout_4_config = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4_config.setContentsMargins(5, 5, 300, -1)
        self.horizontalLayout_4_config.setObjectName("horizontalLayout_4_config")
        self.lable_config = QtWidgets.QLabel(parent=self.centralwidget)
        self.lable_config.setMaximumSize(QtCore.QSize(140, 16777215))
        self.lable_config.setObjectName("lable_config")
        self.horizontalLayout_4_config.addWidget(self.lable_config)
        self.label = QtWidgets.QLabel(parent=self.centralwidget)
        self.label.setObjectName("label")
        self.horizontalLayout_4_config.addWidget(self.label)
        self.textEdit = QtWidgets.QTextEdit(parent=self.centralwidget)
        self.textEdit.setMaximumSize(QtCore.QSize(16777215, 30))
        self.textEdit.setStyleSheet("")
        self.textEdit.setObjectName("textEdit")
        self.horizontalLayout_4_config.addWidget(self.textEdit)
        self.label_2 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_4_config.addWidget(self.label_2)
        self.cb60 = QtWidgets.QCheckBox(parent=self.centralwidget)
        self.cb60.setMaximumSize(QtCore.QSize(100, 16777215))
        self.cb60.setObjectName("cb60")
        self.horizontalLayout_4_config.addWidget(self.cb60)
        self.cb30 = QtWidgets.QCheckBox(parent=self.centralwidget)
        self.cb30.setMaximumSize(QtCore.QSize(100, 16777215))
        self.cb30.setObjectName("cb30")
        self.horizontalLayout_4_config.addWidget(self.cb30)
        self.cb15 = QtWidgets.QCheckBox(parent=self.centralwidget)
        self.cb15.setMaximumSize(QtCore.QSize(100, 16777215))
        self.cb15.setObjectName("cb15")
        self.horizontalLayout_4_config.addWidget(self.cb15)
        self.gridLayout.addLayout(self.horizontalLayout_4_config, 5, 0, 2, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 952, 25))
        self.menubar.setMinimumSize(QtCore.QSize(0, 25))
        self.menubar.setMaximumSize(QtCore.QSize(16777215, 25))
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.menubar.setFont(font)
        self.menubar.setDefaultUp(True)
        self.menubar.setNativeMenuBar(False)
        self.menubar.setObjectName("menubar")
        self.menuEP_TOOL = QtWidgets.QMenu(parent=self.menubar)
        self.menuEP_TOOL.setObjectName("menuEP_TOOL")
        self.menuSHAKER = QtWidgets.QMenu(parent=self.menubar)
        self.menuSHAKER.setObjectName("menuSHAKER")
        self.menuVIBRATION = QtWidgets.QMenu(parent=self.menubar)
        self.menuVIBRATION.setObjectName("menuVIBRATION")
        self.menuABOUT = QtWidgets.QMenu(parent=self.menubar)
        self.menuABOUT.setObjectName("menuABOUT")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar.addAction(self.menuEP_TOOL.menuAction())
        self.menubar.addAction(self.menuSHAKER.menuAction())
        self.menubar.addAction(self.menuVIBRATION.menuAction())
        self.menubar.addAction(self.menuABOUT.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton_2.setText(_translate("MainWindow", "pb_2"))
        self.pushButton_3.setText(_translate("MainWindow", "pb_3"))
        self.pushButton_4.setText(_translate("MainWindow", "pb_4"))
        self.pushButton_5.setText(_translate("MainWindow", "Set-Time"))
        self.pushButton_6.setText(_translate("MainWindow", "pb_6"))
        self.pushButton.setText(_translate("MainWindow", "pb_7"))
        self.radioButton.setText(_translate("MainWindow", "Cbor mode (JIG Only)"))
        self.pushButton_1_test.setText(_translate("MainWindow", "Pb-1 test"))
        self.pushButton_2_test.setText(_translate("MainWindow", "Pb-2 test"))
        self.pushButton_3_test.setText(_translate("MainWindow", "Pb-3 test"))
        self.pushButton_4_test.setText(_translate("MainWindow", "Pb-4 test"))
        self.label_console.setText(_translate("MainWindow", "Console Log"))
        self.label_3.setText(_translate("MainWindow", "TEST SELECT : "))
        self.pb_plot.setText(_translate("MainWindow", "PLOT Result"))
        self.pb_start_sample.setText(_translate("MainWindow", "START SAMPLE"))
        self.pb_stop_sample.setText(_translate("MainWindow", "STOP SAMPLE"))
        self.lable_progress.setText(_translate("MainWindow", " Progress "))
        self.pb_scan.setText(_translate("MainWindow", "SCAN BLE DEVICE"))
        self.pb_connect.setText(_translate("MainWindow", "CONNECT"))
        self.pb_disconnect.setText(_translate("MainWindow", "DISCONNECT"))
        self.label_6.setText(_translate("MainWindow", "AUGURY LAB DASHBOARD"))
        self.lable_config.setText(_translate("MainWindow", "CONFIG PARAMETER :"))
        self.label.setText(_translate("MainWindow", "Time 0-5000 [ms]"))
        self.label_2.setText(_translate("MainWindow", "Sensetivity: "))
        self.cb60.setText(_translate("MainWindow", "+-60g"))
        self.cb30.setText(_translate("MainWindow", "+-30g"))
        self.cb15.setText(_translate("MainWindow", "+-15g"))
        self.menuEP_TOOL.setTitle(_translate("MainWindow", "EP TOOL"))
        self.menuSHAKER.setTitle(_translate("MainWindow", "SHAKER"))
        self.menuVIBRATION.setTitle(_translate("MainWindow", "VIBRATION"))
        self.menuABOUT.setTitle(_translate("MainWindow", "ABOUT"))
from PyQt5 import QtWebEngineWidgets


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
