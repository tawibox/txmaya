import os

import maya.cmds as mc
import maya.OpenMaya as om
import maya.OpenMayaUI as omui

from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

__author__ = "Xiaowei Oscar Tan"
__version__ = '2.0.0'

# Load plug-ins
list_plugins = ['AbcExport.so',
                'AbcImport.so',
                'objExport.so',
                'fbxmaya.so']
for i in list_plugins:
    if not mc.pluginInfo(i, q=True, loaded=True):
        mc.loadPlugin(i)


def maya_main_window():
    """
    Return the maya main window widget as a Python object
    """
    maya_main_ptr = omui.MQtUtil.mainWindow()
    if maya_main_ptr is not None:
        return wrapInstance(long(maya_main_ptr), QtWidgets.QWidget)


class FileBuffer(QtWidgets.QDialog):

    dialog_instance = None

    @classmethod
    def run(cls):
        if not cls.dialog_instance:
            cls.dialog_instance = FileBuffer()
        if cls.dialog_instance.isHidden():
            cls.dialog_instance.show()
        else:
            cls.dialog_instance.raise_()
            cls.dialog_instance.activateWindow()

    def __init__(self, parent=maya_main_window()):
        super(FileBuffer, self).__init__(parent)
        # set window title
        self.setWindowTitle('tx File Buffer')
        # init win size
        self.setMinimumWidth(350)
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
        self.line_edit = QtWidgets.QLineEdit()

        self.label_dir = QtWidgets.QLabel("Buffer Directory: ")
        self.label_buffer_size = QtWidgets.QLabel("Buffer Files Size: ")
        self.label_anim_keep = QtWidgets.QLabel("Preserve Anim:")
        self.label_anim_no = QtWidgets.QLabel("Delete Anim:")

        self.text_buffer = QtWidgets.QLabel("--")
        self.text_buffer.setTextFormat(QtCore.Qt.RichText)
        self.text_output = QtWidgets.QLabel("")
        self.text_output.setTextFormat(QtCore.Qt.RichText)

        self.radio_mb = QtWidgets.QRadioButton("mb")
        self.radio_mb.setChecked(True)
        self.radio_ma = QtWidgets.QRadioButton("ma")
        self.radio_abc = QtWidgets.QRadioButton("abc")
        self.radio_fbx = QtWidgets.QRadioButton("fbx")
        self.radio_obj = QtWidgets.QRadioButton("obj")

        self.radio_grp = QtWidgets.QButtonGroup()
        self.radio_grp.addButton(self.radio_mb)
        self.radio_grp.addButton(self.radio_ma)
        self.radio_grp.addButton(self.radio_abc)
        self.radio_grp.addButton(self.radio_fbx)
        self.radio_grp.addButton(self.radio_obj)
        self.radio_grp.setId(self.radio_mb, 0)
        self.radio_grp.setId(self.radio_ma, 1)
        self.radio_grp.setId(self.radio_abc, 2)
        self.radio_grp.setId(self.radio_fbx, 3)
        self.radio_grp.setId(self.radio_obj, 4)

        self.btn_file_browser = QtWidgets.QPushButton()
        self.btn_file_browser.setIcon(QtGui.QIcon(":fileOpen.png"))
        self.btn_check = QtWidgets.QPushButton("Update Buffer Size")
        self.btn_clear = QtWidgets.QPushButton("Clear Buffer on Disk")
        self.btn_export = QtWidgets.QPushButton("Export Selection to Buffer")
        self.btn_import = QtWidgets.QPushButton("Import Buffer")

    def create_layouts(self):
        layout_line_edit = QtWidgets.QHBoxLayout()
        layout_line_edit.addWidget(self.line_edit)
        layout_line_edit.addWidget(self.btn_file_browser)

        layout_buffer_check = QtWidgets.QHBoxLayout()
        layout_buffer_check.addWidget(self.text_buffer)
        layout_buffer_check.addStretch()
        layout_buffer_check.addWidget(self.btn_check)

        layout_buffer_clear = QtWidgets.QHBoxLayout()
        layout_buffer_clear.addWidget(self.text_output)
        layout_buffer_clear.addStretch()
        layout_buffer_clear.addWidget(self.btn_clear)

        layout_radio_anim_keep = QtWidgets.QGridLayout()
        layout_radio_anim_keep.addWidget(self.radio_mb, 0, 0, 1)
        layout_radio_anim_keep.addWidget(self.radio_ma, 0, 1, 1)

        layout_radio_anim_no = QtWidgets.QGridLayout()
        layout_radio_anim_no.addWidget(self.radio_abc, 0, 0, 1)
        layout_radio_anim_no.addWidget(self.radio_fbx, 0, 1, 1)
        layout_radio_anim_no.addWidget(self.radio_obj, 0, 2, 1)

        layout_btn_io = QtWidgets.QHBoxLayout()
        layout_btn_io.addStretch()
        layout_btn_io.addWidget(self.btn_export)
        layout_btn_io.addWidget(self.btn_import)

        layout_form = QtWidgets.QFormLayout()
        layout_form.addRow(self.label_dir, layout_line_edit)
        layout_form.addRow(self.label_buffer_size, layout_buffer_check)
        layout_form.addRow("", layout_buffer_clear)
        layout_form.addRow(self.label_anim_keep, layout_radio_anim_keep)
        layout_form.addRow(self.label_anim_no, layout_radio_anim_no)

        layout_root = QtWidgets.QVBoxLayout(self)
        layout_root.addLayout(layout_form)
        layout_root.addLayout(layout_btn_io)

    # signals and slots
    def create_connections(self):
        self.btn_file_browser.clicked.connect(self.show_file_browser)

        self.btn_check.clicked.connect(self.display_buffer_size)
        self.line_edit.returnPressed.connect(self.display_buffer_size)
        self.btn_clear.clicked.connect(self.delete_buffer)

        self.btn_export.clicked.connect(self.apply_export)
        self.btn_import.clicked.connect(self.apply_import)

    # methods
    # utils
    def get_file_size(self, path_file):
        file_size = os.stat(path_file).st_size
        return file_size  # bytes

    def byte_convert(self, size):
        # 2**10 = 1024
        power = 2.0 ** 10
        n = 0
        power_labels = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
        while size > power:
            size /= power
            n += 1
        return round(size, 1), power_labels[n] + 'B'  # 'B'='bytes'

    def file_export_sel(self,
                        file_dir,
                        file_name,
                        file_ext,
                        type,
                        options):
        list_sel = mc.ls(sl=True) or []
        path_full = os.path.join(file_dir, '.'.join((file_name, file_ext)))
        if len(list_sel) == 0:
            return
        else:
            mc.file(path_full,
                    exportSelected=True,
                    force=True,
                    preserveReferences=True,
                    type=type,
                    options=options)
            return path_full

    def file_export_sel_abc(self,
                            file_dir,
                            file_name,
                            file_ext,
                            frame_start,
                            frame_end):
        list_sel = mc.ls(sl=True) or []
        # cmd_frame_range
        cmd_frame_range = " ".join(("-frameRange",
                                    str(frame_start),
                                    str(frame_end),
                                    " "))
        # cmd_options
        cmd_options = " ".join(("-uvWrite",
                                "-worldSpace",
                                "-writeVisibility",
                                "-dataFormat ogawa",
                                "-writeUVSets",
                                " "))
        # cmd_root: items to export
        cmd_root = str()
        for i in list_sel:
            root_each = " ".join(("-root", i, " "))
            cmd_root += root_each
        # cmd_path
        path_full = os.path.join(file_dir, '.'.join((file_name, file_ext)))
        cmd_path = " ".join(("-file", path_full))
        # cmd
        cmd = cmd_frame_range + cmd_options + cmd_root + cmd_path
        # do export
        if len(list_sel) == 0:
            return None
        else:
            mc.AbcExport(j=cmd)
            return path_full

    def file_import(self,
                    file_dir,
                    file_name,
                    file_ext,
                    type,
                    options):
        path_full = os.path.join(file_dir, '.'.join((file_name, file_ext)))
        exists = mc.file(path_full, query=True, exists=True)
        if exists is True:
            mc.file(path_full,
                    type=type,
                    options=options,
                    i=True,
                    ignoreVersion=True,
                    preserveReferences=True,
                    mergeNamespacesOnClash=False,
                    importFrameRate=True,
                    importTimeRange='override'
                    )
            return path_full
        else:
            return

    # special
    def show_file_browser(self):
        path_dir = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                         "Select Directory")
        if path_dir:
            self.line_edit.setText(path_dir)

    def get_buffer_size(self):
        path_dir = self.line_edit.text()
        file_info = QtCore.QFileInfo(path_dir)
        if file_info.exists():
            buffer_size = 0
            for root, dirs, files in os.walk(path_dir):
                for name in files:
                    if "fileBufferTemp" in name:
                        path_full = os.path.join(root, name)
                        buffer_size += self.get_file_size(path_full)
            return buffer_size
        else:
            return

    def display_buffer_size(self):
        path_dir = self.line_edit.text()
        info_dir = QtCore.QFileInfo(path_dir)
        # when line edit is empty
        if not path_dir:
            self.text_buffer.setText('<b><i>Directory not exists!</i></b>')
        # when path_dir doesn't exist
        elif not info_dir.exists():
            self.text_buffer.setText('<b><i>Directory not exists!</i></b>')
        else:
            size = self.get_buffer_size()
            if size != 0:
                self.text_buffer.setText("<b>"
                                         + str(self.byte_convert(size)[0])
                                         + " "
                                         + self.byte_convert(size)[1]
                                         + "</b>")
            else:
                self.text_buffer.setText("<b>0 KB</b>")

    def delete_buffer(self):
        path_dir = self.line_edit.text()
        for root, dirs, files in os.walk(path_dir):
            for name in files:
                if "fileBufferTemp" in name:
                    path_full = os.path.join(root, name)
                    os.remove(path_full)
        self.display_buffer_size()

    def apply_export(self):
        path_dir = self.line_edit.text()
        info_dir = QtCore.QFileInfo(path_dir)
        file_name = "fileBufferTemp"
        radio_id = self.radio_grp.checkedId()
        if not path_dir:
            self.text_buffer.setText("<b><i>Directory not exists!</i></b>")
            return
        elif not info_dir.exists():
            self.text_buffer.setText("<b><i>Directory not exists!</i></b>")
            return
        else:
            if radio_id == 0:
                out_path = self.file_export_sel(file_dir=path_dir,
                                                file_name=file_name,
                                                file_ext="mb",
                                                type="mayaBinary",
                                                options="v=0;")
            if radio_id == 1:
                out_path = self.file_export_sel(file_dir=path_dir,
                                                file_name=file_name,
                                                file_ext="ma",
                                                type="mayaAscii",
                                                options="v=0;")
            if radio_id == 2:
                frame_current = mc.currentTime(query=True)
                out_path = self.file_export_sel_abc(file_dir=path_dir,
                                                    file_name=file_name,
                                                    file_ext="abc",
                                                    frame_start=frame_current,
                                                    frame_end=frame_current)
            if radio_id == 3:
                out_path = self.file_export_sel(file_dir=path_dir,
                                                file_name=file_name,
                                                file_ext="fbx",
                                                type="FBX export",
                                                options="v=0;p=17;f=0")
            if radio_id == 4:
                out_path = self.file_export_sel(file_dir=path_dir,
                                                file_name=file_name,
                                                file_ext="obj",
                                                type="OBJexport",
                                                options="groups=0;"
                                                        "ptgroups=1;"
                                                        "materials=0;"
                                                        "smoothing=1;"
                                                        "normals=1;")
        self.display_buffer_size()
        if out_path is None:
            om.MGlobal.displayWarning("Nothing Selected!")
        else:
            out_size_byte = self.get_file_size(out_path)
            out_size = self.byte_convert(out_size_byte)
            info = "{2}  {0}{1}.".format(str(out_size[0]),
                                         out_size[1],
                                         "Buffer exported successfully:")
            om.MGlobal.displayInfo(info)

    def apply_import(self):
        path_dir = self.line_edit.text()
        file_name = "fileBufferTemp"
        radio_id = self.radio_grp.checkedId()
        if radio_id == 0:
            in_file = self.file_import(file_dir=path_dir,
                                       file_name=file_name,
                                       file_ext="mb",
                                       type="mayaBinary",
                                       options="v=0;p=17;f=0;")
        if radio_id == 1:
            in_file = self.file_import(file_dir=path_dir,
                                       file_name=file_name,
                                       file_ext="ma",
                                       type="mayaAscii",
                                       options="v=0;p=17;f=0;")
        if radio_id == 2:
            in_file = self.file_import(file_dir=path_dir,
                                       file_name=file_name,
                                       file_ext="abc",
                                       type="Alembic",
                                       options=None)
        if radio_id == 3:
            in_file = self.file_import(file_dir=path_dir,
                                       file_name=file_name,
                                       file_ext="fbx",
                                       type="FBX",
                                       options="fbx")
        if radio_id == 4:
            in_file = self.file_import(file_dir=path_dir,
                                       file_name=file_name,
                                       file_ext="obj",
                                       type="OBJ",
                                       options="mo=1;")
        if in_file is None:
            om.MGlobal.displayWarning("Buffer file doesn't exist!")
        else:
            om.MGlobal.displayInfo("Buffer file imported successfully.")

    def showEvent(self, e):
        super(FileBuffer, self).showEvent(e)

        if self.geometry:
            self.restoreGeometry(self.geometry)

    def closeEvent(self, e):
        if isinstance(self, FileBuffer):
            super(FileBuffer, self).closeEvent(e)

            self.geometry = self.saveGeometry()

if __name__ == '__main__':
    # delete UI if there's one already open
    try:
        FileBuffer_test.close()
        FileBuffer_test.deleteLater()
    except:
        pass

    FileBuffer_test = FileBuffer()
    FileBuffer_test.show()

