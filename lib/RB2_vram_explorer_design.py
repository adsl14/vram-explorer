# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RB2_vram_explorer_design.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(841, 746)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 20, 821, 651))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.listView = QtWidgets.QListView(self.horizontalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listView.sizePolicy().hasHeightForWidth())
        self.listView.setSizePolicy(sizePolicy)
        self.listView.setObjectName("listView")
        self.horizontalLayout.addWidget(self.listView)
        self.frame = QtWidgets.QFrame(self.horizontalLayoutWidget)
        self.frame.setEnabled(True)
        self.frame.setFrameShape(QtWidgets.QFrame.Box)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.imageTexture = QtWidgets.QLabel(self.frame)
        self.imageTexture.setGeometry(QtCore.QRect(40, 60, 461, 501))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.imageTexture.sizePolicy().hasHeightForWidth())
        self.imageTexture.setSizePolicy(sizePolicy)
        self.imageTexture.setText("")
        self.imageTexture.setScaledContents(True)
        self.imageTexture.setAlignment(QtCore.Qt.AlignCenter)
        self.imageTexture.setObjectName("imageTexture")
        self.exportButton = QtWidgets.QPushButton(self.frame)
        self.exportButton.setGeometry(QtCore.QRect(370, 580, 75, 23))
        self.exportButton.setObjectName("exportButton")
        self.importButton = QtWidgets.QPushButton(self.frame)
        self.importButton.setGeometry(QtCore.QRect(450, 580, 75, 23))
        self.importButton.setObjectName("importButton")
        self.sizeImageText = QtWidgets.QLabel(self.frame)
        self.sizeImageText.setGeometry(QtCore.QRect(20, 10, 150, 16))
        self.sizeImageText.setText("")
        self.sizeImageText.setAlignment(QtCore.Qt.AlignCenter)
        self.sizeImageText.setObjectName("sizeImageText")
        self.encodingImageText = QtWidgets.QLabel(self.frame)
        self.encodingImageText.setGeometry(QtCore.QRect(379, 10, 150, 16))
        self.encodingImageText.setText("")
        self.encodingImageText.setAlignment(QtCore.Qt.AlignCenter)
        self.encodingImageText.setObjectName("encodingImageText")
        self.mipMapsImageText = QtWidgets.QLabel(self.frame)
        self.mipMapsImageText.setGeometry(QtCore.QRect(200, 10, 150, 16))
        self.mipMapsImageText.setText("")
        self.mipMapsImageText.setAlignment(QtCore.Qt.AlignCenter)
        self.mipMapsImageText.setObjectName("mipMapsImageText")
        self.horizontalLayout.addWidget(self.frame)
        self.exportAllButton = QtWidgets.QPushButton(self.centralwidget)
        self.exportAllButton.setGeometry(QtCore.QRect(90, 680, 75, 23))
        self.exportAllButton.setObjectName("exportAllButton")
        self.fileNameText = QtWidgets.QLabel(self.centralwidget)
        self.fileNameText.setGeometry(QtCore.QRect(0, 0, 841, 20))
        self.fileNameText.setText("")
        self.fileNameText.setAlignment(QtCore.Qt.AlignCenter)
        self.fileNameText.setObjectName("fileNameText")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 841, 21))
        self.menubar.setObjectName("menubar")
        self.menuFIle = QtWidgets.QMenu(self.menubar)
        self.menuFIle.setObjectName("menuFIle")
        self.menuAbout = QtWidgets.QMenu(self.menubar)
        self.menuAbout.setObjectName("menuAbout")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setSizeGripEnabled(True)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionClose = QtWidgets.QAction(MainWindow)
        self.actionClose.setObjectName("actionClose")
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionAuthor = QtWidgets.QAction(MainWindow)
        self.actionAuthor.setObjectName("actionAuthor")
        self.actionCredits = QtWidgets.QAction(MainWindow)
        self.actionCredits.setObjectName("actionCredits")
        self.menuFIle.addAction(self.actionOpen)
        self.menuFIle.addAction(self.actionSave)
        self.menuFIle.addAction(self.actionClose)
        self.menuAbout.addAction(self.actionAuthor)
        self.menuAbout.addAction(self.actionCredits)
        self.menubar.addAction(self.menuFIle.menuAction())
        self.menubar.addAction(self.menuAbout.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "RB2 vram explorer 1.3.1"))
        self.exportButton.setText(_translate("MainWindow", "E&xport..."))
        self.importButton.setText(_translate("MainWindow", "I&mport..."))
        self.exportAllButton.setText(_translate("MainWindow", "Export all"))
        self.menuFIle.setTitle(_translate("MainWindow", "&File"))
        self.menuAbout.setTitle(_translate("MainWindow", "About"))
        self.actionOpen.setText(_translate("MainWindow", "O&pen..."))
        self.actionOpen.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.actionClose.setText(_translate("MainWindow", "&Exit"))
        self.actionClose.setShortcut(_translate("MainWindow", "Ctrl+Q"))
        self.actionSave.setText(_translate("MainWindow", "Save"))
        self.actionSave.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.actionAuthor.setText(_translate("MainWindow", "A&uthor"))
        self.actionAuthor.setShortcut(_translate("MainWindow", "Ctrl+A"))
        self.actionCredits.setText(_translate("MainWindow", "C&redits"))
        self.actionCredits.setShortcut(_translate("MainWindow", "Ctrl+C"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

