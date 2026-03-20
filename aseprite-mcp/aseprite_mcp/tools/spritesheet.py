"""Sprite sheet export operations for Aseprite MCP"""

from aseprite_mcp import mcp
from aseprite_mcp.core.commands import AsepriteCommand
import os
import json


@mcp.tool()
async def export_sprite_sheet(
    filename: str,
    output: str,
    layout: str = "horizontal",
    padding: int = 0,
    inner_padding: int = 0
) -> str:
    """
    Export sprite sheet with various layouts

    Args:
        filename: Name of the Aseprite file to export
        output: Output file path
        layout: Layout type - "horizontal", "vertical", "packed", "rows", "columns"
        padding: Padding between sprites (pixels)
        inner_padding: Inner padding within each cell (pixels)

    Returns:
        Success or error message
    """
    if not os.path.exists(filename):
        return f"Error: File '{filename}' not found"

    valid_layouts = ["horizontal", "vertical", "packed", "rows", "columns"]
    if layout not in valid_layouts:
        return f"Error: Invalid layout. Valid: {', '.join(valid_layouts)}"

    # Map layout to Aseprite's sheet type
    layout_map = {
        "horizontal": "horizontal",
        "vertical": "vertical",
        "packed": "packed",
        "rows": "rows",
        "columns": "columns"
    }

    abs_output = os.path.abspath(output).replace('\\', '/')

    lua_script = f"""
    local sprite = app.open('{filename}')
    if not sprite then
        print("Error: Failed to open sprite")
        return
    end

    app.command.ExportSpriteSheet{{
        type=SpriteSheetType.{layout_map[layout].upper()},
        textureFilename='{abs_output}',
        borderPadding={padding},
        shapePadding={inner_padding},
        innerPadding={inner_padding}
    }}

    sprite:close()
    print("Success: Exported sprite sheet to {output} ({layout} layout)")
    """

    success, output_result = AsepriteCommand.execute_lua_script(lua_script)
    return output_result if success else f"Error: {output_result}"


@mcp.tool()
async def export_sprite_sheet_with_json(
    filename: str,
    output_image: str,
    output_json: str
) -> str:
    """
    Export sprite sheet with JSON metadata

    Args:
        filename: Name of the Aseprite file to export
        output_image: Output image file path
        output_json: Output JSON metadata file path

    Returns:
        Success or error message
    """
    if not os.path.exists(filename):
        return f"Error: File '{filename}' not found"

    abs_image = os.path.abspath(output_image).replace('\\', '/')
    abs_json = os.path.abspath(output_json).replace('\\', '/')

    lua_script = f"""
    local sprite = app.open('{filename}')
    if not sprite then
        print("Error: Failed to open sprite")
        return
    end

    app.command.ExportSpriteSheet{{
        type=SpriteSheetType.PACKED,
        textureFilename='{abs_image}',
        dataFilename='{abs_json}',
        dataFormat=SpriteSheetDataFormat.JSON_ARRAY,
        borderPadding=0,
        shapePadding=0,
        innerPadding=0,
        listLayers=true,
        listTags=true,
        listSlices=true
    }}

    sprite:close()
    print("Success: Exported sprite sheet with JSON metadata")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def export_layers_separately(filename: str, output_folder: str) -> str:
    """
    Export each layer as a separate file

    Args:
        filename: Name of the Aseprite file to export
        output_folder: Folder to save layer images

    Returns:
        Success or error message
    """
    if not os.path.exists(filename):
        return f"Error: File '{filename}' not found"

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    abs_folder = os.path.abspath(output_folder).replace('\\', '/')

    lua_script = f"""
    local sprite = app.open('{filename}')
    if not sprite then
        print("Error: Failed to open sprite")
        return
    end

    local exportedCount = 0

    for _, layer in ipairs(sprite.layers) do
        if layer.isImage then
            -- Hide all other layers
            for _, l in ipairs(sprite.layers) do
                l.isVisible = false
            end
            layer.isVisible = true

            -- Export this layer
            local layerName = layer.name:gsub("[^%w%-_]", "_")
            local outputPath = '{abs_folder}/' .. layerName .. '.png'

            sprite:saveCopyAs(outputPath)
            exportedCount = exportedCount + 1
        end
    end

    -- Restore visibility
    for _, layer in ipairs(sprite.layers) do
        layer.isVisible = true
    end

    sprite:close()
    print("Success: Exported " .. exportedCount .. " layers to {output_folder}")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def export_frames_separately(filename: str, output_folder: str, prefix: str = "frame") -> str:
    """
    Export each frame as a separate file

    Args:
        filename: Name of the Aseprite file to export
        output_folder: Folder to save frame images
        prefix: Prefix for frame filenames

    Returns:
        Success or error message
    """
    if not os.path.exists(filename):
        return f"Error: File '{filename}' not found"

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    abs_folder = os.path.abspath(output_folder).replace('\\', '/')

    lua_script = f"""
    local sprite = app.open('{filename}')
    if not sprite then
        print("Error: Failed to open sprite")
        return
    end

    local frameCount = #sprite.frames

    for i, frame in ipairs(sprite.frames) do
        app.activeFrame = frame

        -- Format frame number with leading zeros
        local frameNum = string.format("%03d", i)
        local outputPath = '{abs_folder}/{prefix}_' .. frameNum .. '.png'

        sprite:saveCopyAs(outputPath)
    end

    sprite:close()
    print("Success: Exported " .. frameCount .. " frames to {output_folder}")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"
