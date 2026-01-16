# BB Snap

A Blender addon for precise object transformation using snap-to-increment sliders with advanced movement controls.

## Features

- **Per-Axis Snap Control**: Set independent snap increments for X, Y, and Z axes
- **Move Objects**: Translate objects along X, Y, and Z axes with snapped precision
- **Arrow Buttons**: Quick move buttons (left/right arrows) for instant precise movement
- **Instance Copy**: Create linked duplicates with automatic offset positioning
- **Coordinate Spaces**: Switch between Global and Local coordinate systems
- **Auto-Reset Sliders**: Sliders automatically reset to zero after 0.5 seconds of inactivity
- **Snap Modes**: 
  - **Uniform**: All axes use the same snap increment (X value)
  - **Per Axis**: Each axis has its own independent snap increment
- **From Selected**: Automatically set snap increments from object's bounding box dimensions

## Installation

1. Download the latest `bb_snap_modified.zip` from the [Releases](../../releases) page
2. Open Blender (4.2.0 or later)
3. Go to `Edit > Preferences > Add-ons`
4. Click `Install...` and select the downloaded zip file
5. Enable the addon by checking the box next to "BB Snap"

## Usage

### Accessing the Addon

The BB Snap panel is located in the 3D Viewport's sidebar:
- Press `N` to open the sidebar
- Navigate to the **Tool** tab
- Find the **BB Snap** panel

### Settings

**Coordinate Space**:
- **Global**: Transform objects relative to world coordinates
- **Local**: Transform objects relative to their local orientation

**Snap Mode**:
- **Uniform**: All axes use the X axis snap increment (Y and Z fields are greyed out)
- **Per Axis**: Each axis has its own independent snap increment value

### Move Controls

Each axis (X, Y, Z) has the following controls:

**Layout**: `[Label] [Snap Value] [◄] [Slider] [►] [I]`

- **Snap Value Field**: Set the snap increment for this axis (greyed out in Uniform mode for Y/Z)
- **Left Arrow (◄)**: Move objects negative direction by snap increment
- **Slider**: Drag to move objects, snaps to increment, auto-resets after 0.5s
- **Right Arrow (►)**: Move objects positive direction by snap increment  
- **Instance (I)**: Create linked duplicate and offset by snap increment

### From Selected Button

Click "From Selected" to automatically set snap increments based on the active object's bounding box:
- X snap = object width
- Y snap = object depth
- Z snap = object height
- Automatically switches to "Per Axis" mode

## Tips

- Select one or more objects before using the controls
- Use arrow buttons for precise single-increment movements
- Use the slider for continuous movement with auto-reset
- Use Instance (I) button to quickly create arrays of objects
- "From Selected" is perfect for aligning objects to existing geometry
- Local coordinate space is useful for moving objects along their own orientation
- Uniform mode ensures consistent spacing across all axes

## Requirements

- Blender 4.2.0 or later

## License

This addon is licensed under the GNU General Public License v3.0 or later.

## Credits

- **Author**: Blender Bob
- **Co-Author**: Claude.ai (Anthropic)

## Support

If you encounter any issues or have suggestions, please [open an issue](../../issues) on GitHub.

## Changelog

### Version 1.0.0
- Initial release
- Per-axis snap increment control
- Move sliders with snap-to-increment functionality
- Left/right arrow buttons for quick precise movement
- Instance copy button for creating linked duplicates
- Global and Local coordinate space support
- Uniform and Per Axis snap modes
- From Selected button for automatic snap sizing
- Auto-reset sliders on inactivity
- Integrated into Tool tab
