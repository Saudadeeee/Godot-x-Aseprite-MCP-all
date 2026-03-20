"""Advanced layer operations for Aseprite MCP"""

from aseprite_mcp import mcp
from aseprite_mcp.utils import (
    validate_opacity, validate_blend_mode, validate_non_empty_string
)
from aseprite_mcp.utils.lua_templates import (
    layer_operation_template, sprite_operation_template, execute_lua_with_template
)


@mcp.tool()
async def set_layer_opacity(filename: str, layer_name: str, opacity: int) -> str:
    """Set the opacity of a layer (0-255, where 255 is fully opaque)"""
    validate_opacity(opacity)

    action = f"layer.opacity = {opacity}\nprint('Success: Layer opacity set to {opacity}')"
    return execute_lua_with_template(layer_operation_template, filename, layer_name, action)


@mcp.tool()
async def set_layer_blend_mode(filename: str, layer_name: str, blend_mode: str) -> str:
    """Set the blend mode of a layer"""
    validated_mode = validate_blend_mode(blend_mode)

    action = f"""
    layer.blendMode = BlendMode.{validated_mode.upper()}
    print('Success: Layer blend mode set to {validated_mode}')
    """
    return execute_lua_with_template(layer_operation_template, filename, layer_name, action)


@mcp.tool()
async def toggle_layer_visibility(filename: str, layer_name: str, visible: bool) -> str:
    """Show or hide a layer"""
    visibility_text = 'visible' if visible else 'hidden'
    action = f"""
    layer.isVisible = {'true' if visible else 'false'}
    print('Success: Layer visibility set to {visibility_text}')
    """
    return execute_lua_with_template(layer_operation_template, filename, layer_name, action)


@mcp.tool()
async def create_layer_group(filename: str, group_name: str) -> str:
    """Create a layer group to organize layers"""
    validate_non_empty_string(group_name, "Group name")

    operation = f"""
    -- Check if group already exists
    for _, l in ipairs(sprite.layers) do
        if l.name == '{group_name}' and l.isGroup then
            print("Error: Layer group '{group_name}' already exists")
            sprite:close()
            return
        end
    end

    app.transaction(function()
        local group = sprite:newGroup()
        group.name = '{group_name}'
    end)

    print("Success: Layer group '{group_name}' created")
    """
    return execute_lua_with_template(sprite_operation_template, filename, operation)


@mcp.tool()
async def move_layer_to_group(filename: str, layer_name: str, group_name: str) -> str:
    """Move a layer into a group"""
    validate_non_empty_string(layer_name, "Layer name")
    validate_non_empty_string(group_name, "Group name")

    operation = f"""
    local layer = nil
    local group = nil

    -- Find layer and group
    for _, l in ipairs(sprite.layers) do
        if l.name == '{layer_name}' then
            layer = l
        end
        if l.name == '{group_name}' and l.isGroup then
            group = l
        end
    end

    if not layer then
        print("Error: Layer '{layer_name}' not found")
        sprite:close()
        return
    end

    if not group then
        print("Error: Layer group '{group_name}' not found or is not a group")
        sprite:close()
        return
    end

    app.transaction(function()
        layer.parent = group
    end)

    print("Success: Layer '{layer_name}' moved to group '{group_name}'")
    """
    return execute_lua_with_template(sprite_operation_template, filename, operation)


@mcp.tool()
async def rename_layer(filename: str, old_name: str, new_name: str) -> str:
    """Rename a layer"""
    validate_non_empty_string(old_name, "Old layer name")
    validate_non_empty_string(new_name, "New layer name")

    operation = f"""
    local layer = nil
    for _, l in ipairs(sprite.layers) do
        if l.name == '{old_name}' then
            layer = l
            break
        end
    end

    if not layer then
        print("Error: Layer '{old_name}' not found")
        sprite:close()
        return
    end

    -- Check if new name already exists
    for _, l in ipairs(sprite.layers) do
        if l.name == '{new_name}' then
            print("Error: Layer '{new_name}' already exists")
            sprite:close()
            return
        end
    end

    layer.name = '{new_name}'
    print("Success: Layer renamed from '{old_name}' to '{new_name}'")
    """
    return execute_lua_with_template(sprite_operation_template, filename, operation)
