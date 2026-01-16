# BB Snap

A Blender addon for precise object transformation using snap-to-increment sliders.

## Features

- **Snap Distance Control**: Set a custom snap increment for all transformations
- **Move Objects**: Translate objects along X, Y, and Z axes with snapped precision
- **Scale Objects**: Scale objects with optional proportional scaling across all axes
- **Coordinate Spaces**: Switch between Global and Local coordinate systems
- **Auto-Reset Sliders**: Sliders automatically reset to zero after 0.5 seconds of inactivity
- **Proportional Scale**: Scale all three axes uniformly (enabled by default)

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

**Snap Distance**: Set the increment value for all transformations. Objects will move/scale in multiples of this value.

**Coordinate Space**:
- **Global**: Transform objects relative to world coordinates
- **Local**: Transform objects relative to their local orientation

### Move

Use the X, Y, Z sliders to translate selected objects:
- Drag the slider left or right to move objects
- Movement snaps to your specified increment
- Sliders automatically reset to zero after 0.5 seconds

### Scale

Use the X, Y, Z sliders to scale selected objects:
- **Proportional Scale** (default): All three axes scale together uniformly
- Uncheck to scale each axis independently
- Scaling snaps to your specified increment
- Sliders automatically reset to zero after 0.5 seconds

## Tips

- Select one or more objects before using the sliders
- The snap increment applies to both move and scale operations
- You can scrub back and forth on sliders for quick adjustments
- Local coordinate space is useful for moving objects along their own orientation

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
- Move and Scale sliders with snap-to-increment functionality
- Global and Local coordinate space support
- Proportional scaling option
- Auto-reset sliders on inactivity
- Integrated into Tool tab
