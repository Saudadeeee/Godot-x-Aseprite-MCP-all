"""Utility functions for Aseprite MCP"""

from aseprite_mcp import mcp
from aseprite_mcp.core.commands import AsepriteCommand
import os
import shutil
from datetime import datetime


@mcp.tool()
async def batch_convert(input_folder: str, output_folder: str, format: str) -> str:
    """
    Batch convert files to another format

    Args:
        input_folder: Folder with .aseprite files
        output_folder: Output folder
        format: Target format (png, gif, jpg)

    Returns:
        Success or error message
    """
    if not os.path.exists(input_folder):
        return f"Error: Input folder '{input_folder}' not found"

    os.makedirs(output_folder, exist_ok=True)

    files = [f for f in os.listdir(input_folder) if f.endswith('.aseprite') or f.endswith('.ase')]

    if not files:
        return "Error: No .aseprite files found"

    converted = 0
    for file in files:
        input_path = os.path.join(input_folder, file)
        output_name = os.path.splitext(file)[0] + f".{format}"
        output_path = os.path.join(output_folder, output_name)

        abs_input = os.path.abspath(input_path).replace('\\', '/')
        abs_output = os.path.abspath(output_path).replace('\\', '/')

        lua_script = f"""
        local sprite = app.open('{abs_input}')
        if sprite then
            sprite:saveCopyAs('{abs_output}')
            sprite:close()
        end
        """

        success, _ = AsepriteCommand.execute_lua_script(lua_script)
        if success:
            converted += 1

    return f"Success: Converted {converted}/{len(files)} files to {format}"


@mcp.tool()
async def optimize_file_size(filename: str) -> str:
    """
    Optimize file size (basic compression)

    Args:
        filename: Name of the Aseprite file

    Returns:
        Success or error message
    """
    if not os.path.exists(filename):
        return f"Error: File '{filename}' not found"

    original_size = os.path.getsize(filename)

    # Just resave - Aseprite will optimize
    lua_script = f"""
    local sprite = app.open('{filename}')
    if sprite then
        sprite:saveAs('{filename}')
        sprite:close()
    end
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)

    if success:
        new_size = os.path.getsize(filename)
        saved = original_size - new_size
        percent = (saved / original_size * 100) if original_size > 0 else 0
        return f"Success: Optimized file. Saved {saved} bytes ({percent:.1f}%)"

    return f"Error: {output}"


@mcp.tool()
async def get_sprite_info(filename: str) -> str:
    """
    Get detailed sprite information

    Args:
        filename: Name of the Aseprite file

    Returns:
        Sprite information or error message
    """
    if not os.path.exists(filename):
        return f"Error: File '{filename}' not found"

    lua_script = f"""
    local sprite = app.open('{filename}')
    if not sprite then
        print("Error: Failed to open sprite")
        return
    end

    local info = {{
        "Dimensions: " .. sprite.width .. "x" .. sprite.height,
        "Color Mode: " .. tostring(sprite.colorMode),
        "Frames: " .. #sprite.frames,
        "Layers: " .. #sprite.layers,
        "Palette Colors: " .. #sprite.palettes[1],
        "Filesize: " .. tostring(sprite.filename)
    }}

    sprite:close()
    print(table.concat(info, ", "))
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def compare_sprites(file1: str, file2: str) -> str:
    """
    Compare two sprites

    Args:
        file1: First sprite file
        file2: Second sprite file

    Returns:
        Comparison results
    """
    if not os.path.exists(file1):
        return f"Error: File '{file1}' not found"
    if not os.path.exists(file2):
        return f"Error: File '{file2}' not found"

    # Simple comparison - size and frame count
    lua_script = f"""
    local s1 = app.open('{file1}')
    local s2 = app.open('{file2}')

    if not s1 or not s2 then
        print("Error: Failed to open sprites")
        return
    end

    local same_size = (s1.width == s2.width and s1.height == s2.height)
    local same_frames = (#s1.frames == #s2.frames)
    local same_layers = (#s1.layers == #s2.layers)

    s1:close()
    s2:close()

    print("Size match: " .. tostring(same_size) .. ", Frames match: " .. tostring(same_frames) .. ", Layers match: " .. tostring(same_layers))
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def backup_sprite(filename: str, backup_folder: str = None) -> str:
    """
    Create backup with timestamp

    Args:
        filename: Name of the Aseprite file
        backup_folder: Backup folder (default: backups/)

    Returns:
        Success or error message
    """
    if not os.path.exists(filename):
        return f"Error: File '{filename}' not found"

    if backup_folder is None:
        backup_folder = "backups"

    os.makedirs(backup_folder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    basename = os.path.splitext(os.path.basename(filename))[0]
    backup_name = f"{basename}_{timestamp}.aseprite"
    backup_path = os.path.join(backup_folder, backup_name)

    shutil.copy2(filename, backup_path)

    return f"Success: Backup created: {backup_path}"


@mcp.tool()
async def restore_sprite(filename: str, backup_timestamp: str) -> str:
    """
    Restore from backup

    Args:
        filename: Target filename
        backup_timestamp: Timestamp of backup to restore

    Returns:
        Success or error message
    """
    backup_folder = "backups"
    basename = os.path.splitext(os.path.basename(filename))[0]
    backup_name = f"{basename}_{backup_timestamp}.aseprite"
    backup_path = os.path.join(backup_folder, backup_name)

    if not os.path.exists(backup_path):
        return f"Error: Backup '{backup_path}' not found"

    shutil.copy2(backup_path, filename)
    return f"Success: Restored from backup {backup_timestamp}"


@mcp.tool()
async def convert_color_mode(filename: str, mode: str) -> str:
    """
    Convert color mode

    Args:
        filename: Name of the Aseprite file
        mode: Target mode (rgb, grayscale, indexed)

    Returns:
        Success or error message
    """
    if not os.path.exists(filename):
        return f"Error: File '{filename}' not found"

    mode_map = {
        "rgb": "ColorMode.RGB",
        "grayscale": "ColorMode.GRAYSCALE",
        "indexed": "ColorMode.INDEXED"
    }

    if mode.lower() not in mode_map:
        return f"Error: Invalid mode. Use: rgb, grayscale, indexed"

    lua_script = f"""
    local sprite = app.open('{filename}')
    if not sprite then
        print("Error: Failed to open sprite")
        return
    end

    app.command.ChangePixelFormat{{format="{mode.lower()}"}}

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Converted to {mode} color mode")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def set_grid(filename: str, width: int, height: int) -> str:
    """
    Set grid size

    Args:
        filename: Name of the Aseprite file
        width: Grid width
        height: Grid height

    Returns:
        Success or error message
    """
    if not os.path.exists(filename):
        return f"Error: File '{filename}' not found"

    lua_script = f"""
    local sprite = app.open('{filename}')
    if not sprite then
        print("Error: Failed to open sprite")
        return
    end

    sprite.gridBounds = Rectangle(0, 0, {width}, {height})

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Set grid to {width}x{height}")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def toggle_grid(filename: str, visible: bool) -> str:
    """
    Show/hide grid

    Args:
        filename: Name of the Aseprite file
        visible: True to show, False to hide

    Returns:
        Success or error message
    """
    # Grid visibility is a UI setting, not stored in file
    return f"Info: Grid visibility is a UI setting. Use View > Grid in Aseprite."


@mcp.tool()
async def snap_to_grid(filename: str, enabled: bool) -> str:
    """
    Enable/disable snap to grid

    Args:
        filename: Name of the Aseprite file
        enabled: True to enable, False to disable

    Returns:
        Success or error message
    """
    # Snap to grid is a UI setting
    return f"Info: Snap to grid is a UI setting. Use View > Snap to Grid in Aseprite."
