"""Lua script templates and utilities"""

from typing import Optional


def sprite_operation_template(filename: str, operation_code: str) -> str:
    """Template for basic sprite operations with error handling"""
    return f"""
local sprite = app.open('{filename}')
if not sprite then
    print("Error: Failed to open sprite")
    return
end

{operation_code}

sprite:saveAs('{filename}')
sprite:close()
"""


def transaction_wrapper(code: str) -> str:
    """Wrap code in Aseprite transaction"""
    return f"""
app.transaction(function()
    {code}
end)
"""


def find_layer_template(layer_name: str, action_code: str) -> str:
    """Template for finding a layer and performing action"""
    return f"""
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

{action_code}
"""


def create_lua_color(hex_color: str) -> str:
    """Convert hex color to Lua Color constructor"""
    return f'Color{{fromString="{hex_color}"}}'


def create_lua_rectangle(x: int, y: int, width: int, height: int) -> str:
    """Create Lua Rectangle constructor"""
    return f'Rectangle({x}, {y}, {width}, {height})'


def layer_operation_template(filename: str, layer_name: str, action_code: str) -> str:
    """Template for operations that require finding a specific layer"""
    operation = find_layer_template(layer_name, action_code)
    return sprite_operation_template(filename, operation)


def execute_lua_with_template(template_func, *args, **kwargs):
    """Execute a Lua script template with error handling"""
    from ..core.commands import AsepriteCommand

    lua_script = template_func(*args, **kwargs)
    success, output = AsepriteCommand.execute_lua_script(lua_script)
    return output if success else f"Error: {output}"


def transform_operation_template(filename: str, layer_name: Optional[str], transform_code: str, success_message: str) -> str:
    """Template for transform operations that can target a layer or entire sprite"""
    if layer_name:
        operation = find_layer_template(layer_name, f"""
        app.activeLayer = layer
        {transform_code}
        print('Success: Layer \\'{layer_name}\\' {success_message}')
        """)
    else:
        operation = f"""
        {transform_code}
        print('Success: Sprite {success_message}')
        """

    return sprite_operation_template(filename, operation)