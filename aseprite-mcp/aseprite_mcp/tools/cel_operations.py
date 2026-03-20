"""Cel operations for Aseprite MCP"""

from aseprite_mcp import mcp
from aseprite_mcp.core.commands import AsepriteCommand
import os


@mcp.tool()
async def move_cel(filename: str, layer_name: str, frame_number: int, x: int, y: int) -> str:
    """
    Move cel to a new position

    Args:
        filename: Name of the Aseprite file to modify
        layer_name: Name of the layer containing the cel
        frame_number: Frame number (1-based)
        x: New X position
        y: New Y position

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

    local layer = nil
    for _, l in ipairs(sprite.layers) do
        if l.name == '{layer_name}' then
            layer = l
            break
        end
    end

    if not layer then
        print("Error: Layer '{layer_name}' not found")
        sprite:close()
        return
    end

    local frameNum = {frame_number}
    if frameNum < 1 or frameNum > #sprite.frames then
        print("Error: Frame number out of range (1-" .. #sprite.frames .. ")")
        sprite:close()
        return
    end

    local cel = layer:cel(frameNum)
    if not cel then
        print("Error: No cel at frame " .. frameNum)
        sprite:close()
        return
    end

    app.transaction(function()
        cel.position = Point({x}, {y})
    end)

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Moved cel to position ({x}, {y})")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def copy_cel(filename: str, src_layer: str, src_frame: int,
                  dst_layer: str, dst_frame: int) -> str:
    """
    Copy cel from one layer/frame to another

    Args:
        filename: Name of the Aseprite file to modify
        src_layer: Source layer name
        src_frame: Source frame number (1-based)
        dst_layer: Destination layer name
        dst_frame: Destination frame number (1-based)

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

    local srcLayer, dstLayer = nil, nil
    for _, l in ipairs(sprite.layers) do
        if l.name == '{src_layer}' then srcLayer = l end
        if l.name == '{dst_layer}' then dstLayer = l end
    end

    if not srcLayer then
        print("Error: Source layer '{src_layer}' not found")
        sprite:close()
        return
    end

    if not dstLayer then
        print("Error: Destination layer '{dst_layer}' not found")
        sprite:close()
        return
    end

    local srcCel = srcLayer:cel({src_frame})
    if not srcCel then
        print("Error: No cel at source frame {src_frame}")
        sprite:close()
        return
    end

    app.transaction(function()
        -- Copy image data
        local newImage = Image(srcCel.image)
        sprite:newCel(dstLayer, {dst_frame}, newImage, srcCel.position)
    end)

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Copied cel from {src_layer}:{src_frame} to {dst_layer}:{dst_frame}")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def link_cel(filename: str, layer_name: str, frame_number: int, target_frame: int) -> str:
    """
    Link cel to share content between frames

    Args:
        filename: Name of the Aseprite file to modify
        layer_name: Layer name
        frame_number: Frame to link from (1-based)
        target_frame: Frame to link to (1-based)

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

    local layer = nil
    for _, l in ipairs(sprite.layers) do
        if l.name == '{layer_name}' then
            layer = l
            break
        end
    end

    if not layer then
        print("Error: Layer '{layer_name}' not found")
        sprite:close()
        return
    end

    local sourceCel = layer:cel({frame_number})
    if not sourceCel then
        print("Error: No cel at frame {frame_number}")
        sprite:close()
        return
    end

    app.transaction(function()
        -- Create linked cel
        sprite:newCel(layer, {target_frame}, sourceCel.image, sourceCel.position)
    end)

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Linked cel from frame {frame_number} to frame {target_frame}")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def set_cel_opacity(filename: str, layer_name: str, frame_number: int, opacity: int) -> str:
    """
    Set opacity of a specific cel

    Args:
        filename: Name of the Aseprite file to modify
        layer_name: Layer name
        frame_number: Frame number (1-based)
        opacity: Opacity value (0-255)

    Returns:
        Success or error message
    """
    if not os.path.exists(filename):
        return f"Error: File '{filename}' not found"

    if opacity < 0 or opacity > 255:
        return f"Error: Opacity must be 0-255, got {opacity}"

    lua_script = f"""
    local sprite = app.open('{filename}')
    if not sprite then
        print("Error: Failed to open sprite")
        return
    end

    local layer = nil
    for _, l in ipairs(sprite.layers) do
        if l.name == '{layer_name}' then
            layer = l
            break
        end
    end

    if not layer then
        print("Error: Layer '{layer_name}' not found")
        sprite:close()
        return
    end

    local cel = layer:cel({frame_number})
    if not cel then
        print("Error: No cel at frame {frame_number}")
        sprite:close()
        return
    end

    app.transaction(function()
        cel.opacity = {opacity}
    end)

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Set cel opacity to {opacity}")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def clear_cel(filename: str, layer_name: str, frame_number: int) -> str:
    """
    Clear content of a cel (make it transparent)

    Args:
        filename: Name of the Aseprite file to modify
        layer_name: Layer name
        frame_number: Frame number (1-based)

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

    local layer = nil
    for _, l in ipairs(sprite.layers) do
        if l.name == '{layer_name}' then
            layer = l
            break
        end
    end

    if not layer then
        print("Error: Layer '{layer_name}' not found")
        sprite:close()
        return
    end

    local cel = layer:cel({frame_number})
    if not cel then
        print("Error: No cel at frame {frame_number}")
        sprite:close()
        return
    end

    app.transaction(function()
        cel.image:clear()
    end)

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Cleared cel content")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"
