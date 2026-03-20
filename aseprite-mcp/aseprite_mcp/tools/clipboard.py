"""Clipboard operations for Aseprite MCP"""

from aseprite_mcp import mcp
from aseprite_mcp.core.commands import AsepriteCommand
import os


@mcp.tool()
async def copy_to_clipboard(filename: str) -> str:
    """
    Copy selection or entire sprite to clipboard

    Args:
        filename: Name of the Aseprite file

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

    app.command.Copy()

    sprite:close()
    print("Success: Copied to clipboard")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def cut_to_clipboard(filename: str) -> str:
    """
    Cut selection to clipboard

    Args:
        filename: Name of the Aseprite file to modify

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

    app.command.Cut()

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Cut to clipboard")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def paste_from_clipboard(filename: str, x: int = 0, y: int = 0) -> str:
    """
    Paste from clipboard

    Args:
        filename: Name of the Aseprite file to modify
        x: X position to paste at
        y: Y position to paste at

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

    app.command.Paste()

    -- Move pasted content to specified position
    if {x} ~= 0 or {y} ~= 0 then
        local cel = app.activeCel
        if cel then
            cel.position = Point({x}, {y})
        end
    end

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Pasted from clipboard at ({x}, {y})")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def copy_layer(filename: str, layer_name: str) -> str:
    """
    Copy entire layer

    Args:
        filename: Name of the Aseprite file
        layer_name: Name of layer to copy

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

    app.activeLayer = layer
    app.command.SelectAll()
    app.command.Copy()

    sprite:close()
    print("Success: Copied layer '{layer_name}'")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def paste_as_new_layer(filename: str, layer_name: str = "Pasted") -> str:
    """
    Paste clipboard content as new layer

    Args:
        filename: Name of the Aseprite file to modify
        layer_name: Name for the new layer

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

    app.transaction(function()
        local newLayer = sprite:newLayer()
        newLayer.name = '{layer_name}'
        app.activeLayer = newLayer
        app.command.Paste()
    end)

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Pasted as new layer '{layer_name}'")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def merge_layers(filename: str, layer_names: list, result_name: str) -> str:
    """
    Merge multiple layers into one

    Args:
        filename: Name of the Aseprite file to modify
        layer_names: List of layer names to merge
        result_name: Name for the merged layer

    Returns:
        Success or error message
    """
    if not os.path.exists(filename):
        return f"Error: File '{filename}' not found"

    if not layer_names or len(layer_names) < 2:
        return "Error: Need at least 2 layers to merge"

    layers_lua = ", ".join([f'"{name}"' for name in layer_names])

    lua_script = f"""
    local sprite = app.open('{filename}')
    if not sprite then
        print("Error: Failed to open sprite")
        return
    end

    local layerNames = {{{layers_lua}}}
    local layersToMerge = {{}}

    for _, name in ipairs(layerNames) do
        for _, layer in ipairs(sprite.layers) do
            if layer.name == name then
                table.insert(layersToMerge, layer)
                break
            end
        end
    end

    if #layersToMerge < 2 then
        print("Error: Could not find all specified layers")
        sprite:close()
        return
    end

    app.transaction(function()
        -- Select layers and merge
        app.range.layers = layersToMerge
        app.command.MergeDownLayer()

        -- Rename result
        if layersToMerge[1].isVisible then
            layersToMerge[1].name = '{result_name}'
        end
    end)

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Merged {len(layer_names)} layers into '{result_name}'")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"
