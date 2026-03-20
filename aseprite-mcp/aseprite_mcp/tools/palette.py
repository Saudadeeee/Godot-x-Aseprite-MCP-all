"""Color and palette management for Aseprite MCP"""

from aseprite_mcp import mcp
from aseprite_mcp.utils import validate_color
from aseprite_mcp.utils.lua_templates import sprite_operation_template, execute_lua_with_template


@mcp.tool()
async def create_palette(filename: str, colors: list) -> str:
    """Create a new palette from a list of hex colors"""
    if not colors or len(colors) == 0:
        return "Error: Colors list cannot be empty"

    # Validate all colors
    color_values = []
    for color in colors:
        validated_color = validate_color(color)
        color_values.append(validated_color)

    # Build Lua array string
    colors_lua = ", ".join([f'"{c}"' for c in color_values])

    operation = f"""
    local colors = {{{colors_lua}}}
    local palette = Palette(#colors)

    for i, colorHex in ipairs(colors) do
        palette:setColor(i - 1, Color{{fromString = colorHex}})
    end

    sprite:setPalette(palette)
    print("Success: Created palette with " .. #colors .. " colors")
    """

    return execute_lua_with_template(sprite_operation_template, filename, operation)


@mcp.tool()
async def get_palette_colors(filename: str) -> str:
    """
    Get all colors from the current palette

    Args:
        filename: Name of the Aseprite file

    Returns:
        List of colors in hex format or error message
    """
    if not os.path.exists(filename):
        return f"Error: File '{filename}' not found"

    lua_script = f"""
    local sprite = app.open('{filename}')
    if not sprite then
        print("Error: Failed to open sprite")
        return
    end

    local palette = sprite.palettes[1]
    local colors = {{}}

    for i = 0, #palette - 1 do
        local color = palette:getColor(i)
        local hex = string.format("#%02X%02X%02X", color.red, color.green, color.blue)
        table.insert(colors, hex)
    end

    sprite:close()
    print("Palette colors: " .. table.concat(colors, ", "))
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def add_color_to_palette(filename: str, color: str) -> str:
    """
    Add a color to the current palette

    Args:
        filename: Name of the Aseprite file to modify
        color: Hex color string (e.g., "#FF0000")

    Returns:
        Success or error message
    """
    if not os.path.exists(filename):
        return f"Error: File '{filename}' not found"

    if not color.startswith('#') or len(color) not in [7, 9]:
        return f"Error: Invalid color format '{color}'. Use #RRGGBB format"

    lua_script = f"""
    local sprite = app.open('{filename}')
    if not sprite then
        print("Error: Failed to open sprite")
        return
    end

    local palette = sprite.palettes[1]
    local newSize = #palette + 1
    palette:resize(newSize)
    palette:setColor(newSize - 1, Color{{fromString = "{color}"}})

    sprite:setPalette(palette)
    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Added color {color} to palette (index " .. (newSize - 1) .. ")")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def replace_color(filename: str, old_color: str, new_color: str) -> str:
    """
    Replace all occurrences of a color in the sprite with another color

    Args:
        filename: Name of the Aseprite file to modify
        old_color: Hex color to replace (e.g., "#FF0000")
        new_color: Hex color to replace with (e.g., "#00FF00")

    Returns:
        Success or error message
    """
    if not os.path.exists(filename):
        return f"Error: File '{filename}' not found"

    if not old_color.startswith('#') or len(old_color) not in [7, 9]:
        return f"Error: Invalid old color format. Use #RRGGBB format"

    if not new_color.startswith('#') or len(new_color) not in [7, 9]:
        return f"Error: Invalid new color format. Use #RRGGBB format"

    lua_script = f"""
    local sprite = app.open('{filename}')
    if not sprite then
        print("Error: Failed to open sprite")
        return
    end

    local oldColor = Color{{fromString = "{old_color}"}}
    local newColor = Color{{fromString = "{new_color}"}}
    local pixelsChanged = 0

    app.transaction(function()
        for _, layer in ipairs(sprite.layers) do
            if layer.isImage then
                for _, cel in ipairs(layer.cels) do
                    local image = cel.image
                    for y = 0, image.height - 1 do
                        for x = 0, image.width - 1 do
                            local pixelColor = image:getPixel(x, y)
                            -- Compare RGB values
                            local pc = Color{{rgbaPixel = pixelColor}}
                            if pc.red == oldColor.red and
                               pc.green == oldColor.green and
                               pc.blue == oldColor.blue then
                                image:drawPixel(x, y, newColor.rgbaPixel)
                                pixelsChanged = pixelsChanged + 1
                            end
                        end
                    end
                end
            end
        end
    end)

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Replaced " .. pixelsChanged .. " pixels from {old_color} to {new_color}")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def load_palette_from_file(filename: str, palette_file: str) -> str:
    """
    Load a palette from an external file (.gpl, .ase, .aseprite, .act)

    Args:
        filename: Name of the Aseprite file to modify
        palette_file: Path to the palette file

    Returns:
        Success or error message
    """
    if not os.path.exists(filename):
        return f"Error: File '{filename}' not found"

    if not os.path.exists(palette_file):
        return f"Error: Palette file '{palette_file}' not found"

    # Get absolute paths to avoid path issues
    abs_filename = os.path.abspath(filename)
    abs_palette = os.path.abspath(palette_file)

    lua_script = f"""
    local sprite = app.open('{abs_filename}')
    if not sprite then
        print("Error: Failed to open sprite")
        return
    end

    -- Load palette from file
    local paletteSprite = app.open('{abs_palette}')
    if not paletteSprite then
        print("Error: Failed to load palette file")
        sprite:close()
        return
    end

    local palette = paletteSprite.palettes[1]
    sprite:setPalette(palette)

    paletteSprite:close()
    sprite:saveAs('{abs_filename}')
    sprite:close()
    print("Success: Loaded palette from {palette_file}")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"
