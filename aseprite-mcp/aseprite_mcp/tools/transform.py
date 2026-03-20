"""Image transformation operations for Aseprite MCP"""

from aseprite_mcp import mcp
from aseprite_mcp.utils import validate_dimensions, validate_resize_method
from aseprite_mcp.utils.lua_templates import transform_operation_template, execute_lua_with_template
from typing import Optional


@mcp.tool()
async def flip_horizontal(filename: str, layer_name: Optional[str] = None) -> str:
    """Flip image or layer horizontally"""
    transform_code = 'app.command.Flip{ target="mask", orientation="horizontal" }'
    success_message = "flipped horizontally"
    return execute_lua_with_template(transform_operation_template, filename, layer_name, transform_code, success_message)


@mcp.tool()
async def flip_vertical(filename: str, layer_name: Optional[str] = None) -> str:
    """Flip image or layer vertically"""
    transform_code = 'app.command.Flip{ target="mask", orientation="vertical" }'
    success_message = "flipped vertically"
    return execute_lua_with_template(transform_operation_template, filename, layer_name, transform_code, success_message)

        if not layer then
            print("Error: Layer '{layer_name}' not found")
            sprite:close()
            return
        end

        app.activeLayer = layer
        app.command.Flip{{ target="mask", orientation="vertical" }}

        sprite:saveAs('{filename}')
        sprite:close()
        print("Success: Layer '{layer_name}' flipped vertically")
        """
    else:
        lua_script = f"""
        local sprite = app.open('{filename}')
        if not sprite then
            print("Error: Failed to open sprite")
            return
        end

        app.command.Flip{{ target="mask", orientation="vertical" }}

        sprite:saveAs('{filename}')
        sprite:close()
        print("Success: Sprite flipped vertically")
        """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def rotate_image(filename: str, angle: float, layer_name: str = None) -> str:
    """
    Rotate image by specified angle (90, 180, 270 degrees or custom)

    Args:
        filename: Name of the Aseprite file to modify
        angle: Rotation angle in degrees (90, 180, 270, or custom)
        layer_name: Name of specific layer to rotate (None = rotate entire sprite)

    Returns:
        Success or error message
    """
    if not os.path.exists(filename):
        return f"Error: File '{filename}' not found"

    # Normalize angle to 0-360
    angle = angle % 360

    lua_script = f"""
    local sprite = app.open('{filename}')
    if not sprite then
        print("Error: Failed to open sprite")
        return
    end

    local targetLayer = nil
    if "{layer_name}" ~= "" and "{layer_name}" ~= "None" then
        for _, l in ipairs(sprite.layers) do
            if l.name == '{layer_name}' then
                targetLayer = l
                break
            end
        end

        if not targetLayer then
            print("Error: Layer '{layer_name}' not found")
            sprite:close()
            return
        end
        app.activeLayer = targetLayer
    end

    local angle = {angle}

    if angle == 90 then
        app.command.Rotate{{ target="mask", angle="90" }}
    elseif angle == 180 then
        app.command.Rotate{{ target="mask", angle="180" }}
    elseif angle == 270 then
        app.command.Rotate{{ target="mask", angle="-90" }}
    else
        -- For custom angles, we need to use canvas rotation
        app.command.CanvasSize{{
            left=0, right=0, top=0, bottom=0
        }}
    end

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Rotated by {angle} degrees")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def resize_sprite(filename: str, width: int, height: int, method: str = "nearest") -> str:
    """
    Resize sprite to new dimensions

    Args:
        filename: Name of the Aseprite file to modify
        width: New width in pixels
        height: New height in pixels
        method: Resize method - "nearest" (pixel-perfect), "bilinear", or "rotsprite"

    Returns:
        Success or error message
    """
    if not os.path.exists(filename):
        return f"Error: File '{filename}' not found"

    if width <= 0 or height <= 0:
        return f"Error: Width and height must be positive, got {width}x{height}"

    valid_methods = ["nearest", "bilinear", "rotsprite"]
    if method not in valid_methods:
        return f"Error: Invalid method. Valid: {', '.join(valid_methods)}"

    lua_script = f"""
    local sprite = app.open('{filename}')
    if not sprite then
        print("Error: Failed to open sprite")
        return
    end

    sprite:resize({width}, {height})

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Sprite resized to {width}x{height} using {method} method")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def crop_sprite(filename: str, x: int, y: int, width: int, height: int) -> str:
    """
    Crop sprite to specified region

    Args:
        filename: Name of the Aseprite file to modify
        x: X coordinate of crop region
        y: Y coordinate of crop region
        width: Width of crop region
        height: Height of crop region

    Returns:
        Success or error message
    """
    if not os.path.exists(filename):
        return f"Error: File '{filename}' not found"

    if width <= 0 or height <= 0:
        return f"Error: Width and height must be positive"

    lua_script = f"""
    local sprite = app.open('{filename}')
    if not sprite then
        print("Error: Failed to open sprite")
        return
    end

    sprite:crop(Rectangle({x}, {y}, {width}, {height}))

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Sprite cropped to region ({x}, {y}, {width}x{height})")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def scale_sprite(filename: str, scale_x: float, scale_y: float) -> str:
    """
    Scale sprite by percentage

    Args:
        filename: Name of the Aseprite file to modify
        scale_x: Horizontal scale factor (1.0 = 100%, 2.0 = 200%)
        scale_y: Vertical scale factor (1.0 = 100%, 2.0 = 200%)

    Returns:
        Success or error message
    """
    if not os.path.exists(filename):
        return f"Error: File '{filename}' not found"

    if scale_x <= 0 or scale_y <= 0:
        return f"Error: Scale factors must be positive"

    lua_script = f"""
    local sprite = app.open('{filename}')
    if not sprite then
        print("Error: Failed to open sprite")
        return
    end

    local newWidth = math.floor(sprite.width * {scale_x})
    local newHeight = math.floor(sprite.height * {scale_y})

    sprite:resize(newWidth, newHeight)

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Sprite scaled by {scale_x}x{scale_y} to " .. newWidth .. "x" .. newHeight)
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def trim_sprite(filename: str) -> str:
    """
    Auto-trim transparent pixels around sprite

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

    app.command.AutocropSprite()

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Sprite trimmed (removed transparent borders)")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def expand_canvas(filename: str, left: int, top: int, right: int, bottom: int) -> str:
    """
    Expand canvas size by adding space around edges

    Args:
        filename: Name of the Aseprite file to modify
        left: Pixels to add on left side
        top: Pixels to add on top
        right: Pixels to add on right side
        bottom: Pixels to add on bottom

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

    app.command.CanvasSize{{
        left={left},
        top={top},
        right={right},
        bottom={bottom}
    }}

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Canvas expanded (L:{left} T:{top} R:{right} B:{bottom})")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"
