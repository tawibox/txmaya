# TD Extra v1.0

# Calculate "Texel Density"
# set "mtoa_constant_uv_offset" to the same value of mesh's texel density

import maya.OpenMaya as om
import maya.cmds as cmds
import pymel.core as pm
import math
import os
import shutil
import sys
import stat
import time
from subprocess import Popen, PIPE
from functools import partial


def component_to_object(*args):
    current_sel = cmds.ls(sl=True)
    list_mesh = []
    for i in current_sel:
        i_mesh = i.split('.')[0]
        list_mesh.append(i_mesh)
    cmds.selectMode(object=True)
    cmds.select(d=True)
    for i in list_mesh:
        cmds.select(i, add=True)


def get_texel_density(map_size, *args):
    component_to_object()
    current_sel = pm.ls(sl=True)
    if len(current_sel) >0:
        all_mesh_td = 0
        for each_mesh in current_sel:
            #print each_mesh
            each_mesh_face_count = each_mesh.numFaces()
            each_mesh_td_total = 0
            for each_face in each_mesh.f:
                #print each_face
                area3D = each_face.getArea(space="world")
                area2D = each_face.getUVArea()
                sizeMap = map_size
                each_face_td = (math.sqrt(area2D) / math.sqrt(area3D)) * sizeMap
                #print each_face_td
                each_mesh_td_total += each_face_td
            each_mesh_td = each_mesh_td_total / each_mesh_face_count
            all_mesh_td += each_mesh_td
        td = all_mesh_td / len(current_sel)
        return td
    else:
        om.MGlobal.displayWarning("Select at least 1 geo!")
    return 0


def uv_scaler(scale_factor, *args):
    current_sel = cmds.ls(sl=True)
    # convert selected object to UV
    cmds.select(cmds.polyListComponentConversion(tuv=True), r=True)
    current_sel_uv = cmds.ls(sl=True, fl=True)
    # calculate center
    uv_center_u = 0
    uv_center_v = 0
    for i in current_sel_uv:
        #print cmds.polyEditUV(i, query=True)
        uv_center_u += cmds.polyEditUV(i, query=True)[0]
        uv_center_v += cmds.polyEditUV(i, query=True)[1]
    uv_center_u = uv_center_u / len(current_sel_uv)
    uv_center_v = uv_center_v / len(current_sel_uv)
    #print "U: ", uv_center_u
    #print "V: ", uv_center_v
    # scale uv
    cmds.polyEditUV(pivotU=uv_center_u,
                    pivotV=uv_center_v,
                    scaleU=scale_factor,
                    scaleV=scale_factor)


def action_get_td(*args):
    """
    :param args:
                :arg[0] field_td
                :arg[1] field_map_size
    :return:
    """
    map_size = cmds.intField(args[1], q=1, value=1)
    td = get_texel_density(map_size)
    cmds.floatField(args[0], e=1, value=td)


def action_set_td(*args):
    """
    :param args:
                :arg[0] field_td
                :arg[1] field_map_size
    :return:
    """
    td_target = cmds.floatField(args[0], q=1, value=1)
    map_size = cmds.intField(args[1], q=1, value=1)
    td_select = get_texel_density(map_size)
    scale_ratio = td_target / td_select
    uv_scaler(scale_ratio)


def win_main(*args):
    win_name = 'txTexelDensityExtra'
    win_title = 'tx Texel Density Extra'

    # Refresh UI
    if cmds.window(win_name, exists=True, query=True):
        cmds.deleteUI(win_name)
    if cmds.windowPref(win_name, exists=True, query=True):
        cmds.windowPref(win_name, remove=True)

    # Making Window
    cmds.window(win_name,
                title=win_title,
                width=300,
                resizeToFitChildren=True,
                sizeable=False)
    # drop down menu
    cmds.menuBarLayout()
    cmds.menu(label='Help', helpMenu=True)
    cmds.menuItem(label='About',
                  command="print('tx Texel Density Extra v1.0Beta')")


    # main window content
    cmds.columnLayout('rootLayout',
                      w=300,
                      h=120,
                      columnAlign='center')

    # row 00
    cmds.rowLayout(numberOfColumns=1,
                   height=30)

    # row 01
    cmds.rowLayout('texel_density',
                   numberOfColumns=2,
                   width=300)
    cmds.text('Texel Density: ',
              w=100,
              align='right')
    field_td = cmds.floatField(w=160)
    cmds.setParent('rootLayout')

    # row 02
    cmds.rowLayout('buttons',
                   numberOfColumns=4,
                   width=300)
    cmds.separator(w=20, style='none')
    button_get = cmds.button(label='Get',
                             w=130)

    button_set = cmds.button(label='Set Uniformly',
                             w=130)
    cmds.separator(w=20, style='none')
    cmds.setParent('rootLayout')

    # row 03
    cmds.rowLayout(numberOfColumns=1,
                   height=60)
    # row 04
    cmds.rowLayout('map_size',
                   numberOfColumns=2,
                   width=300)
    cmds.text('Map Size: ',
              w=100,
              align='right')
    field_map_size = cmds.intField(value=512,
                                   w=100)
    cmds.setParent('rootLayout')

    # signals/slots
    cmds.button(button_get,
                e=True,
                command=partial(action_get_td,
                                field_td,
                                field_map_size))
    cmds.button(button_set,
                e=True,
                command=partial(action_set_td,
                                field_td,
                                field_map_size))
    # show window
    cmds.showWindow(win_name)


if __name__ == '__main__':
    win_main()