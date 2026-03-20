import os
from typing import List, Dict, Any
from ..core.commands import AsepriteCommand
from .. import mcp

@mcp.tool()
async def draw_pixels(filename: str, pixels: List[Dict[str, Any]]) -> str:
    """Draw pixels on the canvas with specified colors.

    Args:
        filename: Name of the Aseprite file to modify
        pixels: List of pixel data, each containing:
            {"x": int, "y": int, "color": str}
            where color is a hex code like "#FF0000"
    """
    if not os.path.exists(filename):
        return f"File {filename} not found"

    script = """
    local spr = app.activeSprite
    if not spr then return "No active sprite" end
    
    app.transaction(function()
        local cel = app.activeCel
        if not cel then
            -- If no active cel, create one
            app.activeLayer = spr.layers[1]
            app.activeFrame = spr.frames[1]
            cel = app.activeCel
            if not cel then
                return "No active cel and couldn't create one"
            end
        end
        
        local img = cel.image
    """
    
    # Add pixel drawing commands
    for pixel in pixels:
        x = pixel.get("x", 0)
        y = pixel.get("y", 0)
        color = pixel.get("color", "#000000")
        # Convert hex to RGB
        color = color.lstrip("#")
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
        
        script += f"""
        img:putPixel({x}, {y}, Color({r}, {g}, {b}, 255))
        """
    
    script += """
    end)
    
    spr:saveAs(spr.filename)
    return "Pixels drawn successfully"
    """
    
    success, output = AsepriteCommand.execute_lua_script(script, filename)
    
    if success:
        return f"Pixels drawn successfully in {filename}"
    else:
        return f"Failed to draw pixels: {output}"

@mcp.tool()
async def draw_line(filename: str, x1: int, y1: int, x2: int, y2: int, color: str = "#000000", thickness: int = 1) -> str:
    """Draw a line on the canvas.

    Args:
        filename: Name of the Aseprite file to modify
        x1: Starting x coordinate
        y1: Starting y coordinate
        x2: Ending x coordinate
        y2: Ending y coordinate
        color: Hex color code (default: "#000000")
        thickness: Line thickness in pixels (default: 1)
    """
    if not os.path.exists(filename):
        return f"File {filename} not found"
    
    # Convert hex to RGB
    color = color.lstrip("#")
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    
    script = f"""
    local spr = app.activeSprite
    if not spr then return "No active sprite" end
    
    app.transaction(function()
        local cel = app.activeCel
        if not cel then
            app.activeLayer = spr.layers[1]
            app.activeFrame = spr.frames[1]
            cel = app.activeCel
            if not cel then
                return "No active cel and couldn't create one"
            end
        end
        
        local color = Color({r}, {g}, {b}, 255)
        local brush = Brush()
        brush.size = {thickness}
        app.useTool({{
            tool="line",
            color=color,
            brush=brush,
            points={{Point({x1}, {y1}), Point({x2}, {y2})}}
        }})
    end)
    
    spr:saveAs(spr.filename)
    return "Line drawn successfully"
    """
    
    success, output = AsepriteCommand.execute_lua_script(script, filename)
    
    if success:
        return f"Line drawn successfully in {filename}"
    else:
        return f"Failed to draw line: {output}"

@mcp.tool()
async def draw_rectangle(filename: str, x: int, y: int, width: int, height: int, color: str = "#000000", fill: bool = False) -> str:
    """Draw a rectangle on the canvas.

    Args:
        filename: Name of the Aseprite file to modify
        x: Top-left x coordinate
        y: Top-left y coordinate
        width: Width of the rectangle
        height: Height of the rectangle
        color: Hex color code (default: "#000000")
        fill: Whether to fill the rectangle (default: False)
    """
    if not os.path.exists(filename):
        return f"File {filename} not found"
    
    # Convert hex to RGB
    color = color.lstrip("#")
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    
    script = f"""
    local spr = app.activeSprite
    if not spr then return "No active sprite" end
    
    app.transaction(function()
        local cel = app.activeCel
        if not cel then
            app.activeLayer = spr.layers[1]
            app.activeFrame = spr.frames[1]
            cel = app.activeCel
            if not cel then
                return "No active cel and couldn't create one"
            end
        end
        
        local color = Color({r}, {g}, {b}, 255)
        local tool = {'"rectangle"' if not fill else '"filled_rectangle"'}
        app.useTool({{
            tool=tool,
            color=color,
            points={{Point({x}, {y}), Point({x + width}, {y + height})}}
        }})
    end)
    
    spr:saveAs(spr.filename)
    return "Rectangle drawn successfully"
    """
    
    success, output = AsepriteCommand.execute_lua_script(script, filename)
    
    if success:
        return f"Rectangle drawn successfully in {filename}"
    else:
        return f"Failed to draw rectangle: {output}"

@mcp.tool()
async def fill_area(filename: str, x: int, y: int, color: str = "#000000") -> str:
    """Fill an area with color using the paint bucket tool.

    Args:
        filename: Name of the Aseprite file to modify
        x: X coordinate to fill from
        y: Y coordinate to fill from
        color: Hex color code (default: "#000000")
    """
    if not os.path.exists(filename):
        return f"File {filename} not found"
    
    # Convert hex to RGB
    color = color.lstrip("#")
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    
    script = f"""
    local spr = app.activeSprite
    if not spr then return "No active sprite" end
    
    app.transaction(function()
        local cel = app.activeCel
        if not cel then
            app.activeLayer = spr.layers[1]
            app.activeFrame = spr.frames[1]
            cel = app.activeCel
            if not cel then
                return "No active cel and couldn't create one"
            end
        end
        
        local color = Color({r}, {g}, {b}, 255)
        app.useTool({{
            tool="paint_bucket",
            color=color,
            points={{Point({x}, {y})}}
        }})
    end)
    
    spr:saveAs(spr.filename)
    return "Area filled successfully"
    """
    
    success, output = AsepriteCommand.execute_lua_script(script, filename)
    
    if success:
        return f"Area filled successfully in {filename}"
    else:
        return f"Failed to fill area: {output}"

@mcp.tool()
async def draw_circle(filename: str, center_x: int, center_y: int, radius: int, color: str = "#000000", fill: bool = False) -> str:
    """Draw a circle on the canvas.

    Args:
        filename: Name of the Aseprite file to modify
        center_x: X coordinate of circle center
        center_y: Y coordinate of circle center
        radius: Radius of the circle in pixels
        color: Hex color code (default: "#000000")
        fill: Whether to fill the circle (default: False)
    """
    if not os.path.exists(filename):
        return f"File {filename} not found"
    
    # Convert hex to RGB
    color = color.lstrip("#")
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    
    script = f"""
    local spr = app.activeSprite
    if not spr then return "No active sprite" end
    
    app.transaction(function()
        local cel = app.activeCel
        if not cel then
            app.activeLayer = spr.layers[1]
            app.activeFrame = spr.frames[1]
            cel = app.activeCel
            if not cel then
                return "No active cel and couldn't create one"
            end
        end
        
        local color = Color({r}, {g}, {b}, 255)
        local tool = {'"ellipse"' if not fill else '"filled_ellipse"'}
        app.useTool({{
            tool=tool,
            color=color,
            points={{
                Point({center_x - radius}, {center_y - radius}),
                Point({center_x + radius}, {center_y + radius})
            }}
        }})
    end)
    
    spr:saveAs(spr.filename)
    return "Circle drawn successfully"
    """
    
    success, output = AsepriteCommand.execute_lua_script(script, filename)
    
    if success:
        return f"Circle drawn successfully in {filename}"
    else:
        return f"Failed to draw circle: {output}"
    