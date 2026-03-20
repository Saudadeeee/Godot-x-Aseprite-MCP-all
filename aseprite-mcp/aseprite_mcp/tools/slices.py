"""Slices and 9-patch support for Aseprite MCP"""

from aseprite_mcp import mcp
from aseprite_mcp.core.commands import AsepriteCommand
import os


@mcp.tool()
async def create_slice(filename: str, name: str, x: int, y: int, width: int, height: int) -> str:
    """
    Create a slice region

    Args:
        filename: Name of the Aseprite file to modify
        name: Name for the slice
        x: X coordinate
        y: Y coordinate
        width: Width
        height: Height

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

    local slice = sprite:newSlice(Rectangle({x}, {y}, {width}, {height}))
    slice.name = '{name}'

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Created slice '{name}' at ({x},{y}) {width}x{height}")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def create_nine_patch_slice(filename: str, name: str, bounds: dict, center: dict) -> str:
    """
    Create 9-patch slice for UI scaling

    Args:
        filename: Name of the Aseprite file
        name: Name for the slice
        bounds: Dict with x, y, width, height
        center: Dict with x, y, width, height for center region

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

    local slice = sprite:newSlice(Rectangle({bounds['x']}, {bounds['y']}, {bounds['width']}, {bounds['height']}))
    slice.name = '{name}'
    slice.center = Rectangle({center['x']}, {center['y']}, {center['width']}, {center['height']})

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Created 9-patch slice '{name}'")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def list_slices(filename: str) -> str:
    """List all slices in sprite"""
    if not os.path.exists(filename):
        return f"Error: File '{filename}' not found"

    lua_script = f"""
    local sprite = app.open('{filename}')
    if not sprite then
        print("Error: Failed to open sprite")
        return
    end

    local sliceNames = {{}}
    for _, slice in ipairs(sprite.slices) do
        table.insert(sliceNames, slice.name)
    end

    sprite:close()
    print("Slices: " .. table.concat(sliceNames, ", "))
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def export_slices(filename: str, output_folder: str) -> str:
    """Export all slices as separate files"""
    if not os.path.exists(filename):
        return f"Error: File '{filename}' not found"

    os.makedirs(output_folder, exist_ok=True)
    abs_folder = os.path.abspath(output_folder).replace('\\', '/')

    lua_script = f"""
    local sprite = app.open('{filename}')
    if not sprite then
        print("Error: Failed to open sprite")
        return
    end

    app.command.ExportSpriteSheet{{
        type=SpriteSheetType.PACKED,
        textureFilename='{abs_folder}/slices.png',
        listSlices=true
    }}

    sprite:close()
    print("Success: Exported slices to {output_folder}")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"
