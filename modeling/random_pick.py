import maya.cmds as mc
import random
import maya.OpenMaya as om
import maya.OpenMayaUI as omui
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance


__author__ = "Xiaowei Oscar Tan"


def maya_main_window():
    """
    Return the maya main window widget as a Python object
    """
    maya_main_ptr = omui.MQtUtil.mainWindow()
    if maya_main_ptr is not None:
        return wrapInstance(long(maya_main_ptr), QtWidgets.QWidget)


class RandomPick(QtWidgets.QDialog):

    LIST_SEL_BASE = []
    COUNT_PICKED = 0

    def __init__(self, parent=maya_main_window()):
        super(RandomPick, self).__init__(parent)
        # set window title
        self.setWindowTitle('tx Random Pick')
        # init win size
        self.setMinimumWidth(250)
        # self.setMinimumHeight(200)
        # win OS only. get rid of '?' button on GUI.
        self.setWindowFlags(self.windowFlags()
                            ^ QtCore.Qt.WindowContextHelpButtonHint)
        # widgets and layouts
        self.create_widgets()
        self.create_layouts()
        # connections
        self.create_connections()

    def create_widgets(self):
        # label
        self.label_base_count = QtWidgets.QLabel("Num of Selection Base: ")
        self.label_pick_count = QtWidgets.QLabel("Num of Picked: ")
        self.label_percentage = QtWidgets.QLabel("%")
        # text
        self.text_base_count = QtWidgets.QLabel("<p style='color:#ffbc1f';><b>--</b></p>")
        self.text_base_count.setTextFormat(QtCore.Qt.RichText)
        self.text_pick_count = QtWidgets.QLabel("<p style='color:#ffbc1f';><b>--</b></p>")
        self.text_pick_count.setTextFormat(QtCore.Qt.RichText)
        # radio
        self.radio_percentage = QtWidgets.QRadioButton("By Percentage: ")
        self.radio_percentage.setChecked(True)
        self.radio_count = QtWidgets.QRadioButton("By Count: ")
        # slider
        self.slider = QtWidgets.QSlider()
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(100)
        # line edit
        self.line_percentage = QtWidgets.QLineEdit()
        self.line_percentage.setMaximumWidth(60)
        self.line_percentage.setAlignment(QtCore.Qt.AlignRight)
        self.line_percentage.setText(str(self.slider.value()))
        self.line_percentage.setValidator(QtGui.QIntValidator())

        self.line_count = QtWidgets.QLineEdit("0")
        self.line_count.setMaximumWidth(60)
        self.line_count.setAlignment(QtCore.Qt.AlignRight)
        self.line_count.setValidator(QtGui.QIntValidator())
        self.line_count.setEnabled(False)
        # button
        self.btn_pick = QtWidgets.QPushButton("Random Pick")
        self.btn_refresh = QtWidgets.QPushButton("Refresh Selection Base")
        # spacing
        # self.space = QtWidgets.QSpacerItem(20, 40)

    def create_layouts(self):
        layout_percentage_content = QtWidgets.QHBoxLayout()
        layout_percentage_content.addSpacing(20)
        layout_percentage_content.addWidget(self.line_percentage)
        layout_percentage_content.addWidget(self.label_percentage)
        layout_percentage_content.addSpacing(8)
        layout_percentage_content.addWidget(self.slider)

        layout_count_content = QtWidgets.QHBoxLayout()
        layout_count_content.addSpacing(20)
        layout_count_content.addWidget(self.line_count)
        layout_count_content.addStretch()

        layout_percentage = QtWidgets.QVBoxLayout()
        layout_percentage.addWidget(self.radio_percentage)
        layout_percentage.addLayout(layout_percentage_content)

        layout_count = QtWidgets.QVBoxLayout()
        layout_count.addWidget(self.radio_count)
        layout_count.addLayout(layout_count_content)

        layout_print_content = QtWidgets.QGridLayout()
        layout_print_content.addWidget(self.label_base_count, 0, 0,
                                       QtCore.Qt.AlignRight)
        layout_print_content.addWidget(self.text_base_count, 0, 1,
                                       QtCore.Qt.AlignRight)
        layout_print_content.addWidget(self.label_pick_count, 1, 0,
                                       QtCore.Qt.AlignRight)
        layout_print_content.addWidget(self.text_pick_count, 1, 1,
                                       QtCore.Qt.AlignRight)

        layout_print = QtWidgets.QHBoxLayout()
        layout_print.addSpacing(60)
        layout_print.addLayout(layout_print_content)

        layout_button_refresh = QtWidgets.QHBoxLayout()
        layout_button_refresh.addStretch()
        layout_button_refresh.addWidget(self.btn_refresh)

        layout_button = QtWidgets.QVBoxLayout()
        layout_button.addStretch()
        layout_button.addLayout(layout_button_refresh)
        layout_button.addWidget(self.btn_pick)

        layout_root = QtWidgets.QVBoxLayout(self)
        layout_root.addLayout(layout_percentage)
        layout_root.addLayout(layout_count)
        layout_root.addLayout(layout_print)
        layout_root.addLayout(layout_button)

    def create_connections(self):
        # UI updates
        self.slider.valueChanged.connect(self.update_line_percentage)
        self.line_percentage.returnPressed.connect(self.update_slider)

        self.radio_percentage.clicked.connect(self.disable_count)
        self.radio_percentage.clicked.connect(self.display_count_picked)
        self.radio_count.clicked.connect(self.disable_percentage)
        self.radio_count.clicked.connect(self.display_count_picked)
        # display
        self.line_percentage.textChanged.connect(self.display_count_picked)
        self.line_count.textChanged.connect(self.display_count_picked)
        # other
        self.btn_refresh.clicked.connect(self.get_list_sel_base)
        self.btn_refresh.clicked.connect(self.display_count_sel_base)
        self.btn_refresh.clicked.connect(self.display_count_picked)
        self.btn_pick.clicked.connect(self.random_pick)

    # signals ans slots
    # UI updates
    def update_line_percentage(self):
        slider_value = self.slider.value()
        self.line_percentage.setText(str(slider_value))

    def update_slider(self):
        line_value = self.line_percentage.text()
        self.slider.setValue(int(line_value))

    def disable_percentage(self):
        self.line_percentage.setEnabled(False)
        self.slider.setEnabled(False)
        self.line_count.setEnabled(True)

    def disable_count(self):
        self.line_percentage.setEnabled(True)
        self.slider.setEnabled(True)
        self.line_count.setEnabled(False)

    # method
    def display_count_sel_base(self):
        self.text_base_count.setText("<p style='color:#ffbc1f';><b>"
                                     + str(len(self.LIST_SEL_BASE))
                                     + "</b></p>")

    def display_count_picked(self):
        self.get_count_picked()
        self.text_pick_count.setText("<p style='color:#ffbc1f';><b>"
                                     + str(self.COUNT_PICKED)
                                     + "</b></p>")

    def get_list_sel_base(self):
        self.LIST_SEL_BASE = mc.ls(sl=True, long=True) or []

    def get_count_picked(self):
        if self.radio_percentage.isChecked():
            percentage_picked = float(self.line_percentage.text())
            self.COUNT_PICKED = int(round((percentage_picked / 100)
                                          * len(self.LIST_SEL_BASE)))
        if self.radio_count.isChecked():
            self.COUNT_PICKED = int(self.line_count.text())

    def random_pick(self):
        self.get_count_picked()

        if self.COUNT_PICKED <= len(self.LIST_SEL_BASE):
            list_picked = random.sample(self.LIST_SEL_BASE,
                                        k=self.COUNT_PICKED)
            mc.select(list_picked)
        else:
            om.MGlobal.displayWarning("Invald pick count input!")


if __name__ == '__main__':
    # delete UI if there's one already open
    try:
        RandomPick_dialog.close()
        RandomPick_dialog.deleteLater()
    except:
        pass

    RandomPick_dialog = RandomPick()
    RandomPick_dialog.show()
    RandomPick_dialog.get_list_sel_base()
    RandomPick_dialog.get_count_picked()
    RandomPick_dialog.display_count_sel_base()
    RandomPick_dialog.display_count_picked()
