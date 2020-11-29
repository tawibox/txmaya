import random

import maya.cmds as mc
import maya.OpenMaya as om
import maya.OpenMayaUI as omui

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

__author__ = "Xiaowei Oscar Tan"
__version__ = '3.2.0'


def maya_main_window():
    """
    Return the maya main window widget as a Python object
    """
    maya_main_ptr = omui.MQtUtil.mainWindow()
    if maya_main_ptr is not None:
        return wrapInstance(long(maya_main_ptr), QtWidgets.QWidget)


class Mirrorer(QtWidgets.QDialog):

    dialog_instance = None

    @classmethod
    def run(cls):
        if not cls.dialog_instance:
            cls.dialog_instance = Mirrorer()
        if cls.dialog_instance.isHidden():
            cls.dialog_instance.show()
        else:
            cls.dialog_instance.raise_()
            cls.dialog_instance.activateWindow()

    def __init__(self, parent=maya_main_window()):
        super(Mirrorer, self).__init__(parent)
        # set window title
        self.setWindowTitle('tx Mirrorer')
        # init win size
        self.setMinimumWidth(250)
        self.setMaximumHeight(108)
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
        self.label_space = QtWidgets.QLabel("Space: ")
        self.text_world = QtWidgets.QLabel("<b>World</b>")

        self.button_x = QtWidgets.QPushButton("Along X")
        self.button_x.setStyleSheet("background-color:rgb(160,0,0)")
        self.button_y = QtWidgets.QPushButton("Along Y")
        self.button_y.setStyleSheet("background-color:rgb(0,160,0)")
        self.button_z = QtWidgets.QPushButton("Along Z")
        self.button_z.setStyleSheet("background-color:rgb(0,0,160)")

    def create_layouts(self):
        layout_space = QtWidgets.QHBoxLayout()
        layout_space.addWidget(self.label_space)
        layout_space.addWidget(self.text_world)
        layout_space.addStretch()

        layout_buttons = QtWidgets.QVBoxLayout()
        layout_buttons.addWidget(self.button_x)
        layout_buttons.addWidget(self.button_y)
        layout_buttons.addWidget(self.button_z)

        layout_root = QtWidgets.QVBoxLayout(self)
        layout_root.addLayout(layout_space)
        layout_root.addLayout(layout_buttons)

    def create_connections(self):
        self.button_x.clicked.connect(lambda: self.mirrorer(self.button_x))
        self.button_y.clicked.connect(lambda: self.mirrorer(self.button_y))
        self.button_z.clicked.connect(lambda: self.mirrorer(self.button_z))

    # method
    def mirrorer(self, button):
        if button.text() == "Along X":
            mirror_channel = '.scaleX'
        if button.text() == "Along Y":
            mirror_channel = '.scaleY'
        if button.text() == "Along Z":
            mirror_channel = '.scaleZ'

        current_sel = mc.ls(sl=True)
        for i in current_sel:
            # get info
            name = i.split("|")[-1]
            hierarchy = mc.listRelatives(i, fullPath=True) or [""]
            hierarchy_list = hierarchy[0].split("|")
            hierarchy_root = "|".join(hierarchy_list[:-2]) or "|"
            # do duplicate
            i_mirror = mc.duplicate(i, name=name + "_MIRROR")
            i_grp_temp = mc.group(empty=True, n="txMirrorer_temp")
            mc.parent(i_mirror[0], "txMirrorer_temp")
            # do mirroring
            mc.xform(i_grp_temp,
                     worldSpace=True,
                     scalePivot=[0, 0, 0],
                     rotatePivot=[0, 0, 0])
            mc.setAttr(i_grp_temp + mirror_channel, -1)
            # put the mirrored back to original hierarchy
            if hierarchy_root == "|":
                mc.parent(i_mirror[0], world=True)
            else:
                mc.parent(i_mirror[0], hierarchy_root)
            mc.delete(i_grp_temp)
            # clean up scale attr, uv and normals
            # mc.makeIdentity(i_mirror[0],
            #                 apply=True,
            #                 preserveNormals=True,
            #                 translate=False,
            #                 rotate=False,
            #                 scale=True,
            #                 normal=False)
            # do UV flip
            list_mirrored_mesh = mc.listRelatives(i_mirror[0],
                                                  allDescendents=True,
                                                  type="mesh",
                                                  fullPath=True) or []
            if list_mirrored_mesh:
                for j in list_mirrored_mesh:
                    mc.polyFlipUV(j)
            mc.select(i_mirror[0])

    def showEvent(self, e):
        super(Mirrorer, self).showEvent(e)
        if self.geometry:
            self.restoreGeometry(self.geometry)

    def closeEvent(self, e):
        if isinstance(self, Mirrorer):
            super(Mirrorer, self).closeEvent(e)

            self.geometry = self.saveGeometry()


if __name__ == '__main__':
    try:
        Mirrorer_test.close()
        Mirrorer_test.deleteLater()
    except:
        pass

    Mirrorer_test = Mirrorer()
    Mirrorer_test.show()
