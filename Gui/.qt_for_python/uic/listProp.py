# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'g:\Forschung\Gui\listProp.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(412, 351)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.elemProperties = QtWidgets.QTableWidget(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.elemProperties.sizePolicy().hasHeightForWidth())
        self.elemProperties.setSizePolicy(sizePolicy)
        self.elemProperties.setMouseTracking(False)
        self.elemProperties.setTabletTracking(False)
        self.elemProperties.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.elemProperties.setAutoFillBackground(False)
        self.elemProperties.setAutoScroll(True)
        self.elemProperties.setAlternatingRowColors(False)
        self.elemProperties.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.elemProperties.setWordWrap(False)
        self.elemProperties.setCornerButtonEnabled(False)
        self.elemProperties.setObjectName("elemProperties")
        self.elemProperties.setColumnCount(2)
        self.elemProperties.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.elemProperties.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.elemProperties.setHorizontalHeaderItem(1, item)
        self.elemProperties.horizontalHeader().setVisible(True)
        self.elemProperties.horizontalHeader().setCascadingSectionResizes(False)
        self.elemProperties.horizontalHeader().setDefaultSectionSize(190)
        self.elemProperties.horizontalHeader().setStretchLastSection(False)
        self.elemProperties.verticalHeader().setSortIndicatorShown(False)
        self.elemProperties.verticalHeader().setStretchLastSection(False)
        self.gridLayout.addWidget(self.elemProperties, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        item = self.elemProperties.horizontalHeaderItem(0)
        item.setText(_translate("Form", "Property"))
        item = self.elemProperties.horizontalHeaderItem(1)
        item.setText(_translate("Form", "Detail"))