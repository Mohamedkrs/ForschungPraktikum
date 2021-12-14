import os, glob
import logging
from distutils.util import strtobool
from functools import partial

import cimpy
from pathlib import Path
import sys
from PyQt5 import QtGui, QtWidgets, Qt, QtCore
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
import DataManager

logging.basicConfig(filename='importCIGREMV.log', level=logging.INFO, filemode='w')


def errorMessages(message):
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Warning)
    msgBox.setText(message)
    msgBox.setWindowTitle("Warning")
    msgBox.exec_()


class MainWindow(QDialog):
    foo_dir = ""
    data_manager = DataManager.ManageElements()
    tableWt = False
    firstLoad = True
    mRIDold = None

    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("Gui.ui", self)
        # self.elemProperties.setMouseTracking(True)
        # self.current_hover = [0, 0]
        ##self.elemProperties.itemEntered.connect(self.cellHover)

        self.noWheelCombos = []
        self.list = self.findChildren(QtWidgets.QCheckBox)
        self.searchBtn.clicked.connect(self.browse_files)
        self.loadBtn.clicked.connect(self.import_from_xml)
        self.elemView.itemClicked.connect(self.clicked)
        #self.elemView.itemSelectionChanged.connect(self.clicked)
        self.exportBtn.clicked.connect(self.export)
        self.elemProperties.itemChanged.connect(self.current_mRID)
        self.elemProperties.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.filterBtn.clicked.connect(self.filtering)
        self.resetBtn.clicked.connect(self.import_from_xml)

    def import_from_xml(self):
        self.elemView.clear()
        self.elemProperties.clearContents()
        self.elemProperties.setRowCount(0)
        file_path = self.folderPath.text()
        # Parse importedXml Files ###
        if not file_path:
            errorMessages("The Path is Empty")
            return
        example = Path(file_path).resolve()
        xml_files = []
        for file in example.glob('*.xml'):
            xml_files.append(str(file.absolute()))
        if len(xml_files) == 0:
            errorMessages("The folder doesnt contain any xml files")
            return
        if not self.exportBtn.isEnabled():
            self.exportBtn.setEnabled(True)
            self.filterBtn.setEnabled(True)
            self.resetBtn.setEnabled(True)
        cgmesver = "cgmes_v2_4_15"
        import_result = cimpy.cim_import(xml_files, cgmesver)
        self.data_manager.data = import_result
        elemViewData=self.data_manager.import_eq_data()
        self.elemView.addItems(elemViewData)

        for key in self.data_manager.data['meta_info']['profiles']:
            for checkbox in self.list:
                if key == checkbox.text():
                    checkbox.setCheckable(True)
                    checkbox.setChecked(True)
                    break

    def current_mRID(self):
        if not self.data_manager.elements[self.elemView.currentItem().text()] == self.mRIDold:
            self.mRIDold = self.data_manager.elements[self.elemView.currentItem().text()]

    def clicked(self):

        if self.firstLoad:  # set old mRID
            self.firstLoad = False
            self.mRIDold = self.data_manager.elements[self.elemView.currentItem().text()]
        self.update_data(self.mRIDold)
        mRID = self.data_manager.elements[self.elemView.currentItem().text()]
        row = 0
        self.elemProperties.setRowCount(0)
        for key, val in self.data_manager.data['topology'][mRID].__dict__.items():
            if val is None:

                property_name = QTableWidgetItem(key)
                property_name.setFlags(property_name.flags() ^ QtCore.Qt.ItemIsEditable)
                property_detail = QTableWidgetItem("None")
                property_detail.setFlags(property_name.flags() ^ QtCore.Qt.ItemIsEditable)
                self.elemProperties.insertRow(self.elemProperties.rowCount())
                self.elemProperties.setItem(row, 0, property_name)
                self.elemProperties.setItem(row, 1, property_detail)
            elif isinstance(val, (str, int, float, bool)):
                self.elemProperties.insertRow(self.elemProperties.rowCount())
                property_name = QTableWidgetItem(key)
                property_name.setFlags(property_name.flags() ^ QtCore.Qt.ItemIsEditable)

                detail = val
                if detail is None:
                    property_detail = QTableWidgetItem("None")
                else:
                    property_detail = QTableWidgetItem(str(detail))
                self.elemProperties.setItem(row, 0, property_name)
                if "mRID" in key:
                    property_detail.setFlags(property_detail.flags() ^ QtCore.Qt.ItemIsEditable)
                if isinstance(detail, bool):
                    c = QtWidgets.QComboBox()
                    self.noWheelCombos.append(c)
                    if detail:
                        c.addItems([str(detail), "False"])
                    else:
                        c.addItems([str(detail), "True"])
                    c.installEventFilter(self)
                    self.elemProperties.setCellWidget(row, 1, c)

                elif "operatingMode" in key:
                    c = QtWidgets.QComboBox()
                    c.addItems(
                        [val, 'cell11', 'cell12', 'cell13',
                         'cell15', ])
                    self.elemProperties.setCellWidget(row, 1, c)
                else:
                    self.elemProperties.setItem(row, 1, property_detail)
            elif isinstance(val, list):
                property_name = QTableWidgetItem(key)
                property_name.setFlags(property_name.flags() ^ QtCore.Qt.ItemIsEditable)
                detail = val[0].__dict__["mRID"]
                #c = QtWidgets.QButtonGroup()
                btn1 = QtWidgets.QPushButton()
                btn1.setText("list")
                btn1.clicked.connect(self.handleButtonClicked)
                self.elemProperties.insertRow(self.elemProperties.rowCount())
                self.elemProperties.setItem(row, 0, property_name)
                self.elemProperties.setCellWidget(row, 1, btn1)
                # self.elemProperties.setItem(row, 1, property_name)
            elif "mRID" in val.__dict__:
                property_name = QTableWidgetItem(key)
                property_name.setFlags(property_name.flags() ^ QtCore.Qt.ItemIsEditable)
                detail = val.__dict__["mRID"]
                btn = QtWidgets.QPushButton()

                if detail in self.data_manager.elements.values():
                    btn.setText([k for k, v in self.data_manager.elements.items() if v == detail][0])
                else:
                    btn.setText(detail)
                btn.clicked.connect(self.handleButtonClicked)
                property_detail = QTableWidgetItem(str(detail))
                property_detail.setFlags(property_detail.flags() ^ QtCore.Qt.ItemIsEditable)
                self.elemProperties.insertRow(self.elemProperties.rowCount())
                # self.elemProperties.setItem(row, 1, property_detail)
                self.elemProperties.setItem(row, 0, property_name)
                self.elemProperties.setCellWidget(row, 1, btn)
            else:
                property_name = QTableWidgetItem(key)
                property_name.setFlags(property_name.flags() ^ QtCore.Qt.ItemIsEditable)
                # detail = self.data_manager.data['topology'][mRID].__dict__[key][0].__dict__["mRID"]
                btn = QtWidgets.QPushButton()
                btn.setText("another class")
                btn.clicked.connect(self.handleButtonClicked)
                self.elemProperties.insertRow(self.elemProperties.rowCount())
                self.elemProperties.setItem(row, 0, property_name)
                self.elemProperties.setCellWidget(row, 1, btn)
                # self.elemProperties.setItem(row, 1, property_name)

            row += 1

    def update_data(self, mRID):

        for item in range(self.elemProperties.rowCount()):

            widget = self.elemProperties.cellWidget(item, 1)
            if isinstance(widget, QtWidgets.QComboBox):
                if self.elemProperties.cellWidget(item, 1).currentText() in ["True", "False"]:
                    self.data_manager.data['topology'][mRID].__dict__[
                        self.elemProperties.item(item, 0).text()] = bool(
                        strtobool(self.elemProperties.cellWidget(item, 1).currentText()))
                else:
                    self.data_manager.data['topology'][mRID].__dict__[
                        self.elemProperties.item(item, 0).text()] = self.elemProperties.cellWidget(item,
                                                                                                   1).currentText()

            elif not isinstance(widget, QtWidgets.QPushButton):
                self.data_manager.data['topology'][mRID].__dict__[
                    self.elemProperties.item(item, 0).text()] = self.elemProperties.item(item, 1).text()

            # print(self.elemProperties.item(item,0).text())

    # Export data depending on checked boxes
    def export(self):
        self.update_data(self.mRIDold)
        dialog = QFileDialog()
        output_dir = dialog.getExistingDirectory(self, 'Select a Folder')
        if not output_dir:
            return
        if os.path.isdir(output_dir):
            qm = QMessageBox
            question = qm.question(self, '', "This Folder will be overridden, continue?", qm.Yes | qm.No)
            if question == qm.No:
                return
        active_profile_list = []
        for checkbox in self.list:
            if checkbox.isChecked():
                active_profile_list.append(checkbox.text())

        export_data = cimpy.sincal_Pf(self.data_manager.data)
        for filename12 in glob.glob(output_dir + "/*"):
            os.remove(filename12)
        cimpy.cim_export(export_data, output_dir + "/output", "cgmes_v2_4_15", active_profile_list)

    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.Wheel and
                source in self.noWheelCombos):
            return True
        return super(MainWindow, self).eventFilter(source, event)

    def browse_files(self):
        dialog = QFileDialog()
        importpath = dialog.getExistingDirectory(self, 'Select a CIM Folder')
        if importpath:
            self.folderPath.setText(importpath)

    def handleButtonClicked(self):
        # button = QtGui.qApp.focusWidget()
        button = self.sender()
        index = self.elemProperties.indexAt(button.pos())
        if index.isValid():
            if self.elemProperties.cellWidget(index.row(), index.column()).text() in self.data_manager.elements.keys():
                itemtext = self.elemProperties.cellWidget(index.row(), index.column()).text()
                items = self.elemView.findItems(itemtext, QtCore.Qt.MatchExactly)
                self.elemView.setCurrentRow(self.elemView.row(items[0]))
            elif self.elemProperties.cellWidget(index.row(), index.column()).text() == "list":
                mRID = self.data_manager.elements[self.elemView.currentItem().text()]
                self.show_list_data(
                    self.data_manager.data['topology'][mRID].__dict__[self.elemProperties.item(index.row(), 0).text()])

    def show_list_data(self, data):
        for dicts in data:
            if dicts.__dict__["mRID"] in self.data_manager.elements.values():
                for k,c in self.data_manager.elements.items():
                    if c == dicts.__dict__["mRID"]:
                        print(k)
            else:
                print("nope")
                
        #table = ListData()
        #table.data = data
        #print(data)
        #table.displayView()

        #table.exec()
    def printint(self):
        print("hi")

    def filtering(self):
        filter = Filtering()
        filter.exec()
        res = {}
        if filter.elem_andor_prop != '':
            res = self.data_manager.filter_data(filter.elem, filter.prop, filter.detail, filter.elem_andor_prop,
                                                filter.prop_andor_elem)
        if len(res) > 0:
            self.elemProperties.setRowCount(0)
            self.elemView.clear()
            self.elemView.addItems(res)
        elif filter.elem_andor_prop != '':
            errorMessages("No Matches Found")


class ListData(QDialog):
    data = []
    data_managertwo = DataManager.ManageElements()
    tabledata = {}
    def __init__(self):
        super(ListData, self).__init__()
        loadUi("ListData.ui", self)
        self.elemView.itemClicked.connect(self.clicked)
        #self.data_managertwo.data=self.data
    def expand_dict(self):
        for dicts in self.data:
            print("testing")
            print(dicts.__dict__)
            self.data_managertwo.data.append(dicts.__dict__)
    def displayView(self):
        self.expand_dict()
        self.elemView.addItems(self.data_managertwo.import_eq_data())

    def clicked(self):

        mRID = "_48746FEF975E4732921B39AA07924D08"
        row = 0
        self.elemProperties.setRowCount(0)
        for key, val in self.tabledata.items():
            if self.tabledata[key] is None:

                property_name = QTableWidgetItem(key)
                property_name.setFlags(property_name.flags() ^ QtCore.Qt.ItemIsEditable)
                property_detail = QTableWidgetItem("None")
                property_detail.setFlags(property_name.flags() ^ QtCore.Qt.ItemIsEditable)
                self.elemProperties.insertRow(self.elemProperties.rowCount())
                self.elemProperties.setItem(row, 0, property_name)
                self.elemProperties.setItem(row, 1, property_detail)
            elif isinstance(self.tabledata[key], (str, int, float, bool)):
                self.elemProperties.insertRow(self.elemProperties.rowCount())
                property_name = QTableWidgetItem(key)
                property_name.setFlags(property_name.flags() ^ QtCore.Qt.ItemIsEditable)

                detail = self.tabledata[key]
                if detail is None:
                    property_detail = QTableWidgetItem("None")
                else:
                    property_detail = QTableWidgetItem(str(detail))
                self.elemProperties.setItem(row, 0, property_name)
                if "mRID" in key:
                    property_detail.setFlags(property_detail.flags() ^ QtCore.Qt.ItemIsEditable)
                if isinstance(detail, bool):
                    c = QtWidgets.QComboBox()
                    # self.noWheelCombos.append(c)
                    if detail:
                        c.addItems([str(detail), "False"])
                    else:
                        c.addItems([str(detail), "True"])
                    c.installEventFilter(self)
                    self.elemProperties.setCellWidget(row, 1, c)

                elif "operatingMode" in key:
                    c = QtWidgets.QComboBox()
                    c.addItems(
                        [self.tabledata[key], 'cell11', 'cell12', 'cell13',
                         'cell15', ])
                    self.elemProperties.setCellWidget(row, 1, c)
                else:
                    self.elemProperties.setItem(row, 1, property_detail)
            elif isinstance(self.tabledata[key], list):
                property_name = QTableWidgetItem(key)
                property_name.setFlags(property_name.flags() ^ QtCore.Qt.ItemIsEditable)
                detail = self.tabledata[key][0].__dict__["mRID"]
                btn1 = QtWidgets.QPushButton()
                btn1.setText("list")
                # btn1.clicked.connect(self.handleButtonClicked)
                self.elemProperties.insertRow(self.elemProperties.rowCount())
                self.elemProperties.setItem(row, 0, property_name)
                self.elemProperties.setCellWidget(row, 1, btn1)
                # self.elemProperties.setItem(row, 1, property_name)
            elif "mRID" in self.tabledata[key].__dict__:
                property_name = QTableWidgetItem(key)
                property_name.setFlags(property_name.flags() ^ QtCore.Qt.ItemIsEditable)
                detail = self.tabledata[key].__dict__["mRID"]
                btn = QtWidgets.QPushButton()

                # if detail in self.data_manager.elements.values():
                # btn.setText([k for k, v in self.data_manager.elements.items() if v == detail][0])
                # else:
                btn.setText(detail)
                # btn.clicked.connect(self.handleButtonClicked)
                property_detail = QTableWidgetItem(str(detail))
                property_detail.setFlags(property_detail.flags() ^ QtCore.Qt.ItemIsEditable)
                self.elemProperties.insertRow(self.elemProperties.rowCount())
                # self.elemProperties.setItem(row, 1, property_detail)
                self.elemProperties.setItem(row, 0, property_name)
                self.elemProperties.setCellWidget(row, 1, btn)
            else:
                property_name = QTableWidgetItem(key)
                property_name.setFlags(property_name.flags() ^ QtCore.Qt.ItemIsEditable)
                # detail = self.data_manager.data['topology'][mRID].__dict__[key][0].__dict__["mRID"]
                btn = QtWidgets.QPushButton()
                btn.setText("another class")
                # btn.clicked.connect(self.handleButtonClicked)
                self.elemProperties.insertRow(self.elemProperties.rowCount())
                self.elemProperties.setItem(row, 0, property_name)
                self.elemProperties.setCellWidget(row, 1, btn)
                # self.elemProperties.setItem(row, 1, property_name)

            row += 1


class Filtering(QDialog):
    elem = ""
    prop = ""
    detail = ""
    elem_andor_prop = ""
    prop_andor_elem = ""

    def __init__(self):
        super(Filtering, self).__init__()
        loadUi("filter.ui", self)
        self.okBtn.clicked.connect(self.setDetails)
        self.cancelBtn.clicked.connect(self.close)

    def setDetails(self):
        self.elem = self.elemText.text()
        self.prop = self.propText.text()
        self.detail = self.detText.text()
        self.elem_andor_prop = self.elem_andor_prop_cBox.currentText()
        self.prop_andor_elem = self.prop_andor_det_cBox.currentText()
        self.close()


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(main_window)
    widget.adjustSize()
    widget.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
