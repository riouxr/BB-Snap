bl_info = {
    "name": "BB Snap",
    "author": "Blender Bob, Claude.ai",
    "version": (1, 2, 0),
    "blender": (4, 2, 0),
    "location": "View3D > N-Panel > Tool",
    "description": "Snap objects to incremental distances using sliders",
    "category": "Object",
}

import bpy
from bpy.props import FloatProperty, EnumProperty, BoolProperty
from bpy.types import Panel, Operator, PropertyGroup
import mathutils


# Global tracking for auto-reset
_reset_timer_handle = None
_last_slider_time = 0


def move_selected_objects(context, axis, movement, coord_space):
    """Move selected objects by the specified amount"""
    selected_objects = context.selected_objects
    
    if not selected_objects:
        return
    
    for obj in selected_objects:
        if coord_space == 'GLOBAL':
            if axis == 'X':
                obj.location.x += movement
            elif axis == 'Y':
                obj.location.y += movement
            elif axis == 'Z':
                obj.location.z += movement
        else:  # LOCAL
            if axis == 'X':
                local_vector = mathutils.Vector((movement, 0, 0))
            elif axis == 'Y':
                local_vector = mathutils.Vector((0, movement, 0))
            elif axis == 'Z':
                local_vector = mathutils.Vector((0, 0, movement))
            
            global_vector = obj.matrix_world.to_3x3() @ local_vector
            obj.location += global_vector


def schedule_reset():
    """Schedule a reset check"""
    global _reset_timer_handle, _last_slider_time
    import time
    
    _last_slider_time = time.time()
    
    if _reset_timer_handle is None or not bpy.app.timers.is_registered(check_for_reset):
        _reset_timer_handle = bpy.app.timers.register(check_for_reset, first_interval=0.5)


def check_for_reset():
    """Check if enough time has passed to reset sliders"""
    global _last_slider_time, _reset_timer_handle
    import time
    
    current_time = time.time()
    time_since_last_change = current_time - _last_slider_time
    
    if time_since_last_change >= 0.5:
        try:
            if bpy.context.scene and hasattr(bpy.context.scene, 'bbsnap_props'):
                props = bpy.context.scene.bbsnap_props
                
                props["x_slider"] = 0.0
                props["y_slider"] = 0.0
                props["z_slider"] = 0.0
                props.prev_x = 0.0
                props.prev_y = 0.0
                props.prev_z = 0.0
                
                for window in bpy.context.window_manager.windows:
                    for area in window.screen.areas:
                        if area.type == 'VIEW_3D':
                            for region in area.regions:
                                if region.type == 'UI':
                                    region.tag_redraw()
        except:
            pass
        
        _reset_timer_handle = None
        return None
    
    return 0.05


def update_x_slider(self, context):
    """Update function for X slider"""
    props = context.scene.bbsnap_props
    snap_dist = props.move_snap_x
    snapped_value = round(props.x_slider / snap_dist) * snap_dist
    delta = snapped_value - props.prev_x
    
    if abs(delta) > 0.0001:
        move_selected_objects(context, 'X', delta, props.coordinate_space)
        props.prev_x = snapped_value
        schedule_reset()
    
    props["x_slider"] = snapped_value


def update_y_slider(self, context):
    """Update function for Y slider"""
    props = context.scene.bbsnap_props
    snap_dist = props.move_snap_x if props.proportional_move else props.move_snap_y
    snapped_value = round(props.y_slider / snap_dist) * snap_dist
    delta = snapped_value - props.prev_y
    
    if abs(delta) > 0.0001:
        move_selected_objects(context, 'Y', delta, props.coordinate_space)
        props.prev_y = snapped_value
        schedule_reset()
    
    props["y_slider"] = snapped_value


def update_z_slider(self, context):
    """Update function for Z slider"""
    props = context.scene.bbsnap_props
    snap_dist = props.move_snap_x if props.proportional_move else props.move_snap_z
    snapped_value = round(props.z_slider / snap_dist) * snap_dist
    delta = snapped_value - props.prev_z
    
    if abs(delta) > 0.0001:
        move_selected_objects(context, 'Z', delta, props.coordinate_space)
        props.prev_z = snapped_value
        schedule_reset()
    
    props["z_slider"] = snapped_value


def update_proportional_move(self, context):
    """Update Y and Z snap values when proportional move is toggled"""
    if self.proportional_move:
        self.move_snap_y = self.move_snap_x
        self.move_snap_z = self.move_snap_x


def update_move_snap_x(self, context):
    """Update Y and Z when X changes if proportional is on"""
    if self.proportional_move:
        self.move_snap_y = self.move_snap_x
        self.move_snap_z = self.move_snap_x


class BBSnapProperties(PropertyGroup):
    """Properties for BB Snap addon"""
    
    move_snap_x: FloatProperty(
        name="X Snap",
        description="Snap increment for X axis movement",
        default=1.0,
        min=0.001,
        soft_min=0.1,
        soft_max=10.0,
        precision=3,
        update=update_move_snap_x,
    )
    
    move_snap_y: FloatProperty(
        name="Y Snap",
        description="Snap increment for Y axis movement",
        default=1.0,
        min=0.001,
        soft_min=0.1,
        soft_max=10.0,
        precision=3,
    )
    
    move_snap_z: FloatProperty(
        name="Z Snap",
        description="Snap increment for Z axis movement",
        default=1.0,
        min=0.001,
        soft_min=0.1,
        soft_max=10.0,
        precision=3,
    )
    
    coordinate_space: EnumProperty(
        name="Coordinate Space",
        description="Move objects in Global or Local space",
        items=[
            ('GLOBAL', "Global", "Move in global coordinates"),
            ('LOCAL', "Local", "Move in local coordinates"),
        ],
        default='GLOBAL',
    )
    
    proportional_move: BoolProperty(
        name="Proportional Move",
        description="Move all axes proportionally together",
        default=False,
        update=update_proportional_move,
    )
    
    prev_x: FloatProperty(default=0.0)
    prev_y: FloatProperty(default=0.0)
    prev_z: FloatProperty(default=0.0)
    
    x_slider: FloatProperty(
        name="X",
        description="Move along X axis (snaps to increment)",
        default=0.0,
        soft_min=-10.0,
        soft_max=10.0,
        precision=3,
        update=update_x_slider,
    )
    
    y_slider: FloatProperty(
        name="Y",
        description="Move along Y axis (snaps to increment)",
        default=0.0,
        soft_min=-10.0,
        soft_max=10.0,
        precision=3,
        update=update_y_slider,
    )
    
    z_slider: FloatProperty(
        name="Z",
        description="Move along Z axis (snaps to increment)",
        default=0.0,
        soft_min=-10.0,
        soft_max=10.0,
        precision=3,
        update=update_z_slider,
    )


class BBSNAP_OT_from_selected(Operator):
    """Set move snap increments from selected object's bounding box dimensions"""
    bl_idname = "bbsnap.from_selected"
    bl_label = "From Selected"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.bbsnap_props
        props.proportional_move = False
        
        obj = context.active_object
        
        if not obj:
            self.report({'WARNING'}, "No active object")
            return {'CANCELLED'}
        
        bbox = obj.bound_box
        
        min_x = min([v[0] for v in bbox])
        max_x = max([v[0] for v in bbox])
        min_y = min([v[1] for v in bbox])
        max_y = max([v[1] for v in bbox])
        min_z = min([v[2] for v in bbox])
        max_z = max([v[2] for v in bbox])
        
        dim_x = (max_x - min_x) * obj.scale.x
        dim_y = (max_y - min_y) * obj.scale.y
        dim_z = (max_z - min_z) * obj.scale.z
        
        props.move_snap_x = abs(dim_x) if abs(dim_x) > 0.001 else 1.0
        props.move_snap_y = abs(dim_y) if abs(dim_y) > 0.001 else 1.0
        props.move_snap_z = abs(dim_z) if abs(dim_z) > 0.001 else 1.0
        
        self.report({'INFO'}, f"Set increments: X={dim_x:.3f}, Y={dim_y:.3f}, Z={dim_z:.3f}")
        
        return {'FINISHED'}


class BBSNAP_OT_set_proportional_move(Operator):
    """Toggle proportional move mode"""
    bl_idname = "bbsnap.set_proportional_move"
    bl_label = "Set Proportional Move"
    bl_options = {'REGISTER', 'UNDO'}
    
    mode: BoolProperty()
    
    def execute(self, context):
        props = context.scene.bbsnap_props
        props.proportional_move = self.mode
        return {'FINISHED'}


class BBSNAP_OT_move_button(Operator):
    """Move selected objects by snap increment. Hold SHIFT to duplicate, hold ALT for linked duplicate"""
    bl_idname = "bbsnap.move_button"
    bl_label = "Move"
    bl_options = {'REGISTER', 'UNDO'}
    
    axis: EnumProperty(
        items=[
            ('X', "X", "X axis"),
            ('Y', "Y", "Y axis"),
            ('Z', "Z", "Z axis"),
        ]
    )
    
    direction: bpy.props.IntProperty(default=1)
    shift: BoolProperty(default=False, options={'SKIP_SAVE'})
    alt: BoolProperty(default=False, options={'SKIP_SAVE'})
    
    def invoke(self, context, event):
        self.shift = event.shift
        self.alt = event.alt
        return self.execute(context)
    
    def execute(self, context):
        props = context.scene.bbsnap_props
        selected_objects = context.selected_objects
        
        if not selected_objects:
            self.report({'WARNING'}, "No objects selected")
            return {'CANCELLED'}
        
        if self.axis == 'X':
            snap_dist = props.move_snap_x
        elif self.axis == 'Y':
            snap_dist = props.move_snap_y
        elif self.axis == 'Z':
            snap_dist = props.move_snap_z
        
        movement = snap_dist * self.direction
        
        # ALT key pressed: create linked duplicate (instance)
        if self.alt:
            new_objects = []
            
            for obj in selected_objects:
                new_obj = obj.copy()
                new_obj.data = obj.data  # Share the same data (linked duplicate)
                context.collection.objects.link(new_obj)
                
                if props.coordinate_space == 'GLOBAL':
                    if self.axis == 'X':
                        new_obj.location.x = obj.location.x + movement
                    elif self.axis == 'Y':
                        new_obj.location.y = obj.location.y + movement
                    elif self.axis == 'Z':
                        new_obj.location.z = obj.location.z + movement
                else:  # LOCAL
                    if self.axis == 'X':
                        local_vector = mathutils.Vector((movement, 0, 0))
                    elif self.axis == 'Y':
                        local_vector = mathutils.Vector((0, movement, 0))
                    elif self.axis == 'Z':
                        local_vector = mathutils.Vector((0, 0, movement))
                    
                    global_vector = obj.matrix_world.to_3x3() @ local_vector
                    new_obj.location = obj.location + global_vector
                
                new_objects.append(new_obj)
            
            # Deselect original objects and select new ones
            for obj in selected_objects:
                obj.select_set(False)
            
            for obj in new_objects:
                obj.select_set(True)
            
            if new_objects:
                context.view_layer.objects.active = new_objects[-1]
            
            self.report({'INFO'}, f"Created {len(new_objects)} linked duplicate(s)")
        
        # SHIFT key pressed: create standard duplicate
        elif self.shift:
            new_objects = []
            
            for obj in selected_objects:
                new_obj = obj.copy()
                if obj.data:
                    new_obj.data = obj.data.copy()  # Copy the data (standard duplicate)
                context.collection.objects.link(new_obj)
                
                if props.coordinate_space == 'GLOBAL':
                    if self.axis == 'X':
                        new_obj.location.x = obj.location.x + movement
                    elif self.axis == 'Y':
                        new_obj.location.y = obj.location.y + movement
                    elif self.axis == 'Z':
                        new_obj.location.z = obj.location.z + movement
                else:  # LOCAL
                    if self.axis == 'X':
                        local_vector = mathutils.Vector((movement, 0, 0))
                    elif self.axis == 'Y':
                        local_vector = mathutils.Vector((0, movement, 0))
                    elif self.axis == 'Z':
                        local_vector = mathutils.Vector((0, 0, movement))
                    
                    global_vector = obj.matrix_world.to_3x3() @ local_vector
                    new_obj.location = obj.location + global_vector
                
                new_objects.append(new_obj)
            
            # Deselect original objects and select new ones
            for obj in selected_objects:
                obj.select_set(False)
            
            for obj in new_objects:
                obj.select_set(True)
            
            if new_objects:
                context.view_layer.objects.active = new_objects[-1]
            
            self.report({'INFO'}, f"Created {len(new_objects)} duplicate(s)")
        
        # No modifier key: just move
        else:
            move_selected_objects(context, self.axis, movement, props.coordinate_space)
        
        return {'FINISHED'}


class BBSNAP_PT_panel(Panel):
    """BB Snap N-Panel"""
    bl_label = "BB Snap"
    bl_idname = "BBSNAP_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.bbsnap_props
        
        box = layout.box()
        box.label(text="Settings:", icon='SETTINGS')
        
        box.label(text="Coordinate Space:")
        row = box.row(align=True)
        row.prop_enum(props, "coordinate_space", 'GLOBAL')
        row.prop_enum(props, "coordinate_space", 'LOCAL')
        
        layout.separator()
        box = layout.box()
        box.label(text="Move:", icon='ORIENTATION_GLOBAL' if props.coordinate_space == 'GLOBAL' else 'ORIENTATION_LOCAL')
        
        row = box.row(align=True)
        row.label(text="Snap Mode:")
        op = row.operator("bbsnap.set_proportional_move", text="Uniform", depress=props.proportional_move)
        op.mode = True
        op = row.operator("bbsnap.set_proportional_move", text="Per Axis", depress=not props.proportional_move)
        op.mode = False
        
        box.operator("bbsnap.from_selected", icon='SNAP_VOLUME')
        
        # Modifier key hints
        box.separator()
        hint_box = box.box()
        hint_box.label(text="Arrow Button Modifiers:", icon='INFO')
        hint_box.label(text="  Shift + Click: Duplicate & Move")
        hint_box.label(text="  Alt + Click: Linked Duplicate & Move")
        
        box.separator()
        
        # X Slider
        row = box.row(align=True)
        row.label(text="X:")
        row.prop(props, "move_snap_x", text="")
        row.separator()
        op = row.operator("bbsnap.move_button", text="", icon='TRIA_LEFT')
        op.axis = 'X'
        op.direction = -1
        row.prop(props, "x_slider", text="", slider=True)
        op = row.operator("bbsnap.move_button", text="", icon='TRIA_RIGHT')
        op.axis = 'X'
        op.direction = 1
        
        # Y Slider
        row = box.row(align=True)
        row.label(text="Y:")
        sub = row.row(align=True)
        sub.enabled = not props.proportional_move
        sub.prop(props, "move_snap_y", text="")
        row.separator()
        op = row.operator("bbsnap.move_button", text="", icon='TRIA_LEFT')
        op.axis = 'Y'
        op.direction = -1
        row.prop(props, "y_slider", text="", slider=True)
        op = row.operator("bbsnap.move_button", text="", icon='TRIA_RIGHT')
        op.axis = 'Y'
        op.direction = 1
        
        # Z Slider
        row = box.row(align=True)
        row.label(text="Z:")
        sub = row.row(align=True)
        sub.enabled = not props.proportional_move
        sub.prop(props, "move_snap_z", text="")
        row.separator()
        op = row.operator("bbsnap.move_button", text="", icon='TRIA_LEFT')
        op.axis = 'Z'
        op.direction = -1
        row.prop(props, "z_slider", text="", slider=True)
        op = row.operator("bbsnap.move_button", text="", icon='TRIA_RIGHT')
        op.axis = 'Z'
        op.direction = 1


classes = (
    BBSnapProperties,
    BBSNAP_OT_from_selected,
    BBSNAP_OT_set_proportional_move,
    BBSNAP_OT_move_button,
    BBSNAP_PT_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.bbsnap_props = bpy.props.PointerProperty(type=BBSnapProperties)


def unregister():
    global _reset_timer_handle
    
    if _reset_timer_handle is not None and bpy.app.timers.is_registered(check_for_reset):
        bpy.app.timers.unregister(check_for_reset)
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.bbsnap_props


if __name__ == "__main__":
    register()