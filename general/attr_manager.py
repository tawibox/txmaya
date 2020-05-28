import maya.cmds as cmds
from functools import partial


win_name = 'mainUI'
win_title = 'Text Field'


current_selection = cmds.ls(sl=True, long=True, dag=True)
list_mesh = cmds.listRelatives(current_selection,
                               shapes=True,
                               type="mesh",
                               fullPath=True) or []


def create_attr_number(attr_name, object,
                       attr_type, default_value):
    '''
    attr_type: int ('long'), float('float')
    '''
    if not cmds.attributeQuery(attr_name, node=object, exists=True):
        cmds.addAttr(object,
                     longName=attr_name,
                     attributeType=attr_type,
                     defaultValue=default_value)


def create_attr_vector(attr_name, object,
                       default_value_x, default_value_y, default_value_z):
    if not cmds.attributeQuery(attr_name, node=object, exists=True):
        cmds.addAttr(object,
                     longName=attr_name,
                     attributeType='double3')
        cmds.addAttr(object,
                     longName=attr_name + 'X',
                     attributeType='double',
                     p=attr_name,
                     defaultValue=default_value_x)
        cmds.addAttr(object,
                     longName=attr_name + 'Y',
                     attributeType='double',
                     p=attr_name,
                     defaultValue=default_value_y)
        cmds.addAttr(object,
                     longName=attr_name + 'Z',
                     attributeType='double',
                     p=attr_name,
                     defaultValue=default_value_z)


def create_attr_string(attr_name, object,
                       attr_type, default_string):
    if not cmds.attributeQuery(attr_name, node=object, exists=True):
        cmds.addAttr(object, longName=attr_name, dataType=attr_type)
    cmds.setAttr(object + '.' + attr_name, default_string, type=attr_type)


# for i in list_mesh:
    # create_attr_number('mtoa_constant_uv_offset_u', i, 'float', 0)
    # create_attr_number('mtoa_constant_uv_offset_v', i, 'float', 0)
    # create_attr_number('mtoa_constant_uv_scale', i, 'float', 1)
    # create_attr_number('mtoa_constant_uv_rotate', i, 'float', 0)
    # create_attr_number('mtoa_constant_id_01', i, 'long', 0)
    # create_attr_string('mtoa_constant_my_string', i, 'string', 'some default')
    # create_attr_vector('mtoa_constant_my_vector', i, 1, 0, 3)





def main_win(print_text_field):
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

    # Main window content
    cmds.columnLayout('rootLayout')

    # Text Field - attr name
    cmds.rowLayout('textField', w=300, h=30, numberOfColumns=3)
    cmds.text(w=50, label='Attribute Name:')
    input_text = cmds.textField(w=200, text="type sth here...")
    cmds.setParent('rootLayout')

    # Int Field
    cmds.rowLayout('intField', w=300, h=30, numberOfColumns=3)
    cmds.text(w=50, label='Attribute Type:')
    input_int = cmds.intField(w=200, value=0.1)
    cmds.setParent('rootLayout')

    # Button
    cmds.rowLayout('buttonLayout', w=300, h=50, numberOfColumns=3)
    cmds.separator(w=50, style='none')
    cmds.button(label='Print content from fields above',
                w=200,
                command=partial(print_text_field, input_text, input_int))
    cmds.separator(w=50, style='none')
    cmds.setParent('rootLayout')

    # Show window
    cmds.showWindow()


def print_text_field(input_text, input_int, *args):
    field_content_string = cmds.textField(input_text, q=True, text=True)
    field_content_int = cmds.intField(input_int, q=True, value=True)
    print '###'
    print 'Text Input: %s' % field_content_string
    print 'Int Input: %s' % field_content_int
    print '###'


main_win(print_text_field)