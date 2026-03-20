"""Selection operations for Aseprite MCP"""

from aseprite_mcp import mcp
from aseprite_mcp.core.commands import AsepriteCommand
import os


@mcp.tool()
async def select_rectangle(filename: str, x: int, y: int, width: int, height: int) -> str:
    """
    Create a rectangular selection

    Args:
        filename: Name of the Aseprite file to modify
        x: X coordinate of top-left corner
        y: Y coordinate of top-left corner
        width: Width of the selection
        height: Height of the selection

    Returns:
        Success or error message
    """
    if not os.path.exists(filename):
        return f"Error: File '{filename}' not found"

    if width <= 0 or height <= 0:
        return f"Error: Width and height must be positive, got width={width}, height={height}"

    lua_script = f"""
    local sprite = app.open('{filename}')
    if not sprite then
        print("Error: Failed to open sprite")
        return
    end

    app.transaction(function()
        sprite.selection:select(Rectangle({x}, {y}, {width}, {height}))
    end)

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Selected rectangle at ({x}, {y}) with size {width}x{height}")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def select_all(filename: str) -> str:
    """
    Select the entire canvas

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

    app.transaction(function()
        sprite.selection:selectAll()
    end)

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Selected entire canvas ({width}x{height})")
        :gsub("{{width}}", tostring(sprite.width))
        :gsub("{{height}}", tostring(sprite.height))
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def deselect(filename: str) -> str:
    """
    Remove all selections (deselect)

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

    app.transaction(function()
        sprite.selection:deselect()
    end)

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Selection cleared")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def invert_selection(filename: str) -> str:
    """
    Invert the current selection (select everything except current selection)

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

    if sprite.selection.isEmpty then
        print("Error: No active selection to invert")
        sprite:close()
        return
    end

    app.transaction(function()
        sprite.selection:invert()
    end)

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Selection inverted")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def delete_selection(filename: str) -> str:
    """
    Delete the content of the current selection (clear to transparent)

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

    if sprite.selection.isEmpty then
        print("Error: No active selection to delete")
        sprite:close()
        return
    end

    local cel = app.activeCel
    if not cel then
        print("Error: No active cel")
        sprite:close()
        return
    end

    app.transaction(function()
        -- Get selection bounds
        local bounds = sprite.selection.bounds
        local image = cel.image

        -- Clear pixels in selection
        for y = bounds.y, bounds.y + bounds.height - 1 do
            for x = bounds.x, bounds.x + bounds.width - 1 do
                if sprite.selection:contains(x, y) then
                    -- Convert to cel local coordinates
                    local localX = x - cel.position.x
                    local localY = y - cel.position.y

                    -- Check if within image bounds
                    if localX >= 0 and localX < image.width and
                       localY >= 0 and localY < image.height then
                        image:clear(Rectangle(localX, localY, 1, 1))
                    end
                end
            end
        end
    end)

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Selection content deleted")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"
