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


def messages(message, title):
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Warning)
    msgBox.setText(message)
    msgBox.setWindowTitle(title)
    msgBox.exec_()


class StandardItem(Qt.QStandardItem):
    def __init__(self, txt='', font_size=12, set_bold=False, color=Qt.QColor(0, 0, 0)):
        super().__init__()

        fnt = Qt.QFont('Open Sans', font_size)
        fnt.setBold(set_bold)

        self.setEditable(False)
        self.setForeground(color)
        self.setFont(fnt)
        self.setText(txt)


class MainWindow(QDialog):
    foo_dir = ""
    data_manager = DataManager.ManageElements()
    firstLoad = True
    modified = False
    mRIDold = None

    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("Gui.ui", self)

        self.noWheelCombos = []
        self.checkBoxList = self.findChildren(QtWidgets.QCheckBox)
        self.searchBtn.clicked.connect(self.browse_files)
        self.loadBtn.clicked.connect(self.import_from_xml)

        self.exportBtn.clicked.connect(self.export)
        self.elemProperties.itemChanged.connect(self.current_mRID)
        self.elemProperties.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.filterBtn.clicked.connect(self.filtering)
        self.resetBtn.clicked.connect(self.import_from_xml)
        ######
        self.treeView.doubleClicked.connect(self.clicked)

    def getValue(self, val):
        print(val.data())
        print(val.row())
        print(val.column())
        print(val.parent().row())

    def rightMenuShow(self):  # shows drop down menu if left clicked
        data = self.data_manager.data['topology']['_013708A181A1425AA4002C36E0D092BA'].__dict__
        rightMenu = QMenu()
        removeAction = QAction(u"Show Dynamics", self, triggered=lambda: self.show_list_data(data))
        rightMenu.addAction(removeAction)

        # addAction = QAction(u"add", self, triggered=self.addItem)  # You can also specify custom object events
        # rightMenu.addAction(addAction)
        rightMenu.exec_(QtGui.QCursor.pos())

    def import_from_xml(self):

        self.elemProperties.clearContents()
        self.elemProperties.setRowCount(0)
        file_path = self.folderPath.text()
        # Parse importedXml Files ###
        if not file_path:
            messages("The Path is Empty", "Warning")
            return
        example = Path(file_path).resolve()
        xml_files = []
        for file in example.glob('*.xml'):
            xml_files.append(str(file.absolute()))
        if len(xml_files) == 0:
            messages("The folder doesnt contain any xml files", "Warning")
            return
        if not self.exportBtn.isEnabled():
            self.exportBtn.setEnabled(True)
            self.filterBtn.setEnabled(True)
            self.resetBtn.setEnabled(True)
        cgmesver = "cgmes_v2_4_15"
        import_result = cimpy.cim_import(xml_files, cgmesver)
        self.data_manager.data = import_result

        treeModel = Qt.QStandardItemModel()
        rootNode = treeModel.invisibleRootItem()

        for checkbox in self.checkBoxList:
            if checkbox.text() in self.data_manager.data['meta_info']['profiles'].keys():
                profile = StandardItem(checkbox.text(), 9, set_bold=True)

                for elem in self.data_manager.import_eq_data(checkbox.text()):
                    profile.appendRow(StandardItem(elem, 9))
                rootNode.appendRow(profile)
                self.treeView.setModel(treeModel)

                checkbox.setCheckable(True)
                checkbox.setChecked(True)
            else:
                checkbox.setChecked(False)
                checkbox.setCheckable(False)

    def current_mRID(self):
        #print("item changed")
        self.modified = True
        if not self.data_manager.profile_elements[self.treeView.currentIndex().parent().data()][
                   self.treeView.currentIndex().data()] == self.mRIDold:
            self.mRIDold = self.data_manager.profile_elements[self.treeView.currentIndex().parent().data()][
                self.treeView.currentIndex().data()]

    def clicked(self, val):
        # print(val.data())
        # print(val.text())
        mRID = ""
        if val.data() is not None:
            try:
                mRID = self.data_manager.profile_elements[val.parent().data()][val.data()]
                if self.firstLoad:  # set old mRID
                    self.firstLoad = False
                    self.mRIDold = self.data_manager.profile_elements[val.parent().data()][val.data()]
            except:
                return
        else:
            try:
                mRID = self.data_manager.profile_elements[val.parent().text()][val.text()]
            except:
                return

        if self.modified: self.update_data(self.mRIDold)
        
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
                    c.currentTextChanged.connect(self.current_mRID)
                    c.installEventFilter(self)
                    self.elemProperties.setCellWidget(row, 1, c)

                elif "operatingMode" in key:
                    c = QtWidgets.QComboBox()
                    c.addItems(
                        [val, 'cell11', 'cell12', 'cell13',
                         'cell15', ])
                    c.currentTextChanged.connect(self.current_mRID)
                    self.elemProperties.setCellWidget(row, 1, c)
                else:
                    self.elemProperties.setItem(row, 1, property_detail)
            elif isinstance(val, list):
                property_name = QTableWidgetItem(key)
                property_name.setFlags(property_name.flags() ^ QtCore.Qt.ItemIsEditable)
                detail = val[0].__dict__["mRID"]
                btn1 = QtWidgets.QPushButton()
                btn1.setText("show details")

                for dicts in self.data_manager.data['topology'][mRID].__dict__[key]:
                    if dicts.__dict__["mRID"] in self.data_manager.elements.values():
                        for k, c in self.data_manager.elements.items():
                            if c == dicts.__dict__["mRID"]:
                                btn1 = QtWidgets.QToolButton()
                                btn1.setPopupMode(Qt.QToolButton.MenuButtonPopup)
                                btn1.addAction(QAction(k, self))
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
                    btn.setText("show details")
                btn.clicked.connect(self.handleButtonClicked)
                property_detail = QTableWidgetItem(str(detail))
                property_detail.setFlags(property_detail.flags() ^ QtCore.Qt.ItemIsEditable)
                self.elemProperties.insertRow(self.elemProperties.rowCount())
                self.elemProperties.setItem(row, 0, property_name)
                self.elemProperties.setCellWidget(row, 1, btn)
            else:
                property_name = QTableWidgetItem(key)
                property_name.setFlags(property_name.flags() ^ QtCore.Qt.ItemIsEditable)
                btn = QtWidgets.QPushButton()
                btn.setText("show data")
                btn.clicked.connect(self.handleButtonClicked)
                self.elemProperties.insertRow(self.elemProperties.rowCount())
                self.elemProperties.setItem(row, 0, property_name)
                self.elemProperties.setCellWidget(row, 1, btn)


            row += 1
        self.modified = False

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

            elif not isinstance(widget, QtWidgets.QPushButton) and not isinstance(widget, QtWidgets.QToolButton):
                self.data_manager.data['topology'][mRID].__dict__[
                    self.elemProperties.item(item, 0).text()] = self.elemProperties.item(item, 1).text()

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
        messages("Data successfully exported", "info")

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

    def iterItems(self, root):
        if root is not None:
            stack = [root]
            while stack:
                parent = stack.pop(0)
                for row in range(parent.rowCount()):
                    for column in range(parent.columnCount()):
                        child = parent.child(row, column)
                        yield child
                        if child.hasChildren():
                            stack.append(child)

    def handleButtonClicked(self):
        # button = QtGui.qApp.focusWidget()
        button = self.sender()
        index = self.elemProperties.indexAt(button.pos())
        if index.isValid():
            if self.elemProperties.cellWidget(index.row(), index.column()).text() in self.data_manager.elements.keys():
                itemtext = self.elemProperties.cellWidget(index.row(), index.column()).text()
                count = self.treeView.model().rowCount()
                root = self.treeView.model().invisibleRootItem()
                # for row in range(root.rowCount()):
                #     row_item = root.child(row, 0)
                #    if row_item.hasChildren():
                #       for childIndex in range(row_item.rowCount()):
                #            
                #           print(row_item.child(childIndex, 0).data())
                root = self.treeView.model().invisibleRootItem()
                for item in self.iterItems(root):
                    if itemtext == item.text():
                        self.treeView.selectionModel().setCurrentIndex(item.index(),
                                                                       Qt.QItemSelectionModel.ClearAndSelect)
                        self.clicked(item)
                        break
                # for i in range(count):
                # for k in range(self.treeView.model().index(i,0).item().childCount()):
                #    print(self.treeView.model().index(i,0).model().index(k,0).data())

                # print(count)
                # it = QTreeWidgetItemIterator(self.treeView)
                # root = self.treeView.currentIndex().parent().invisibleRootItem()

                # child_count = root.childCount()
                # for i in range(child_count):
                #    item = root.child(i)
                #    print(item.data())
                # items = self.treeView.findItems(itemtext, QtCore.Qt.MatchExactly)
                # self.elemView.setCurrentRow(self.elemView.row(items[0]))
                # self.clicked()
            elif self.elemProperties.cellWidget(index.row(), index.column()).text() == "show details":
                mRID = self.data_manager.elements[self.elemView.currentItem().text()]
                self.show_list_data(
                    self.data_manager.data['topology'][mRID].__dict__[
                        self.elemProperties.item(index.row(), 0).text()].__dict__)

    def show_list_data(self, data):

        table = ListData(data)
        # table.data = data
        # print(data)
        # table.displayView()

        table.exec()

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
            messages("No Matches Found", "Error")


class ListData(QDialog):
    tabledata = {}
    data = None

    def __init__(self, data):
        self.data = data
        self.data_managertwo = DataManager.ManageElements()
        super(ListData, self).__init__()
        if isinstance(data, list):
            loadUi("ListData.ui", self)
            self.displayView()
            self.elemView.itemClicked.connect(self.clicked)
        else:
            loadUi("listProp.ui", self)
            self.clicked()
        # self.data_managertwo.data=self.data

    def expand_dict(self):
        if isinstance(self.data, list):
            for dicts in self.data:
                # print("testing")
                # print(dicts.__dict__)
                self.data_managertwo.data.append(dicts.__dict__)
        else:
            print(self.data.__dict__)
            self.data_managertwo.data.append(self.data.__dict__)

    def displayView(self):
        self.expand_dict()
        self.elemView.addItems(self.data_managertwo.import_eq_data())

    def clicked(self):

        # mRID = "_48746FEF975E4732921B39AA07924D08"
        row = 0
        self.elemProperties.setRowCount(0)
        for key, val in self.data.items():
            if self.data[key] is None:

                property_name = QTableWidgetItem(key)
                property_name.setFlags(property_name.flags() ^ QtCore.Qt.ItemIsEditable)
                property_detail = QTableWidgetItem("None")
                property_detail.setFlags(property_name.flags() ^ QtCore.Qt.ItemIsEditable)
                self.elemProperties.insertRow(self.elemProperties.rowCount())
                self.elemProperties.setItem(row, 0, property_name)
                self.elemProperties.setItem(row, 1, property_detail)
            elif isinstance(self.data[key], (str, int, float, bool)):
                self.elemProperties.insertRow(self.elemProperties.rowCount())
                property_name = QTableWidgetItem(key)
                property_name.setFlags(property_name.flags() ^ QtCore.Qt.ItemIsEditable)

                detail = self.data[key]
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
                        [self.data[key], 'cell11', 'cell12', 'cell13',
                         'cell15', ])
                    self.elemProperties.setCellWidget(row, 1, c)
                else:
                    self.elemProperties.setItem(row, 1, property_detail)
            elif isinstance(self.data[key], list):
                property_name = QTableWidgetItem(key)
                property_name.setFlags(property_name.flags() ^ QtCore.Qt.ItemIsEditable)
                detail = self.data[key][0].__dict__["mRID"]
                btn1 = QtWidgets.QPushButton()
                btn1.setText("list")
                # btn1.clicked.connect(self.handleButtonClicked)
                self.elemProperties.insertRow(self.elemProperties.rowCount())
                self.elemProperties.setItem(row, 0, property_name)
                self.elemProperties.setCellWidget(row, 1, btn1)
                # self.elemProperties.setItem(row, 1, property_name)
            elif "mRID" in self.data[key].__dict__:
                property_name = QTableWidgetItem(key)
                property_name.setFlags(property_name.flags() ^ QtCore.Qt.ItemIsEditable)
                detail = self.data[key].__dict__["mRID"]
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
