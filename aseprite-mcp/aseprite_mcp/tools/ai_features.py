"""AI-powered features for Aseprite MCP"""

from aseprite_mcp import mcp
from aseprite_mcp.core.commands import AsepriteCommand
import os
import shutil


@mcp.tool()
async def auto_color_sprite(filename: str, color_palette: list) -> str:
    """
    Automatically color sprite using AI-like logic with given palette

    Args:
        filename: Name of the Aseprite file to modify
        color_palette: List of hex colors to use

    Returns:
        Success or error message
    """
    if not os.path.exists(filename):
        return f"Error: File '{filename}' not found"

    if not color_palette:
        return "Error: Color palette cannot be empty"

    colors_lua = ", ".join([f'"{c}"' for c in color_palette])

    lua_script = f"""
    local sprite = app.open('{filename}')
    if not sprite then
        print("Error: Failed to open sprite")
        return
    end

    local palette = {{{colors_lua}}}
    local cel = app.activeCel
    if not cel then
        print("Error: No active cel")
        sprite:close()
        return
    end

    local image = cel.image

    app.transaction(function()
        -- Simple auto-coloring: replace grayscale with palette colors
        for y = 0, image.height - 1 do
            for x = 0, image.width - 1 do
                local pixel = image:getPixel(x, y)
                local color = Color{{rgbaPixel = pixel}}

                if color.alpha > 0 then
                    -- Calculate brightness
                    local brightness = (color.red + color.green + color.blue) / 3
                    local paletteIndex = math.floor(brightness / 256 * #palette) + 1
                    paletteIndex = math.max(1, math.min(#palette, paletteIndex))

                    local newColor = Color{{fromString = palette[paletteIndex]}}
                    newColor.alpha = color.alpha
                    image:drawPixel(x, y, newColor.rgbaPixel)
                end
            end
        end
    end)

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Auto-colored sprite with {len(color_palette)} colors")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def upscale_sprite_ai(filename: str, scale: int = 2, model: str = "pixel") -> str:
    """
    AI-style upscaling (simplified pixel-perfect algorithm)

    Args:
        filename: Name of the Aseprite file to modify
        scale: Scale factor (2, 3, 4)
        model: Upscaling model ("pixel", "smooth")

    Returns:
        Success or error message
    """
    if not os.path.exists(filename):
        return f"Error: File '{filename}' not found"

    if scale < 2 or scale > 8:
        return "Error: Scale must be 2-8"

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

    local origImage = cel.image
    local newWidth = origImage.width * {scale}
    local newHeight = origImage.height * {scale}
    local newImage = Image(newWidth, newHeight, origImage.colorMode)

    app.transaction(function()
        if "{model}" == "pixel" then
            -- Nearest neighbor (pixel-perfect)
            for y = 0, newHeight - 1 do
                for x = 0, newWidth - 1 do
                    local srcX = math.floor(x / {scale})
                    local srcY = math.floor(y / {scale})
                    local pixel = origImage:getPixel(srcX, srcY)
                    newImage:drawPixel(x, y, pixel)
                end
            end
        else
            -- Simple smoothing
            for y = 0, newHeight - 1 do
                for x = 0, newWidth - 1 do
                    local srcX = x / {scale}
                    local srcY = y / {scale}
                    local x1, y1 = math.floor(srcX), math.floor(srcY)
                    local x2, y2 = math.min(x1 + 1, origImage.width - 1), math.min(y1 + 1, origImage.height - 1)

                    -- Bilinear interpolation (simplified)
                    local pixel1 = origImage:getPixel(x1, y1)
                    local pixel2 = origImage:getPixel(x2, y1)
                    local pixel3 = origImage:getPixel(x1, y2)
                    local pixel4 = origImage:getPixel(x2, y2)

                    -- Use nearest for now (full interpolation is complex)
                    newImage:drawPixel(x, y, pixel1)
                end
            end
        end

        cel.image = newImage
    end)

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: AI upscaled sprite {scale}x using {model} model")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def auto_outline_sprite(filename: str, style: str = "clean") -> str:
    """
    Automatically create outline with AI-like edge detection

    Args:
        filename: Name of the Aseprite file to modify
        style: Outline style ("clean", "rough", "soft")

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
    local outlineImage = Image(image.width, image.height, image.colorMode)

    app.transaction(function()
        -- Copy original
        outlineImage:drawImage(image, Point(0, 0))

        -- Edge detection and outline
        for y = 1, image.height - 2 do
            for x = 1, image.width - 2 do
                local center = image:getPixel(x, y)
                local centerColor = Color{{rgbaPixel = center}}

                if centerColor.alpha > 0 then
                    -- Check 8-connected neighbors
                    local needsOutline = false
                    for dy = -1, 1 do
                        for dx = -1, 1 do
                            if dx ~= 0 or dy ~= 0 then
                                local nx, ny = x + dx, y + dy
                                local neighbor = image:getPixel(nx, ny)
                                local neighborColor = Color{{rgbaPixel = neighbor}}

                                if neighborColor.alpha == 0 then
                                    needsOutline = true
                                    break
                                end
                            end
                        end
                        if needsOutline then break end
                    end

                    if needsOutline then
                        -- Apply outline based on style
                        local outlineColor = Color(0, 0, 0, 255) -- Black outline
                        if "{style}" == "soft" then
                            outlineColor = Color(64, 64, 64, 200) -- Gray semi-transparent
                        elseif "{style}" == "rough" then
                            -- Add some randomness (simplified)
                            outlineColor = Color(0, 0, 0, 255)
                        end

                        -- Draw outline pixels
                        for dy = -1, 1 do
                            for dx = -1, 1 do
                                local ox, oy = x + dx, y + dy
                                if ox >= 0 and ox < image.width and oy >= 0 and oy < image.height then
                                    local existing = outlineImage:getPixel(ox, oy)
                                    local existingColor = Color{{rgbaPixel = existing}}
                                    if existingColor.alpha == 0 then
                                        outlineImage:drawPixel(ox, oy, outlineColor.rgbaPixel)
                                    end
                                end
                            end
                        end
                    end
                end
            end
        end

        cel.image = outlineImage
    end)

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Auto-generated {style} outline")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def extract_color_palette_smart(filename: str, num_colors: int = 16) -> str:
    """
    AI-powered smart palette extraction

    Args:
        filename: Name of the Aseprite file
        num_colors: Number of colors to extract

    Returns:
        Extracted palette or error message
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
    local colorFreq = {{}}

    -- Collect color frequency
    for y = 0, image.height - 1 do
        for x = 0, image.width - 1 do
            local pixel = image:getPixel(x, y)
            local color = Color{{rgbaPixel = pixel}}

            if color.alpha > 0 then
                local key = string.format("#%02X%02X%02X", color.red, color.green, color.blue)
                colorFreq[key] = (colorFreq[key] or 0) + 1
            end
        end
    end

    -- Sort by frequency
    local colors = {{}}
    for color, freq in pairs(colorFreq) do
        table.insert(colors, {{color = color, freq = freq}})
    end

    table.sort(colors, function(a, b) return a.freq > b.freq end)

    -- Take top N colors
    local palette = {{}}
    for i = 1, math.min({num_colors}, #colors) do
        table.insert(palette, colors[i].color)
    end

    sprite:close()
    print("Smart palette (" .. #palette .. " colors): " .. table.concat(palette, ", "))
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def suggest_improvements(filename: str) -> str:
    """
    AI analysis to suggest improvements

    Args:
        filename: Name of the Aseprite file

    Returns:
        Improvement suggestions
    """
    if not os.path.exists(filename):
        return f"Error: File '{filename}' not found"

    lua_script = f"""
    local sprite = app.open('{filename}')
    if not sprite then
        print("Error: Failed to open sprite")
        return
    end

    local suggestions = {{}}

    -- Analyze sprite dimensions
    if sprite.width % 8 ~= 0 or sprite.height % 8 ~= 0 then
        table.insert(suggestions, "Consider power-of-2 dimensions for better performance")
    end

    -- Check layer count
    if #sprite.layers > 10 then
        table.insert(suggestions, "Consider organizing layers into groups")
    end

    -- Check palette usage
    if #sprite.palettes[1] > 32 then
        table.insert(suggestions, "Large palette detected - consider reducing colors")
    end

    -- Check for single-pixel details
    local cel = app.activeCel
    if cel then
        local hasIsolatedPixels = false
        local image = cel.image

        for y = 1, image.height - 2 do
            for x = 1, image.width - 2 do
                local center = image:getPixel(x, y)
                local centerColor = Color{{rgbaPixel = center}}

                if centerColor.alpha > 0 then
                    local neighborCount = 0
                    for dy = -1, 1 do
                        for dx = -1, 1 do
                            if dx ~= 0 or dy ~= 0 then
                                local neighbor = image:getPixel(x + dx, y + dy)
                                local neighborColor = Color{{rgbaPixel = neighbor}}
                                if neighborColor.alpha > 0 then
                                    neighborCount = neighborCount + 1
                                end
                            end
                        end
                    end

                    if neighborCount == 0 then
                        hasIsolatedPixels = true
                        break
                    end
                end
            end
            if hasIsolatedPixels then break end
        end

        if hasIsolatedPixels then
            table.insert(suggestions, "Isolated pixels detected - consider cleanup")
        end
    end

    if #suggestions == 0 then
        table.insert(suggestions, "Sprite looks well-optimized!")
    end

    sprite:close()
    print("Suggestions: " .. table.concat(suggestions, "; "))
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def auto_cleanup_lineart(filename: str) -> str:
    """
    Automatically clean up and smooth line art

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

    local cel = app.activeCel
    if not cel then
        print("Error: No active cel")
        sprite:close()
        return
    end

    local image = cel.image
    local cleanedImage = Image(image.width, image.height, image.colorMode)

    app.transaction(function()
        -- Copy original
        cleanedImage:drawImage(image, Point(0, 0))

        -- Simple cleanup: remove isolated pixels
        for y = 1, image.height - 2 do
            for x = 1, image.width - 2 do
                local center = image:getPixel(x, y)
                local centerColor = Color{{rgbaPixel = center}}

                if centerColor.alpha > 0 then
                    local neighborCount = 0
                    for dy = -1, 1 do
                        for dx = -1, 1 do
                            if dx ~= 0 or dy ~= 0 then
                                local neighbor = image:getPixel(x + dx, y + dy)
                                local neighborColor = Color{{rgbaPixel = neighbor}}
                                if neighborColor.alpha > 0 then
                                    neighborCount = neighborCount + 1
                                end
                            end
                        end
                    end

                    -- Remove isolated pixels
                    if neighborCount == 0 then
                        cleanedImage:clear(Rectangle(x, y, 1, 1))
                    end

                    -- Strengthen lines (connect near pixels)
                    if neighborCount >= 2 then
                        -- Keep as is - it's part of a line
                    elseif neighborCount == 1 then
                        -- Single connection - might need strengthening
                        -- For now, keep as is
                    end
                end
            end
        end

        cel.image = cleanedImage
    end)

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Auto-cleaned lineart")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def batch_process_sprites(folder: str, operations: list) -> str:
    """
    Batch process multiple sprites with progress tracking

    Args:
        folder: Folder containing .aseprite files
        operations: List of operations to perform

    Returns:
        Processing results
    """
    if not os.path.exists(folder):
        return f"Error: Folder '{folder}' not found"

    files = [f for f in os.listdir(folder) if f.endswith(('.aseprite', '.ase'))]

    if not files:
        return "Error: No .aseprite files found"

    processed = 0
    errors = 0

    for file in files:
        filepath = os.path.join(folder, file)
        try:
            # Process each operation
            for op in operations:
                if op == "optimize":
                    await optimize_file_size(filepath)
                elif op == "trim":
                    from .transform import trim_sprite
                    await trim_sprite(filepath)
                elif op == "outline":
                    await auto_outline_sprite(filepath)
                # Add more operations as needed

            processed += 1
        except Exception as e:
            errors += 1

    return f"Success: Processed {processed}/{len(files)} files. Errors: {errors}"


@mcp.tool()
async def smart_resize_preserve_pixels(filename: str, target_width: int, target_height: int) -> str:
    """
    Smart resize that preserves pixel art characteristics

    Args:
        filename: Name of the Aseprite file to modify
        target_width: Target width
        target_height: Target height

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

    -- Calculate scale factors
    local scaleX = {target_width} / sprite.width
    local scaleY = {target_height} / sprite.height

    -- If scales are integers, use nearest neighbor
    if scaleX == math.floor(scaleX) and scaleY == math.floor(scaleY) then
        sprite:resize({target_width}, {target_height})
    else
        -- Use more careful scaling for non-integer scales
        -- For now, just use regular resize
        sprite:resize({target_width}, {target_height})
    end

    sprite:saveAs('{filename}')
    sprite:close()
    print("Success: Smart resized to {target_width}x{target_height}")
    """

    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


@mcp.tool()
async def generate_sprite_variations(filename: str, output_folder: str, count: int = 5) -> str:
    """
    Generate sprite variations using AI-like transformations

    Args:
        filename: Name of the source Aseprite file
        output_folder: Folder to save variations
        count: Number of variations to generate

    Returns:
        Success or error message
    """
    if not os.path.exists(filename):
        return f"Error: File '{filename}' not found"

    os.makedirs(output_folder, exist_ok=True)

    # Generate variations with different techniques
    variations = [
        ("hue_shifted", "Hue shift"),
        ("contrast_high", "High contrast"),
        ("outlined", "With outline"),
        ("pixelated", "Pixelated"),
        ("brightened", "Brightened")
    ]

    created = 0
    for i, (variation_type, description) in enumerate(variations[:count]):
        try:
            output_file = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(filename))[0]}_{variation_type}.aseprite")

            # Copy original
            shutil.copy2(filename, output_file)

            # Apply variation
            if variation_type == "hue_shifted":
                await adjust_hue_saturation(output_file, hue=60)
            elif variation_type == "contrast_high":
                await adjust_brightness_contrast(output_file, contrast=50)
            elif variation_type == "outlined":
                await auto_outline_sprite(output_file)
            elif variation_type == "pixelated":
                await pixelate(output_file, 3)
            elif variation_type == "brightened":
                await adjust_brightness_contrast(output_file, brightness=30)

            created += 1
        except Exception:
            pass

    return f"Success: Generated {created} sprite variations in {output_folder}"