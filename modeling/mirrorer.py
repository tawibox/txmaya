import os
import shutil
import sys
import stat
import time
from subprocess import Popen, PIPE
from functools import partial
import maya.cmds as cmds


def main_win():
    win_name = 'mainUI'
    win_title = 'tx Mirrorer'

    # Refresh UI
    if cmds.window(win_name, exists=True, query=True):
        cmds.deleteUI(win_name)
    if cmds.windowPref(win_name, exists=True, query=True):
        cmds.windowPref(win_name, remove=True)

    # Create window
    cmds.window(win_name,
                title=win_title,
                sizeable=False,
                resizeToFitChildren=True)

    # Menu dropdown
    menuBarLayout = cmds.menuBarLayout()
    cmds.menu(label='File')
    cmds.menuItem(label='Reset')
    cmds.menu(label='Help', helpMenu=True)
    cmds.menuItem(label='About')

    # Main window contecsnt
    cmds.columnLayout('rootLayout', w=300, h=60)

    # Button01
    cmds.rowLayout('button01Layout', w=300, h=30, numberOfColumns=3)
    cmds.separator(w=50, style='none')
    cmds.button(label='Along X',
                w=200,
                backgroundColor=(0.3, 0.1, 0.1),
                command=partial(mirrorer, '.scaleX'))
    cmds.separator(w=50, style='none')
    cmds.setParent('rootLayout')

    # Button02
    cmds.rowLayout('button02Layout', w=300, h=30, numberOfColumns=3)
    cmds.separator(w=50, style='none')
    cmds.button(label='Along Y',
                w=200,
                backgroundColor=(0.1, 0.3, 0.1),
                command=partial(mirrorer, '.scaleY'))
    cmds.separator(w=50, style='none')
    cmds.setParent('rootLayout')

    # Button03
    cmds.rowLayout('button03Layout', w=300, h=30, numberOfColumns=3)
    cmds.separator(w=50, style='none')
    cmds.button(label='Along Z',
                w=200,
                backgroundColor=(0.1, 0.1, 0.3),
                command=partial(mirrorer, '.scaleZ'))
    cmds.separator(w=50, style='none')
    cmds.setParent('rootLayout')

    # Show window
    cmds.showWindow()

def mirrorer(channel, *args):

    current_selection = cmds.ls(sl=True, long=True)
    mirror_channel = channel

    for i in current_selection:
        #print i
        #parent_path = cmds.listRelatives(i, p=True, fullPath=True)[0] + '|'
        #print parent_path
        i_copy = cmds.duplicate(i)
        # cmds.parent(i, world=True)
        # cmds.parent(i_copy, world=True)
        grp_temp = cmds.group(i_copy[0], n=i_copy[0]+"_grp_temp")
        cmds.xform(grp_temp,
                   worldSpace=True,
                   scalePivot=[0, 0, 0],
                   rotatePivot=[0, 0, 0])
        cmds.setAttr(grp_temp + mirror_channel, -1)
        cmds.ungroup(grp_temp)
        cmds.makeIdentity(i_copy[0],
                          apply=True,
                          preserveNormals=True,
                          translate=False,
                          rotate=False,
                          scale=True,
                          normal=False)

main_win() #Internal Testimport os
