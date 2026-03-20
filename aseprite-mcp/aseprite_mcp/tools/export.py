import os
from ..core.commands import AsepriteCommand
from .. import mcp

@mcp.tool()
async def export_sprite(filename: str, output_filename: str, format: str = "png") -> str:
    """Export the Aseprite file to another format.

    Args:
        filename: Name of the Aseprite file to export
        output_filename: Name of the output file
        format: Output format (default: "png", can be "png", "gif", "jpg", etc.)
    """
    if not os.path.exists(filename):
        return f"File {filename} not found"
    
    # Make sure format is lowercase
    format = format.lower()
    
    # Ensure output filename has the correct extension
    if not output_filename.lower().endswith(f".{format}"):
        output_filename = f"{output_filename}.{format}"
    
    # For animated exports
    if format == "gif":
        args = ["--batch", filename, "--save-as", output_filename]
        success, output = AsepriteCommand.run_command(args)
    else:
        # For still image exports
        args = ["--batch", filename, "--save-as", output_filename]
        success, output = AsepriteCommand.run_command(args)
    
    if success:
        return f"Sprite exported successfully to {output_filename}"
    else:
        return f"Failed to export sprite: {output}"