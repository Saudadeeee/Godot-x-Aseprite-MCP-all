"""Custom brush system for Aseprite MCP - Simplified version"""

from aseprite_mcp import mcp
from aseprite_mcp.core.commands import AsepriteCommand
import os


@mcp.tool()
async def create_custom_brush(brush_name: str, image_path: str) -> str:
    """
    Create custom brush from image (Note: Limited API support)

    Args:
        brush_name: Name for the brush
        image_path: Path to brush image

    Returns:
        Success or error message
    """
    return f"Info: Custom brush creation has limited API support. Consider importing brushes manually in Aseprite."


@mcp.tool()
async def set_brush_size(size: int) -> str:
    """Set current brush size"""
    return f"Info: Brush size is typically set per-tool. Use drawing functions with size parameter."


@mcp.tool()
async def set_brush_angle(angle: int) -> str:
    """Set brush rotation angle"""
    return f"Info: Brush angle control has limited API support."


@mcp.tool()
async def set_brush_pattern(pattern: str) -> str:
    """Set brush pattern"""
    return f"Info: Brush patterns have limited API support."


@mcp.tool()
async def list_brushes() -> str:
    """List available brushes"""
    return "Info: Brush listing has limited API support. Default brushes: circle, square."
