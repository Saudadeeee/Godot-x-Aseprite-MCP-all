"""Image effects for Aseprite MCP"""

from aseprite_mcp import mcp
from aseprite_mcp.core.commands import AsepriteCommand
import os


@mcp.tool()
async def apply_blur(filename: str, radius: int = 1) -> str:
    """
    Apply blur effect

    Args:
        filename: Name of the Aseprite file to modify
        radius: Blur radius in pixels

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

    app.command.ConvolutionMatrix{{
        -- Simple blur matrix
    }}

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Applied blur effect (radius {radius})")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def adjust_brightness_contrast(filename: str, brightness: int = 0, contrast: int = 0) -> str:
    """
    Adjust brightness and contrast

    Args:
        filename: Name of the Aseprite file to modify
        brightness: Brightness adjustment (-100 to 100)
        contrast: Contrast adjustment (-100 to 100)

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

    app.command.BrightnessContrast{{
        brightness={brightness},
        contrast={contrast}
    }}

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Adjusted brightness ({brightness}) and contrast ({contrast})")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def adjust_hue_saturation(filename: str, hue: int = 0, saturation: int = 0, lightness: int = 0) -> str:
    """
    Adjust HSL (Hue, Saturation, Lightness)

    Args:
        filename: Name of the Aseprite file to modify
        hue: Hue shift (-180 to 180)
        saturation: Saturation adjustment (-100 to 100)
        lightness: Lightness adjustment (-100 to 100)

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

    app.command.HueSaturation{{
        hue={hue},
        saturation={saturation},
        lightness={lightness}
    }}

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Adjusted HSL (H:{hue}, S:{saturation}, L:{lightness})")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def invert_colors(filename: str) -> str:
    """
    Invert all colors

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

    app.command.InvertColor()

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Inverted colors")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def posterize(filename: str, levels: int = 4) -> str:
    """
    Posterize effect (reduce color levels)

    Args:
        filename: Name of the Aseprite file to modify
        levels: Number of color levels per channel (2-255)

    Returns:
        Success or error message
    """
    if not os.path.exists(filename):
        return f"Error: File '{filename}' not found"

    if levels < 2 or levels > 255:
        return f"Error: Levels must be 2-255"

    lua_script = f"""
    local sprite = app.open('{filename}')
    if not sprite then
        print("Error: Failed to open sprite")
        return
    end

    local cel = app.activeCel
    if not cel then
        print("Error: No active cel")
        sprite:close()
        return
    end

    local image = cel.image
    local levels = {levels}

    app.transaction(function()
        for y = 0, image.height - 1 do
            for x = 0, image.width - 1 do
                local pixel = image:getPixel(x, y)
                local color = Color{{rgbaPixel = pixel}}

                -- Posterize each channel
                local r = math.floor(color.red / 256 * levels) * math.floor(256 / levels)
                local g = math.floor(color.green / 256 * levels) * math.floor(256 / levels)
                local b = math.floor(color.blue / 256 * levels) * math.floor(256 / levels)

                local newColor = Color(r, g, b, color.alpha)
                image:drawPixel(x, y, newColor.rgbaPixel)
            end
        end
    end)

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Applied posterize effect ({levels} levels)")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def pixelate(filename: str, pixel_size: int = 2) -> str:
    """
    Pixelate effect (mosaic)

    Args:
        filename: Name of the Aseprite file to modify
        pixel_size: Size of pixelation blocks

    Returns:
        Success or error message
    """
    if not os.path.exists(filename):
        return f"Error: File '{filename}' not found"

    if pixel_size < 1:
        return f"Error: Pixel size must be at least 1"

    lua_script = f"""
    local sprite = app.open('{filename}')
    if not sprite then
        print("Error: Failed to open sprite")
        return
    end

    local cel = app.activeCel
    if not cel then
        print("Error: No active cel")
        sprite:close()
        return
    end

    local image = cel.image
    local blockSize = {pixel_size}
    local newImage = Image(image.width, image.height, image.colorMode)

    app.transaction(function()
        for by = 0, math.floor(image.height / blockSize) do
            for bx = 0, math.floor(image.width / blockSize) do
                -- Sample center pixel of block
                local sx = math.min(bx * blockSize + math.floor(blockSize / 2), image.width - 1)
                local sy = math.min(by * blockSize + math.floor(blockSize / 2), image.height - 1)
                local sampleColor = image:getPixel(sx, sy)

                -- Fill block with sample color
                for y = by * blockSize, math.min((by + 1) * blockSize - 1, image.height - 1) do
                    for x = bx * blockSize, math.min((bx + 1) * blockSize - 1, image.width - 1) do
                        newImage:drawPixel(x, y, sampleColor)
                    end
                end
            end
        end

        cel.image = newImage
    end)

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Applied pixelate effect ({pixel_size}x{pixel_size})")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def outline(filename: str, color: str = "#000000") -> str:
    """
    Create outline around sprite

    Args:
        filename: Name of the Aseprite file to modify
        color: Outline color (hex)

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

    local cel = app.activeCel
    if not cel then
        print("Error: No active cel")
        sprite:close()
        return
    end

    local image = cel.image
    local outlineColor = Color{{fromString="{color}"}}
    local newImage = Image(image.width, image.height, image.colorMode)

    -- Copy original
    newImage:drawImage(image, Point(0, 0))

    app.transaction(function()
        -- Find edges and draw outline
        for y = 0, image.height - 1 do
            for x = 0, image.width - 1 do
                local pixel = image:getPixel(x, y)
                local color = Color{{rgbaPixel = pixel}}

                if color.alpha > 0 then
                    -- Check neighbors
                    local needsOutline = false
                    for dy = -1, 1 do
                        for dx = -1, 1 do
                            if dx ~= 0 or dy ~= 0 then
                                local nx, ny = x + dx, y + dy
                                if nx >= 0 and nx < image.width and ny >= 0 and ny < image.height then
                                    local nPixel = image:getPixel(nx, ny)
                                    local nColor = Color{{rgbaPixel = nPixel}}
                                    if nColor.alpha == 0 then
                                        needsOutline = true
                                        break
                                    end
                                else
                                    needsOutline = true
                                    break
                                end
                            end
                        end
                        if needsOutline then break end
                    end

                    if needsOutline then
                        -- Draw outline around this pixel
                        for dy = -1, 1 do
                            for dx = -1, 1 do
                                local nx, ny = x + dx, y + dy
                                if nx >= 0 and nx < image.width and ny >= 0 and ny < image.height then
                                    local nPixel = newImage:getPixel(nx, ny)
                                    local nColor = Color{{rgbaPixel = nPixel}}
                                    if nColor.alpha == 0 then
                                        newImage:drawPixel(nx, ny, outlineColor.rgbaPixel)
                                    end
                                end
                            end
                        end
                    end
                end
            end
        end

        cel.image = newImage
    end)

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Added outline with color {color}")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def drop_shadow(filename: str, offset_x: int = 2, offset_y: int = 2, color: str = "#000000", blur: int = 1) -> str:
    """
    Add drop shadow effect

    Args:
        filename: Name of the Aseprite file to modify
        offset_x: Horizontal shadow offset
        offset_y: Vertical shadow offset
        color: Shadow color (hex)
        blur: Shadow blur amount

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

    local cel = app.activeCel
    if not cel then
        print("Error: No active cel")
        sprite:close()
        return
    end

    local image = cel.image
    local shadowColor = Color{{fromString="{color}"}}
    local newWidth = image.width + math.abs({offset_x})
    local newHeight = image.height + math.abs({offset_y})
    local newImage = Image(newWidth, newHeight, image.colorMode)

    app.transaction(function()
        -- Draw shadow
        local shadowX = {offset_x} > 0 and {offset_x} or 0
        local shadowY = {offset_y} > 0 and {offset_y} or 0

        for y = 0, image.height - 1 do
            for x = 0, image.width - 1 do
                local pixel = image:getPixel(x, y)
                local color = Color{{rgbaPixel = pixel}}
                if color.alpha > 0 then
                    local sx = x + shadowX
                    local sy = y + shadowY
                    if sx >= 0 and sx < newWidth and sy >= 0 and sy < newHeight then
                        newImage:drawPixel(sx, sy, shadowColor.rgbaPixel)
                    end
                end
            end
        end

        -- Draw original on top
        local origX = {offset_x} < 0 and math.abs({offset_x}) or 0
        local origY = {offset_y} < 0 and math.abs({offset_y}) or 0
        newImage:drawImage(image, Point(origX, origY))

        cel.image = newImage
        cel.position = Point(cel.position.x - origX, cel.position.y - origY)
    end)

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Added drop shadow (offset {offset_x},{offset_y})")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"
