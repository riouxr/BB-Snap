bl_info = {
    "name": "BB Snap",
    "author": "Blender Bob, Claude.ai",
    "version": (1, 0, 0),
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


# Helper function to move objects
def move_selected_objects(context, axis, movement, coord_space):
    """Move selected objects by the specified amount"""
    selected_objects = context.selected_objects
    
    if not selected_objects:
        return
    
    for obj in selected_objects:
        if coord_space == 'GLOBAL':
            # Move in global space
            if axis == 'X':
                obj.location.x += movement
            elif axis == 'Y':
                obj.location.y += movement
            elif axis == 'Z':
                obj.location.z += movement
        else:  # LOCAL
            # Move in local space
            if axis == 'X':
                local_vector = mathutils.Vector((movement, 0, 0))
            elif axis == 'Y':
                local_vector = mathutils.Vector((0, movement, 0))
            elif axis == 'Z':
                local_vector = mathutils.Vector((0, 0, movement))
            
            # Rotate the vector by the object's rotation
            global_vector = obj.matrix_world.to_3x3() @ local_vector
            obj.location += global_vector


def schedule_reset():
    """Schedule a reset check"""
    global _reset_timer_handle, _last_slider_time
    import time
    
    _last_slider_time = time.time()
    
    # Register timer if not already registered
    if _reset_timer_handle is None or not bpy.app.timers.is_registered(check_for_reset):
        _reset_timer_handle = bpy.app.timers.register(check_for_reset, first_interval=0.5)


def check_for_reset():
    """Check if enough time has passed to reset sliders"""
    global _last_slider_time, _reset_timer_handle
    import time
    
    current_time = time.time()
    time_since_last_change = current_time - _last_slider_time
    
    # If 0.5 seconds have passed since last slider change, reset
    if time_since_last_change >= 0.5:
        try:
            if bpy.context.scene and hasattr(bpy.context.scene, 'bbsnap_props'):
                props = bpy.context.scene.bbsnap_props
                
                # Reset all sliders
                props["x_slider"] = 0.0
                props["y_slider"] = 0.0
                props["z_slider"] = 0.0
                props.prev_x = 0.0
                props.prev_y = 0.0
                props.prev_z = 0.0
                props["scale_x_slider"] = 0.0
                props["scale_y_slider"] = 0.0
                props["scale_z_slider"] = 0.0
                props.prev_scale_x = 0.0
                props.prev_scale_y = 0.0
                props.prev_scale_z = 0.0
                
                # Force UI redraw
                for window in bpy.context.window_manager.windows:
                    for area in window.screen.areas:
                        if area.type == 'VIEW_3D':
                            for region in area.regions:
                                if region.type == 'UI':
                                    region.tag_redraw()
        except:
            pass
        
        _reset_timer_handle = None
        return None  # Don't repeat
    
    # Check again in 0.05 seconds
    return 0.05


# Update functions for sliders
def update_x_slider(self, context):
    """Update function for X slider"""
    props = context.scene.bbsnap_props
    
    # Snap the slider value to the snap_distance increment
    snapped_value = round(props.x_slider / props.snap_distance) * props.snap_distance
    
    # Calculate delta from previous snapped value
    delta = snapped_value - props.prev_x
    
    if abs(delta) > 0.0001:  # Only move if there's actual change
        move_selected_objects(context, 'X', delta, props.coordinate_space)
        props.prev_x = snapped_value
        schedule_reset()
    
    # Force the slider to the snapped value (without triggering update again)
    props["x_slider"] = snapped_value


def update_y_slider(self, context):
    """Update function for Y slider"""
    props = context.scene.bbsnap_props
    
    # Snap the slider value to the snap_distance increment
    snapped_value = round(props.y_slider / props.snap_distance) * props.snap_distance
    
    # Calculate delta from previous snapped value
    delta = snapped_value - props.prev_y
    
    if abs(delta) > 0.0001:
        move_selected_objects(context, 'Y', delta, props.coordinate_space)
        props.prev_y = snapped_value
        schedule_reset()
    
    # Force the slider to the snapped value (without triggering update again)
    props["y_slider"] = snapped_value


def update_z_slider(self, context):
    """Update function for Z slider"""
    props = context.scene.bbsnap_props
    
    # Snap the slider value to the snap_distance increment
    snapped_value = round(props.z_slider / props.snap_distance) * props.snap_distance
    
    # Calculate delta from previous snapped value
    delta = snapped_value - props.prev_z
    
    if abs(delta) > 0.0001:
        move_selected_objects(context, 'Z', delta, props.coordinate_space)
        props.prev_z = snapped_value
        schedule_reset()
    
    # Force the slider to the snapped value (without triggering update again)
    props["z_slider"] = snapped_value


def update_snap_distance(self, context):
    """Update function for snap distance"""
    # This can be used to adjust slider behavior if needed
    pass


# Scale update functions
def update_scale_x_slider(self, context):
    """Update function for X scale slider"""
    props = context.scene.bbsnap_props
    
    # Snap the slider value to the snap_distance increment
    snapped_value = round(props.scale_x_slider / props.snap_distance) * props.snap_distance
    
    # Calculate delta from previous snapped value
    delta = snapped_value - props.prev_scale_x
    
    if abs(delta) > 0.0001:  # Only scale if there's actual change
        if props.proportional_scale:
            # Scale all axes proportionally
            scale_selected_objects(context, 'XYZ', delta, props.coordinate_space)
            props.prev_scale_y = snapped_value
            props.prev_scale_z = snapped_value
            props["scale_y_slider"] = snapped_value
            props["scale_z_slider"] = snapped_value
        else:
            scale_selected_objects(context, 'X', delta, props.coordinate_space)
        props.prev_scale_x = snapped_value
        schedule_reset()
    
    # Force the slider to the snapped value (without triggering update again)
    props["scale_x_slider"] = snapped_value


def update_scale_y_slider(self, context):
    """Update function for Y scale slider"""
    props = context.scene.bbsnap_props
    
    # Snap the slider value to the snap_distance increment
    snapped_value = round(props.scale_y_slider / props.snap_distance) * props.snap_distance
    
    # Calculate delta from previous snapped value
    delta = snapped_value - props.prev_scale_y
    
    if abs(delta) > 0.0001:
        if props.proportional_scale:
            # Scale all axes proportionally
            scale_selected_objects(context, 'XYZ', delta, props.coordinate_space)
            props.prev_scale_x = snapped_value
            props.prev_scale_z = snapped_value
            props["scale_x_slider"] = snapped_value
            props["scale_z_slider"] = snapped_value
        else:
            scale_selected_objects(context, 'Y', delta, props.coordinate_space)
        props.prev_scale_y = snapped_value
        schedule_reset()
    
    # Force the slider to the snapped value (without triggering update again)
    props["scale_y_slider"] = snapped_value


def update_scale_z_slider(self, context):
    """Update function for Z scale slider"""
    props = context.scene.bbsnap_props
    
    # Snap the slider value to the snap_distance increment
    snapped_value = round(props.scale_z_slider / props.snap_distance) * props.snap_distance
    
    # Calculate delta from previous snapped value
    delta = snapped_value - props.prev_scale_z
    
    if abs(delta) > 0.0001:
        if props.proportional_scale:
            # Scale all axes proportionally
            scale_selected_objects(context, 'XYZ', delta, props.coordinate_space)
            props.prev_scale_x = snapped_value
            props.prev_scale_y = snapped_value
            props["scale_x_slider"] = snapped_value
            props["scale_y_slider"] = snapped_value
        else:
            scale_selected_objects(context, 'Z', delta, props.coordinate_space)
        props.prev_scale_z = snapped_value
        schedule_reset()
    
    # Force the slider to the snapped value (without triggering update again)
    props["scale_z_slider"] = snapped_value


def scale_selected_objects(context, axis, scale_delta, coord_space):
    """Scale selected objects by the specified amount"""
    selected_objects = context.selected_objects
    
    if not selected_objects:
        return
    
    for obj in selected_objects:
        if axis == 'XYZ':
            # Proportional scaling on all axes
            obj.scale.x += scale_delta
            obj.scale.y += scale_delta
            obj.scale.z += scale_delta
        elif coord_space == 'GLOBAL':
            # Scale in global space
            if axis == 'X':
                obj.scale.x += scale_delta
            elif axis == 'Y':
                obj.scale.y += scale_delta
            elif axis == 'Z':
                obj.scale.z += scale_delta
        else:  # LOCAL
            # For local scale, we still use the object's own scale
            # (scale is always in local space by nature)
            if axis == 'X':
                obj.scale.x += scale_delta
            elif axis == 'Y':
                obj.scale.y += scale_delta
            elif axis == 'Z':
                obj.scale.z += scale_delta


class BBSnapProperties(PropertyGroup):
    """Properties for BB Snap addon"""
    
    snap_distance: FloatProperty(
        name="Snap Distance",
        description="Distance to move objects per slider increment",
        default=1.0,
        min=0.001,
        soft_min=0.1,
        soft_max=10.0,
        precision=3,
        step=1,
        update=update_snap_distance,
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
    
    proportional_scale: BoolProperty(
        name="Proportional Scale",
        description="Scale all axes proportionally together",
        default=True,
    )
    
    # Store previous values for calculating delta
    prev_x: FloatProperty(default=0.0)
    prev_y: FloatProperty(default=0.0)
    prev_z: FloatProperty(default=0.0)
    
    prev_scale_x: FloatProperty(default=0.0)
    prev_scale_y: FloatProperty(default=0.0)
    prev_scale_z: FloatProperty(default=0.0)
    
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
    
    scale_x_slider: FloatProperty(
        name="X",
        description="Scale along X axis (snaps to increment)",
        default=0.0,
        soft_min=-10.0,
        soft_max=10.0,
        precision=3,
        update=update_scale_x_slider,
    )
    
    scale_y_slider: FloatProperty(
        name="Y",
        description="Scale along Y axis (snaps to increment)",
        default=0.0,
        soft_min=-10.0,
        soft_max=10.0,
        precision=3,
        update=update_scale_y_slider,
    )
    
    scale_z_slider: FloatProperty(
        name="Z",
        description="Scale along Z axis (snaps to increment)",
        default=0.0,
        soft_min=-10.0,
        soft_max=10.0,
        precision=3,
        update=update_scale_z_slider,
    )


class BBSNAP_OT_move_objects(Operator):
    """Move selected objects by snap distance"""
    bl_idname = "bbsnap.move_objects"
    bl_label = "Move Objects"
    bl_options = {'REGISTER', 'UNDO'}
    
    axis: EnumProperty(
        items=[
            ('X', "X", "X axis"),
            ('Y', "Y", "Y axis"),
            ('Z', "Z", "Z axis"),
        ]
    )
    
    value: FloatProperty()
    previous_value: FloatProperty()
    
    def execute(self, context):
        props = context.scene.bbsnap_props
        
        # Calculate the delta movement
        delta = self.value - self.previous_value
        movement = delta * props.snap_distance
        
        # Get selected objects
        selected_objects = context.selected_objects
        
        if not selected_objects:
            self.report({'WARNING'}, "No objects selected")
            return {'CANCELLED'}
        
        # Move objects
        for obj in selected_objects:
            if props.coordinate_space == 'GLOBAL':
                # Move in global space
                if self.axis == 'X':
                    obj.location.x += movement
                elif self.axis == 'Y':
                    obj.location.y += movement
                elif self.axis == 'Z':
                    obj.location.z += movement
            else:  # LOCAL
                # Move in local space
                import mathutils
                if self.axis == 'X':
                    local_vector = mathutils.Vector((movement, 0, 0))
                elif self.axis == 'Y':
                    local_vector = mathutils.Vector((0, movement, 0))
                elif self.axis == 'Z':
                    local_vector = mathutils.Vector((0, 0, movement))
                
                # Rotate the vector by the object's rotation
                global_vector = obj.matrix_world.to_3x3() @ local_vector
                obj.location += global_vector
        
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
        
        # Snap Distance field
        box = layout.box()
        box.label(text="Settings:", icon='SETTINGS')
        box.prop(props, "snap_distance")
        
        # Coordinate Space checkboxes (as radio buttons)
        box.label(text="Coordinate Space:")
        row = box.row(align=True)
        row.prop_enum(props, "coordinate_space", 'GLOBAL')
        row.prop_enum(props, "coordinate_space", 'LOCAL')
        
        # Move Sliders
        layout.separator()
        box = layout.box()
        box.label(text="Move:", icon='ORIENTATION_GLOBAL' if props.coordinate_space == 'GLOBAL' else 'ORIENTATION_LOCAL')
        
        # X Slider
        row = box.row()
        row.label(text="X:")
        row.prop(props, "x_slider", text="", slider=True)
        
        # Y Slider
        row = box.row()
        row.label(text="Y:")
        row.prop(props, "y_slider", text="", slider=True)
        
        # Z Slider
        row = box.row()
        row.label(text="Z:")
        row.prop(props, "z_slider", text="", slider=True)
        
        # Scale Sliders
        layout.separator()
        box = layout.box()
        box.label(text="Scale:", icon='EMPTY_ARROWS')
        
        # Proportional Scale checkbox
        box.prop(props, "proportional_scale")
        
        # Scale X Slider
        row = box.row()
        row.label(text="X:")
        row.prop(props, "scale_x_slider", text="", slider=True)
        
        # Scale Y Slider (greyed out if proportional)
        row = box.row()
        row.enabled = not props.proportional_scale
        row.label(text="Y:")
        row.prop(props, "scale_y_slider", text="", slider=True)
        
        # Scale Z Slider (greyed out if proportional)
        row = box.row()
        row.enabled = not props.proportional_scale
        row.label(text="Z:")
        row.prop(props, "scale_z_slider", text="", slider=True)


classes = (
    BBSnapProperties,
    BBSNAP_OT_move_objects,
    BBSNAP_PT_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.bbsnap_props = bpy.props.PointerProperty(type=BBSnapProperties)


def unregister():
    global _reset_timer_handle
    
    # Clean up any running timers
    if _reset_timer_handle is not None and bpy.app.timers.is_registered(check_for_reset):
        bpy.app.timers.unregister(check_for_reset)
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.bbsnap_props


if __name__ == "__main__":
    register()
