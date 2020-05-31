import math

import maya.cmds as mc
import pymel.core as pm
import maya.OpenMaya as om
import maya.OpenMayaUI as omui

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

__author__ = "Xiaowei Oscar Tan"
__version__ = '2.0.2'


def maya_main_window():
    """
    Return the maya main window widget as a Python object
    """
    maya_main_ptr = omui.MQtUtil.mainWindow()
    if maya_main_ptr is not None:
        return wrapInstance(long(maya_main_ptr), QtWidgets.QWidget)


class TexelDensityPatch(QtWidgets.QDialog):

    dialog_instance = None

    @classmethod
    def run(cls):
        if not cls.dialog_instance:
            cls.dialog_instance = TexelDensityPatch()
        if cls.dialog_instance.isHidden():
            cls.dialog_instance.show()
        else:
            cls.dialog_instance.raise_()
            cls.dialog_instance.activateWindow()

    def __init__(self, parent=maya_main_window()):
        super(TexelDensityPatch, self).__init__(parent)
        # set window title
        self.setWindowTitle('tx Texel Density Patch')
        # init win size
        self.setMinimumWidth(250)
        # self.setMinimumHeight(200)
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
        self.button_get = QtWidgets.QPushButton("Get TD")
        self.button_set = QtWidgets.QPushButton("Set TD Uniformly")

        self.label_td = QtWidgets.QLabel("Texel Density: ")
        self.label_map_size = QtWidgets.QLabel("Map Size: ")

        self.lineedit_td = QtWidgets.QLineEdit("0.0000")
        self.lineedit_td.setValidator(QtGui.QDoubleValidator())
        self.lineedit_map_size = QtWidgets.QLineEdit("512")
        self.lineedit_map_size.setFixedWidth(45)
        self.lineedit_map_size.setValidator(QtGui.QIntValidator())

    def create_layouts(self):
        layout_button = QtWidgets.QHBoxLayout()
        layout_button.addWidget(self.button_get)
        layout_button.addWidget(self.button_set)

        layout_map_size = QtWidgets.QHBoxLayout()
        layout_map_size.addStretch()
        layout_map_size.addWidget(self.label_map_size)
        layout_map_size.addWidget(self.lineedit_map_size)

        layout_td = QtWidgets.QHBoxLayout()
        layout_td.addWidget(self.label_td)
        layout_td.addWidget(self.lineedit_td)

        layout_root = QtWidgets.QVBoxLayout(self)
        layout_root.addLayout(layout_map_size)
        layout_root.addLayout(layout_td)

        layout_root.addSpacing(15)
        layout_root.addLayout(layout_button)

    def create_connections(self):
        self.button_get.clicked.connect(self.get_td)
        self.button_set.clicked.connect(self.set_td)

    # signals ans slots
    def calculate_td_sel_components(self):

        """ get selected components' TD """

        map_size = float(self.lineedit_map_size.text())

        # convert selected components to faces
        current_sel = pm.ls(sl=True)
        if len(current_sel) > 0:
            pm.select(d=True)
            for i in current_sel:
                pm.select(pm.polyListComponentConversion(i, toFace=True),
                          add=True)
            # get faces class
            current_sel_faces = pm.ls(sl=True)
            # calculate TD
            num_faces = 0
            td_faces_total = 0
            for faces in current_sel_faces:
                num_faces += len(faces)
                for face in faces:
                    face_area_uv = face.getUVArea()
                    face_area_3d = face.getArea(space="world")
                    td_face = (math.sqrt(face_area_uv)
                               / math.sqrt(face_area_3d)) * map_size
                    td_faces_total += td_face
            td_faces = td_faces_total / num_faces
            # convert selected components to uvs
            current_sel_new = pm.ls(sl=True)
            pm.select(d=True)
            for j in current_sel_new:
                pm.select(pm.polyListComponentConversion(j, toUV=True),
                          add=True)
            return round(td_faces, 4)
        else:
            om.MGlobal.displayWarning("Select at least 1 geo!")
            return 0.0000

    def uv_scale_sel_components(self, scale_factor):

        """ scale selected components' uv """

        # convert selected components to uvs
        current_sel = pm.ls(sl=True)
        pm.select(d=True)
        for i in current_sel:
            pm.select(pm.polyListComponentConversion(i, toUV=True),
                      add=True)
        # get uvs class
        current_sel_uvs = pm.ls(sl=True)
        # get selected uvs' center
        num_uvs = 0
        uvs_center_u = 0
        uvs_center_v = 0
        for uvs in current_sel_uvs:
            num_uvs += len(uvs)
            for uv in uvs:
                uvs_center_u += pm.polyEditUV(uv, query=True)[0]
                uvs_center_v += pm.polyEditUV(uv, query=True)[1]
        uvs_center_u = uvs_center_u / num_uvs
        uvs_center_v = uvs_center_v / num_uvs
        # do scale
        pm.polyEditUV(pivotU=uvs_center_u,
                      pivotV=uvs_center_v,
                      scaleU=scale_factor,
                      scaleV=scale_factor)

    def get_td(self):
        td = str(self.calculate_td_sel_components())
        self.lineedit_td.setText(td)

    def set_td(self):
        current_sel = pm.ls(sl=True)
        if len(current_sel) > 0:
            td_target = float(self.lineedit_td.text())
            if td_target == 0:
                message = "'Texel Density' value can't be zero!"
                om.MGlobal.displayWarning(message)
            else:
                td_select = self.calculate_td_sel_components()
                scale_factor = td_target / td_select
                self.uv_scale_sel_components(scale_factor)
        else:
            om.MGlobal.displayWarning("Select at least 1 geo!")

    def showEvent(self, e):
        super(TexelDensityPatch, self).showEvent(e)
        if self.geometry:
            self.restoreGeometry(self.geometry)

    def closeEvent(self, e):
        if isinstance(self, TexelDensityPatch):
            super(TexelDensityPatch, self).closeEvent(e)
            self.geometry = self.saveGeometry()


if __name__ == '__main__':
    try:
        TexelDensityPatch_test.close()
        TexelDensityPatch_test.deleteLater()
    except:
        pass

    TexelDensityPatch_test = TexelDensityPatch()
    TexelDensityPatch_test.show()
