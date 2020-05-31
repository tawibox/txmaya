'''
Summary:
transferring all uvsets between 2 groups of models.
Geos need to be named properly before running this script.

Geo naming request:
source and target geos need to have same prefix, only difference should be suffix.
'''

import maya.cmds as mc
import maya.OpenMaya as om
import maya.OpenMayaUI as omui

from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance


__author__ = "Xiaowei Oscar Tan"
__version__ = '1.0.1'


def maya_main_window():
    """
    Return the maya main window widget as a Python object
    """
    maya_main_ptr = omui.MQtUtil.mainWindow()
    if maya_main_ptr is not None:
        return wrapInstance(long(maya_main_ptr), QtWidgets.QWidget)


class UvBatchTransfer(QtWidgets.QDialog):

    dialog_instance = None

    @classmethod
    def run(cls):
        if not cls.dialog_instance:
            cls.dialog_instance = UvBatchTransfer()
        if cls.dialog_instance.isHidden():
            cls.dialog_instance.show()
        else:
            cls.dialog_instance.raise_()
            cls.dialog_instance.activateWindow()

    def __init__(self, parent=maya_main_window()):
        super(UvBatchTransfer, self).__init__(parent)
        # set window title
        self.setWindowTitle('tx UV Batch Transfer')
        # init win size
        self.setMinimumWidth(300)
        # self.setMinimumHeight(100)
        # win OS only. get rid of '?' button on GUI.
        self.setWindowFlags(self.windowFlags()
                            ^ QtCore.Qt.WindowContextHelpButtonHint)
        # ui position
        self.geometry = None
        # widgets and layouts
        self.create_widgets()
        self.create_layouts()
        # connections
        self.create_connections()

    def create_widgets(self):
        self.text_brief_1 = QtWidgets.QLabel("Transferring based on topology")
        self.text_brief_2 = QtWidgets.QLabel("Source and target geos' names must be same except for suffixes")
        self.text_brief_2.setTextFormat(QtCore.Qt.RichText)
        self.text_brief_3 = QtWidgets.QLabel("<b>How to use:</b>")
        self.text_brief_4 = QtWidgets.QLabel("1. Rename both source and target geos properly")
        self.text_brief_5 = QtWidgets.QLabel("2. Specify both suffixes below")
        self.text_brief_6 = QtWidgets.QLabel("3. Select all source and target geos")
        self.text_brief_7 = QtWidgets.QLabel("4. Click button")

        self.label_source = QtWidgets.QLabel("Source geos suffix: ")
        self.label_target = QtWidgets.QLabel("Target geos suffix: ")

        self.line_edit_source = QtWidgets.QLineEdit()
        self.line_edit_target = QtWidgets.QLineEdit()

        self.button = QtWidgets.QPushButton("Batch Transfer UVs")

    def create_layouts(self):
        layout_brief = QtWidgets.QVBoxLayout()
        layout_brief.addWidget(self.text_brief_1)
        layout_brief.addWidget(self.text_brief_2)
        layout_brief.addSpacing(7)
        layout_brief.addWidget(self.text_brief_3)
        layout_brief.addWidget(self.text_brief_4)
        layout_brief.addWidget(self.text_brief_5)
        layout_brief.addWidget(self.text_brief_6)
        layout_brief.addWidget(self.text_brief_7)

        layout_line = QtWidgets.QFormLayout()
        layout_line.addRow(self.label_source, self.line_edit_source)
        layout_line.addRow(self.label_target, self.line_edit_target)

        layout_button = QtWidgets.QHBoxLayout()
        layout_button.addStretch()
        layout_button.addWidget(self.button)
        layout_button.addStretch()

        layout_root = QtWidgets.QVBoxLayout(self)
        layout_root.addLayout(layout_brief)
        layout_root.addSpacing(10)
        layout_root.addLayout(layout_line)
        layout_root.addLayout(layout_button)

    def create_connections(self):
        self.button.clicked.connect(self.uv_transfer)

    # methods
    def uv_transfer(self):

        suffix_source = self.line_edit_source.text()
        suffix_target = self.line_edit_target.text()

        list_sel = mc.ls(sl=True,
                         long=True,
                         dag=True) or []
        list_mesh = mc.listRelatives(list_sel,
                                     shapes=True,
                                     type="mesh",
                                     fullPath=True) or []
        list_mesh_source = []
        list_mesh_target = []
        dict_mesh = {}  # {source: target}

        if len(list_sel) == 0:
            om.MGlobal.displayWarning("Please select geos!")
        else:
            # get "list_mesh_source"
            for i in list_mesh:
                # i_shape = i.split("|")[-1]
                i_transform = i.split("|")[-2]
                if suffix_source in i_transform:
                    list_mesh_source.append(i)
            # get "list_mesh_target"
            for i in list_mesh:
                # i_shape = i.split("|")[-1]
                i_transform = i.split("|")[-2]
                if suffix_target in i_transform:
                    list_mesh_target.append(i)
            # check if two groups of geo have some piece counts
            if len(list_mesh_source) != len(list_mesh_target):
                count_source = "sources " + str(len(list_mesh_source))
                count_target = "targets " + str(len(list_mesh_target))
                warning = "Two groups of geos have different numbers of pieces:"
                om.MGlobal.displayWarning(' '.join((warning, count_source, count_target)))
            else:
                # get "dict_mesh"
                for i in list_mesh_source:
                    # i_shape = i.split("|")[-1]
                    i_transform = i.split("|")[-2]
                    prefix = i_transform[:-(len(suffix_source)+1)]
                    # print prefix
                    for j in list_mesh_target:
                        if prefix in j:
                            dict_mesh[i] = j
                for source, target in dict_mesh.items():
                    # do uv transfer
                    mc.polyTransfer(target,
                                    vertices=0,
                                    vertexColor=0,
                                    uvSets=1,
                                    alternateObject=source)
    def showEvent(self, e):
        super(UvBatchTransfer, self).showEvent(e)

        if self.geometry:
            self.restoreGeometry(self.geometry)

    def closeEvent(self, e):
        if isinstance(self, UvBatchTransfer):
            super(UvBatchTransfer, self).closeEvent(e)

            self.geometry = self.saveGeometry()

if __name__ == '__main__':
    # delete UI if there's one already open
    try:
        UvBatchTransfer_test.close()
        UvBatchTransfer_test.deleteLater()
    except:
        pass

    UvBatchTransfer_test = UvBatchTransfer()
    UvBatchTransfer_test.show()

