import os
from ..core.commands import AsepriteCommand
from .. import mcp

@mcp.tool()
async def create_canvas(width: int, height: int, filename: str = "canvas.aseprite") -> str:
    """Create a new Aseprite canvas with specified dimensions.

    Args:
        width: Width of the canvas in pixels
        height: Height of the canvas in pixels
        filename: Name of the output file (default: canvas.aseprite)
    """
    script = f"""
    local spr = Sprite({width}, {height})
    spr:saveAs("{filename}")
    return "Canvas created successfully: {filename}"
    """
    
    success, output = AsepriteCommand.execute_lua_script(script)
    
    if success:
        return f"Canvas created successfully: {filename}"
    else:
        return f"Failed to create canvas: {output}"

@mcp.tool()
async def add_layer(filename: str, layer_name: str) -> str:
    """Add a new layer to the Aseprite file.

    Args:
        filename: Name of the Aseprite file to modify
        layer_name: Name of the new layer
    """
    if not os.path.exists(filename):
        return f"File {filename} not found"
    
    script = f"""
    local spr = app.activeSprite
    if not spr then return "No active sprite" end
    
    app.transaction(function()
        spr:newLayer()
        app.activeLayer.name = "{layer_name}"
    end)
    
    spr:saveAs(spr.filename)
    return "Layer added successfully"
    """
    
    success, output = AsepriteCommand.execute_lua_script(script, filename)
    
    if success:
        return f"Layer '{layer_name}' added successfully to {filename}"
    else:
        return f"Failed to add layer: {output}"

@mcp.tool()
async def add_frame(filename: str) -> str:
    """Add a new frame to the Aseprite file.

    Args:
        filename: Name of the Aseprite file to modify
    """
    if not os.path.exists(filename):
        return f"File {filename} not found"
    
    script = """
    local spr = app.activeSprite
    if not spr then return "No active sprite" end
    
    app.transaction(function()
        spr:newFrame()
    end)
    
    spr:saveAs(spr.filename)
    return "Frame added successfully"
    """
    
    success, output = AsepriteCommand.execute_lua_script(script, filename)
    
    if success:
        return f"New frame added successfully to {filename}"
    else:
        return f"Failed to add frame: {output}"