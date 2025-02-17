# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
from bpy.types import AddonPreferences

bl_info = {
    "name": "Quick Toggle Visibility",
    "author": "purplefire",
    "description": "Toggle object visibility with a pie menu shortcut",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "location": "View3D > Ctrl+Alt+V (customizable)",
    "warning": "",
    "category": "Object",
}

addon_keymaps = []


class KeyframeTogglePreferences(AddonPreferences):
    bl_idname = __name__

    items = []
    for char in range(65, 91):
        items.append((chr(char), chr(char), ""))
    for num in range(48, 58):
        items.append((chr(num), chr(num), ""))

    key_type: bpy.props.EnumProperty(
        name="Keymap",
        description="Choose the key type for the shortcut",
        items=items,
        default="V",
    )  # type: ignore

    use_ctrl: bpy.props.BoolProperty(name="Use Ctrl", default=True)  # type: ignore

    use_alt: bpy.props.BoolProperty(name="Use Alt", default=True)  # type: ignore

    display_type_hidden: bpy.props.EnumProperty(
        name="Display When Hidden",
        description="Choose how objects appear when hidden",
        items=[
            ("WIRE", "Wireframe", "Show as wireframe"),
            ("BOUNDS", "Bounds", "Show as bounds"),
            ("Hide", "Hide", "Hide in viewport"),
        ],
        default="WIRE",
    )  # type: ignore
    display_in_render: bpy.props.BoolProperty(
        name="Display in render",
        default=True,
        description="Set object display in render",
    )  # type: ignore

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Shortcut Settings:")
        row = box.row()
        row.prop(self, "key_type")
        row.prop(self, "use_ctrl")
        row.prop(self, "use_alt")

        box = layout.box()
        box.label(text="Display Settings:")
        box.prop(self, "display_type_hidden")
        box.prop(self, "display_in_render")


def get_preferences():
    return bpy.context.preferences.addons[__name__].preferences


def keyframe_toggle_forward(context):
    prefs = get_preferences()
    for obj in context.selected_objects:
        try:
            if prefs.display_in_render:
                obj.hide_render = True
                obj.keyframe_insert(
                    data_path="hide_render", frame=context.scene.frame_current - 1
                )
            if prefs.display_type_hidden == "Hide":
                obj.hide_viewport = True
                obj.keyframe_insert(
                    data_path="hide_viewport", frame=context.scene.frame_current - 1
                )
            else:
                obj.display_type = prefs.display_type_hidden
                obj.keyframe_insert(
                    data_path="display_type", frame=context.scene.frame_current - 1
                )

            if prefs.display_in_render:
                obj.hide_render = False
                obj.keyframe_insert(
                    data_path="hide_render", frame=context.scene.frame_current
                )
            if prefs.display_type_hidden == "Hide":
                obj.hide_viewport = False
                obj.keyframe_insert(
                    data_path="hide_viewport", frame=context.scene.frame_current
                )
            else:
                obj.display_type = "SOLID"
                obj.keyframe_insert(
                    data_path="display_type", frame=context.scene.frame_current
                )

        except Exception as e:
            print(f"Error toggling object {obj.name}: {str(e)}")


def keyframe_toggle_backward(context):
    prefs = get_preferences()
    for obj in context.selected_objects:
        try:
            if prefs.display_in_render:
                obj.hide_render = False
                obj.keyframe_insert(
                    data_path="hide_render", frame=context.scene.frame_current
                )
            if prefs.display_type_hidden == "Hide":
                obj.hide_viewport = False
                obj.keyframe_insert(
                    data_path="hide_viewport", frame=context.scene.frame_current
                )
            else:
                obj.display_type = "SOLID"
                obj.keyframe_insert(
                    data_path="display_type", frame=context.scene.frame_current
                )

            if prefs.display_in_render:
                obj.hide_render = True
                obj.keyframe_insert(
                    data_path="hide_render", frame=context.scene.frame_current + 1
                )
            if prefs.display_type_hidden == "Hide":
                obj.hide_viewport = True
                obj.keyframe_insert(
                    data_path="hide_viewport", frame=context.scene.frame_current + 1
                )
            else:
                obj.display_type = prefs.display_type_hidden
                obj.keyframe_insert(
                    data_path="display_type", frame=context.scene.frame_current + 1
                )

        except Exception as e:
            print(f"Error toggling object {obj.name}: {str(e)}")


def hide_object(context):
    prefs = get_preferences()
    for obj in context.selected_objects:
        if prefs.display_in_render:
            obj.hide_render = True
        if prefs.display_type_hidden == "Hide":
            obj.hide_viewport = True
        else:
            obj.display_type = prefs.display_type_hidden


def show_object(context):
    prefs = get_preferences()
    for obj in context.selected_objects:
        if prefs.display_in_render:
            obj.hide_render = False
        if prefs.display_type_hidden == "Hide":
            obj.hide_viewport = False
        else:
            obj.display_type = "SOLID"


class ObjectVisibilityPieMenu(bpy.types.Menu):
    bl_label = "Object Visibility Pie Menu"
    bl_idname = "OBJECT_MT_visibility_pie_menu"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator(ExecuteKeyframeToggleForward.bl_idname, text="Hide->Show")
        pie.operator(ExecuteKeyframeToggleBackward.bl_idname, text="Show->Hide")
        pie.operator(ExecuteHideObject.bl_idname, text="Hide")
        pie.operator(ExecuteShowObject.bl_idname, text="Show")


class ExecuteKeyframeToggleForward(bpy.types.Operator):
    bl_idname = "object.execute_keyframe_toggle_forward"
    bl_label = "Execute Keyframe Toggle Forward"
    bl_description = "Toggle object visibility state forward"

    def execute(self, context):
        keyframe_toggle_forward(context)
        return {"FINISHED"}


class ExecuteKeyframeToggleBackward(bpy.types.Operator):
    bl_idname = "object.execute_keyframe_toggle_backward"
    bl_label = "Execute Keyframe Toggle Backward"
    bl_description = "Toggle object visibility state backward"

    def execute(self, context):
        keyframe_toggle_backward(context)
        return {"FINISHED"}


class ExecuteHideObject(bpy.types.Operator):
    bl_idname = "object.execute_hide_object"
    bl_label = "Execute Hide Object"
    bl_description = "Hide Object"

    def execute(self, context):
        hide_object(context)
        return {"FINISHED"}


class ExecuteShowObject(bpy.types.Operator):
    bl_idname = "object.execute_show_object"
    bl_label = "Execute Show Object"
    bl_description = "Show Object"

    def execute(self, context):
        show_object(context)
        return {"FINISHED"}


classes = (
    KeyframeTogglePreferences,
    ObjectVisibilityPieMenu,
    ExecuteKeyframeToggleForward,
    ExecuteKeyframeToggleBackward,
    ExecuteHideObject,
    ExecuteShowObject,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        prefs = get_preferences()
        km = kc.keymaps.new(name="Object Mode")
        kmi = km.keymap_items.new(
            "wm.call_menu_pie",
            prefs.key_type,
            "PRESS",
            ctrl=prefs.use_ctrl,
            alt=prefs.use_alt,
        )
        kmi.properties.name = ObjectVisibilityPieMenu.bl_idname
        addon_keymaps.append((km, kmi))


def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
