# 🚀 Aseprite MCP - Roadmap Nâng Cấp Toàn Diện

## 📊 Phân Tích Hiện Trạng

### ✅ Đã Implement (11 functions)
- ✓ Canvas creation (`Sprite`)
- ✓ Basic layer management (`Layer.add`)
- ✓ Frame management (`Frame.add`)
- ✓ Pixel drawing (`Image:drawPixel`)
- ✓ Line drawing (`useTool`)
- ✓ Rectangle drawing (`useTool`)
- ✓ Circle drawing (`useTool`)
- ✓ Fill area (`useTool - bucket`)
- ✓ Export to PNG/GIF/JPG (`saveCopyAs`)
- ✓ Command execution
- ✓ Lua script execution

**Coverage hiện tại: ~15% API capability**

---

## 🎯 Roadmap Nâng Cấp - 80+ Functions Mới (Không bao gồm Animation)

### 📈 Priority Matrix

```
High Value + Easy → Phase 1 (Quick Wins)
High Value + Hard → Phase 2 (Strategic)
Low Value + Easy → Phase 3 (Nice-to-have)
Low Value + Hard → Phase 4 (Future)
```

---

## 🏆 PHASE 1: Quick Wins (16 functions) - Tác động lớn, dễ implement

### 1.1. Advanced Layer Operations (6 functions) ⭐⭐⭐
**Value:** Rất cao - Thiết yếu cho workflow chuyên nghiệp

```python
# layer_advanced.py

@mcp.tool()
async def set_layer_opacity(filename: str, layer_name: str, opacity: int):
    """Đặt độ trong suốt của layer (0-255)"""

@mcp.tool()
async def set_layer_blend_mode(filename: str, layer_name: str, blend_mode: str):
    """Đặt blend mode: normal, multiply, screen, overlay, darken, lighten, etc."""

@mcp.tool()
async def toggle_layer_visibility(filename: str, layer_name: str, visible: bool):
    """Ẩn/hiện layer"""

@mcp.tool()
async def create_layer_group(filename: str, group_name: str):
    """Tạo layer group để tổ chức layers"""

@mcp.tool()
async def move_layer_to_group(filename: str, layer_name: str, group_name: str):
    """Di chuyển layer vào group"""

@mcp.tool()
async def rename_layer(filename: str, old_name: str, new_name: str):
    """Đổi tên layer"""
```

**Lua API sử dụng:**
- `Layer.opacity`
- `Layer.blendMode`
- `Layer.isVisible`
- `Layer.isGroup`
- `Layer.parent`
- `Layer.name`

---

### 1.2. Color & Palette Management (5 functions) ⭐⭐⭐
**Value:** Cao - Essential cho pixel art

```python
# palette.py

@mcp.tool()
async def create_palette(filename: str, colors: list):
    """Tạo palette mới từ danh sách màu hex"""

@mcp.tool()
async def get_palette_colors(filename: str):
    """Lấy tất cả màu trong palette hiện tại"""

@mcp.tool()
async def add_color_to_palette(filename: str, color: str):
    """Thêm màu vào palette"""

@mcp.tool()
async def replace_color(filename: str, old_color: str, new_color: str):
    """Thay thế màu trong toàn bộ sprite"""

@mcp.tool()
async def load_palette_from_file(filename: str, palette_file: str):
    """Load palette từ file (.gpl, .ase, .act)"""
```

**Lua API sử dụng:**
- `Palette`
- `Palette:resize()`
- `Palette:getColor()`
- `Palette:setColor()`
- `Sprite.palettes`

---

### 1.3. Selection Operations (5 functions) ⭐⭐⭐
**Value:** Cao - Powerful cho editing

```python
# selection.py

@mcp.tool()
async def select_rectangle(filename: str, x: int, y: int, width: int, height: int):
    """Tạo selection hình chữ nhật"""

@mcp.tool()
async def select_all(filename: str):
    """Select toàn bộ canvas"""

@mcp.tool()
async def deselect(filename: str):
    """Bỏ selection"""

@mcp.tool()
async def invert_selection(filename: str):
    """Đảo ngược selection"""

@mcp.tool()
async def delete_selection(filename: str):
    """Xóa vùng đã select"""
```

**Lua API sử dụng:**
- `Selection`
- `Selection:select(Rectangle)`
- `Selection:selectAll()`
- `Selection:deselect()`
- `Selection:invert()`

---

## 🎨 PHASE 2: Strategic Features (24 functions) - High value, more complex

### 2.1. Image Transformation (8 functions) ⭐⭐⭐
**Value:** Rất cao - Professional editing

```python
# transform.py

@mcp.tool()
async def flip_horizontal(filename: str, layer_name: str = None):
    """Lật ngang image/layer"""

@mcp.tool()
async def flip_vertical(filename: str, layer_name: str = None):
    """Lật dọc image/layer"""

@mcp.tool()
async def rotate_image(filename: str, angle: float, layer_name: str = None):
    """Xoay image: 90, 180, 270 degrees hoặc tùy ý"""

@mcp.tool()
async def resize_sprite(filename: str, width: int, height: int, method: str = "nearest"):
    """Resize sprite: nearest, bilinear, rotsprite"""

@mcp.tool()
async def crop_sprite(filename: str, x: int, y: int, width: int, height: int):
    """Crop sprite về vùng được chỉ định"""

@mcp.tool()
async def scale_sprite(filename: str, scale_x: float, scale_y: float):
    """Scale sprite theo tỷ lệ phần trăm"""

@mcp.tool()
async def trim_sprite(filename: str):
    """Tự động trim transparent pixels xung quanh"""

@mcp.tool()
async def expand_canvas(filename: str, left: int, top: int, right: int, bottom: int):
    """Mở rộng canvas size"""
```

**Lua API sử dụng:**
- `app.command.Flip`
- `app.command.Rotate`
- `Sprite:resize()`
- `Sprite:crop()`
- `Image:resize()`

---

### 2.2. Advanced Drawing Tools (7 functions) ⭐⭐
**Value:** Cao - Richer drawing capabilities

```python
# drawing_advanced.py

@mcp.tool()
async def draw_polygon(filename: str, points: list, color: str, fill: bool = False):
    """Vẽ polygon từ list các points"""

@mcp.tool()
async def draw_bezier_curve(filename: str, points: list, color: str, thickness: int = 1):
    """Vẽ Bezier curve"""

@mcp.tool()
async def draw_gradient(filename: str, x1: int, y1: int, x2: int, y2: int, color1: str, color2: str, type: str = "linear"):
    """Vẽ gradient: linear, radial"""

@mcp.tool()
async def draw_text(filename: str, text: str, x: int, y: int, font_size: int = 12, color: str = "#000000"):
    """Vẽ text lên canvas"""

@mcp.tool()
async def apply_brush_stroke(filename: str, points: list, brush_size: int = 1, color: str = "#000000"):
    """Vẽ brush stroke theo path"""

@mcp.tool()
async def draw_pattern(filename: str, x: int, y: int, width: int, height: int, pattern_image: str):
    """Fill vùng bằng pattern từ image"""

@mcp.tool()
async def erase_area(filename: str, x: int, y: int, width: int, height: int):
    """Xóa transparent vùng được chỉ định"""
```

**Lua API sử dụng:**
- `GraphicsContext:drawImage()`
- `GraphicsContext:strokeRect()`
- `Image:drawImage()`
- Custom Lua logic cho algorithms

---

### 2.3. Cel Operations (5 functions) ⭐⭐
**Value:** Trung bình-Cao - Fine-grained control

```python
# cel_operations.py

@mcp.tool()
async def move_cel(filename: str, layer_name: str, frame_number: int, x: int, y: int):
    """Di chuyển cel position"""

@mcp.tool()
async def copy_cel(filename: str, src_layer: str, src_frame: int, dst_layer: str, dst_frame: int):
    """Copy cel từ layer/frame này sang layer/frame khác"""

@mcp.tool()
async def link_cel(filename: str, layer_name: str, frame_number: int, target_frame: int):
    """Link cel (shared content giữa frames)"""

@mcp.tool()
async def set_cel_opacity(filename: str, layer_name: str, frame_number: int, opacity: int):
    """Đặt opacity của cel cụ thể"""

@mcp.tool()
async def clear_cel(filename: str, layer_name: str, frame_number: int):
    """Xóa nội dung cel"""
```

**Lua API sử dụng:**
- `Cel.position`
- `Cel.opacity`
- `Sprite:newCel()`
- `Cel.image`

---

### 2.4. Sprite Sheet Export (4 functions) ⭐⭐⭐
**Value:** Rất cao - Essential cho game dev

```python
# spritesheet.py

@mcp.tool()
async def export_sprite_sheet(
    filename: str,
    output: str,
    layout: str = "horizontal",
    padding: int = 0,
    inner_padding: int = 0
):
    """Export sprite sheet với layout: horizontal, vertical, packed, rows, columns"""

@mcp.tool()
async def export_sprite_sheet_with_json(filename: str, output_image: str, output_json: str):
    """Export sprite sheet + JSON metadata"""

@mcp.tool()
async def export_layers_separately(filename: str, output_folder: str):
    """Export mỗi layer thành file riêng"""

@mcp.tool()
async def export_frames_separately(filename: str, output_folder: str, prefix: str = "frame"):
    """Export mỗi frame thành file riêng"""
```

**Lua API sử dụng:**
- `app.command.ExportSpriteSheet`
- `SpriteSheetType.HORIZONTAL`, `VERTICAL`, `PACKED`, etc.
- `SpriteSheetDataFormat.JSON_ARRAY`, `JSON_HASH`

---

## 🔧 PHASE 3: Professional Tools (20 functions)

### 3.1. Tilemap Support (6 functions) ⭐⭐
**Value:** Cao cho game development

```python
# tilemap.py

@mcp.tool()
async def create_tileset(filename: str, tileset_name: str, tile_width: int, tile_height: int):
    """Tạo tileset mới"""

@mcp.tool()
async def create_tilemap_layer(filename: str, layer_name: str, tileset_name: str):
    """Tạo tilemap layer"""

@mcp.tool()
async def set_tile(filename: str, layer_name: str, x: int, y: int, tile_index: int):
    """Đặt tile tại vị trí grid"""

@mcp.tool()
async def get_tile(filename: str, layer_name: str, x: int, y: int):
    """Lấy tile index tại vị trí"""

@mcp.tool()
async def import_tileset_from_image(filename: str, tileset_name: str, image_path: str, tile_width: int, tile_height: int):
    """Import tileset từ image"""

@mcp.tool()
async def export_tileset(filename: str, tileset_name: str, output: str):
    """Export tileset thành image"""
```

**Lua API sử dụng:**
- `Tileset`
- `Tile`
- `Layer.isTilemap`
- `TilesetMode`

---

### 3.2. Image Effects (8 functions) ⭐⭐
**Value:** Trung bình - Creative tools

```python
# effects.py

@mcp.tool()
async def apply_blur(filename: str, radius: int = 1):
    """Apply blur effect"""

@mcp.tool()
async def adjust_brightness_contrast(filename: str, brightness: int = 0, contrast: int = 0):
    """Điều chỉnh brightness (-100 to 100) và contrast (-100 to 100)"""

@mcp.tool()
async def adjust_hue_saturation(filename: str, hue: int = 0, saturation: int = 0, lightness: int = 0):
    """Điều chỉnh HSL"""

@mcp.tool()
async def invert_colors(filename: str):
    """Đảo ngược màu"""

@mcp.tool()
async def posterize(filename: str, levels: int = 4):
    """Posterize effect"""

@mcp.tool()
async def pixelate(filename: str, pixel_size: int = 2):
    """Pixelate effect"""

@mcp.tool()
async def outline(filename: str, color: str = "#000000"):
    """Tạo outline xung quanh sprite"""

@mcp.tool()
async def drop_shadow(filename: str, offset_x: int = 2, offset_y: int = 2, color: str = "#000000", blur: int = 1):
    """Thêm drop shadow"""
```

**Lua API sử dụng:**
- `app.command` với các effects
- Custom pixel manipulation

---

### 3.3. Clipboard & Copy/Paste (6 functions) ⭐⭐
**Value:** Trung bình - Workflow enhancement

```python
# clipboard.py

@mcp.tool()
async def copy_to_clipboard(filename: str):
    """Copy selection hoặc toàn bộ sprite vào clipboard"""

@mcp.tool()
async def cut_to_clipboard(filename: str):
    """Cut selection vào clipboard"""

@mcp.tool()
async def paste_from_clipboard(filename: str, x: int = 0, y: int = 0):
    """Paste từ clipboard"""

@mcp.tool()
async def copy_layer(filename: str, layer_name: str):
    """Copy toàn bộ layer"""

@mcp.tool()
async def paste_as_new_layer(filename: str, layer_name: str = "Pasted"):
    """Paste thành layer mới"""

@mcp.tool()
async def merge_layers(filename: str, layer_names: list, result_name: str):
    """Merge nhiều layers thành một"""
```

**Lua API sử dụng:**
- `app.clipboard`
- `app.command.Copy`, `Cut`, `Paste`
- Layer manipulation

---

## 🚀 PHASE 4: Advanced & Experimental (20 functions)

### 4.1. Custom Brush System (5 functions) ⭐
**Value:** Trung bình - Advanced users

```python
# brush.py

@mcp.tool()
async def create_custom_brush(brush_name: str, image_path: str):
    """Tạo custom brush từ image"""

@mcp.tool()
async def set_brush_size(size: int):
    """Đặt brush size"""

@mcp.tool()
async def set_brush_angle(angle: int):
    """Đặt brush rotation angle"""

@mcp.tool()
async def set_brush_pattern(pattern: str):
    """Đặt brush pattern: origin, target, none"""

@mcp.tool()
async def list_brushes():
    """Liệt kê tất cả brushes available"""
```

**Lua API sử dụng:**
- `Brush`
- `BrushType`
- `BrushPattern`

---

### 4.2. Slices & 9-Patch (4 functions) ⭐
**Value:** Thấp-Trung bình - UI development

```python
# slices.py

@mcp.tool()
async def create_slice(filename: str, name: str, x: int, y: int, width: int, height: int):
    """Tạo slice region"""

@mcp.tool()
async def create_nine_patch_slice(filename: str, name: str, bounds: dict, center: dict):
    """Tạo 9-patch slice cho UI scaling"""

@mcp.tool()
async def list_slices(filename: str):
    """Liệt kê tất cả slices"""

@mcp.tool()
async def export_slices(filename: str, output_folder: str):
    """Export tất cả slices thành files riêng"""
```

**Lua API sử dụng:**
- `Slice`
- `Slice.bounds`
- `Slice.center` (9-patch)

---

### 4.3. Real-time Communication (3 functions) ⭐
**Value:** Thấp - Experimental

```python
# realtime.py

@mcp.tool()
async def start_websocket_server(port: int = 8080):
    """Khởi động WebSocket server cho real-time updates"""

@mcp.tool()
async def broadcast_sprite_update(filename: str, event_type: str):
    """Broadcast sprite changes qua WebSocket"""

@mcp.tool()
async def subscribe_to_changes(filename: str, callback_url: str):
    """Subscribe to sprite change events"""
```

**Lua API sử dụng:**
- `WebSocket`
- `WebSocketMessageType`

---

### 4.4. Custom UI & Dialogs (5 functions) ⭐⭐
**Value:** Trung bình - Interactive workflows

```python
# ui.py

@mcp.tool()
async def show_color_picker(default_color: str = "#000000"):
    """Hiển thị color picker dialog"""

@mcp.tool()
async def show_input_dialog(title: str, label: str, default_value: str = ""):
    """Hiển thị input dialog"""

@mcp.tool()
async def show_confirm_dialog(title: str, message: str):
    """Hiển thị confirmation dialog"""

@mcp.tool()
async def show_file_dialog(title: str, mode: str = "open", filters: list = None):
    """Hiển thị file picker: open, save"""

@mcp.tool()
async def show_progress_dialog(title: str, steps: int):
    """Hiển thị progress dialog cho long operations"""
```

**Lua API sử dụng:**
- `Dialog`
- Dialog widgets: button, entry, color, file
- `app.alert()`

---

### 4.5. Plugin Development Support (3 functions) ⭐
**Value:** Thấp - Developer tools

```python
# plugin.py

@mcp.tool()
async def install_plugin(plugin_path: str):
    """Install Aseprite plugin"""

@mcp.tool()
async def list_plugins():
    """Liệt kê installed plugins"""

@mcp.tool()
async def execute_plugin_command(plugin_name: str, command: str, params: dict = None):
    """Thực thi plugin command"""
```

**Lua API sử dụng:**
- `Plugin`
- `plugin:newCommand()`

---

## 🎯 PHASE 5: AI Integration & Automation (9+ functions)

### 5.1. AI-Powered Features ⭐⭐⭐
**Value:** Rất cao - Future-proof

```python
# ai_features.py

@mcp.tool()
async def auto_color_sprite(filename: str, color_palette: list):
    """Tự động tô màu sprite theo palette"""

@mcp.tool()
async def upscale_sprite_ai(filename: str, scale: int = 2, model: str = "pixel"):
    """AI upscaling: pixel-perfect, smooth"""

@mcp.tool()
async def auto_outline_sprite(filename: str, style: str = "clean"):
    """Tự động tạo outline với AI"""

@mcp.tool()
async def extract_color_palette_smart(filename: str, num_colors: int = 16):
    """AI-powered palette extraction"""

@mcp.tool()
async def suggest_improvements(filename: str):
    """AI analyze và suggest improvements"""

@mcp.tool()
async def auto_cleanup_lineart(filename: str):
    """Tự động cleanup và smooth lineart"""

@mcp.tool()
async def batch_process_sprites(folder: str, operations: list):
    """Batch processing với progress tracking"""
```

---

## 📦 Utility Functions (15+ functions)

### 6.1. Advanced File Operations

```python
# file_operations.py

@mcp.tool()
async def batch_convert(input_folder: str, output_folder: str, format: str):
    """Batch convert files"""

@mcp.tool()
async def optimize_file_size(filename: str):
    """Optimize file size"""

@mcp.tool()
async def get_sprite_info(filename: str):
    """Get detailed sprite information:
    - dimensions, color mode, frame count
    - layer count, palette info, file size"""

@mcp.tool()
async def compare_sprites(file1: str, file2: str):
    """Compare hai sprites và return differences"""

@mcp.tool()
async def backup_sprite(filename: str, backup_folder: str = None):
    """Tạo backup với timestamp"""

@mcp.tool()
async def restore_sprite(filename: str, backup_timestamp: str):
    """Restore từ backup"""
```

### 6.2. Color Space & Profile Management

```python
# colorspace.py

@mcp.tool()
async def convert_color_mode(filename: str, mode: str):
    """Convert: RGB, Grayscale, Indexed"""

@mcp.tool()
async def assign_color_profile(filename: str, profile_path: str):
    """Assign ICC color profile"""

@mcp.tool()
async def convert_to_indexed_color(filename: str, num_colors: int = 256, dithering: str = "none"):
    """Convert to indexed với dithering"""
```

### 6.3. Grid & Guides

```python
# grid.py

@mcp.tool()
async def set_grid(filename: str, width: int, height: int):
    """Đặt grid size"""

@mcp.tool()
async def toggle_grid(filename: str, visible: bool):
    """Show/hide grid"""

@mcp.tool()
async def snap_to_grid(filename: str, enabled: bool):
    """Enable/disable snap to grid"""
```

---

## 📊 Tổng Kết Implementation Plan

### Tổng Số Functions Mới: **90 functions** (Không bao gồm Animation)

| Phase | Functions | Complexity | Timeline | Priority |
|-------|-----------|------------|----------|----------|
| **Phase 1** | 16 | Low-Medium | 1-2 weeks | ⭐⭐⭐ Critical |
| **Phase 2** | 24 | Medium-High | 3-5 weeks | ⭐⭐⭐ High |
| **Phase 3** | 20 | Medium | 3-4 weeks | ⭐⭐ Medium |
| **Phase 4** | 20 | High | 4-6 weeks | ⭐ Low |
| **Phase 5** | 9+ | Very High | 5-7 weeks | ⭐⭐⭐ Strategic |
| **Utilities** | 15 | Low-Medium | 2-3 weeks | ⭐⭐ Medium |

**Total Timeline: 18-27 weeks (4.5-7 months) cho full implementation**

---

## 🎓 Learning Curves & Dependencies

### Technical Dependencies
1. **Lua Scripting Mastery** - Deep dive vào Aseprite Lua API
2. **Image Processing** - Algorithms cho effects và transformations
3. **WebSocket** - For real-time features
4. **AI/ML Integration** - Cho Phase 5 features
5. **Testing Infrastructure** - Unit tests cho 100+ functions

### Recommended Order
```
Phase 1 → Utilities → Phase 2 → Phase 3 → Phase 5 (parallel) → Phase 4
```

---

## 💡 Quick Wins để Bắt Đầu Ngay

### Week 1-2: Essential 8 Functions
1. ✅ `set_layer_opacity`
2. ✅ `set_layer_blend_mode`
3. ✅ `toggle_layer_visibility`
4. ✅ `flip_horizontal/vertical`
5. ✅ `select_rectangle`
6. ✅ `export_sprite_sheet`
7. ✅ `get_sprite_info`
8. ✅ `resize_sprite`

### Impact: +50% usability với minimal effort

---

## 🚀 Game-Changing Features

### Top 5 High-Impact Additions
1. **Sprite Sheet Export với JSON** - Game development essential
2. **Layer Blend Modes & Opacity** - Advanced compositing
3. **Image Transformation Suite** - Professional editing
4. **Batch Processing** - Productivity multiplier
5. **AI Color & Upscaling** - Revolutionary cho pixel art

---

## 🔥 Competitive Advantages sau khi hoàn thành

1. **Duy nhất MCP server** cho Aseprite với full API coverage
2. **AI Integration** - Không có tool nào khác có
3. **Automation** - Batch processing và scripting
4. **Real-time Collaboration** - WebSocket support
5. **Professional Workflow** - Complete toolchain cho game dev

---

## 📖 Documentation Structure

```
docs/
├── api/
│   ├── layer_operations.md
│   ├── drawing_tools.md
│   ├── transformation.md
│   ├── export.md
│   └── ai_features.md
├── tutorials/
│   ├── getting_started.md
│   ├── game_dev_pipeline.md
│   └── ai_assisted_creation.md
└── examples/
    ├── create_sprite_sheet.py
    ├── batch_processing.py
    └── ai_colorization.py
```

---

## 🎯 Success Metrics

### Coverage Goals
- ✅ Phase 1: 35% API coverage
- ✅ Phase 2: 60% API coverage
- ✅ Phase 3: 80% API coverage
- ✅ Phase 4: 95% API coverage
- ✅ Phase 5: 100% + AI enhancements

### Performance Targets
- ⚡ Execution time: < 500ms per operation
- 🔄 Batch operations: 10+ sprites/sec
- 📊 Memory usage: < 100MB per sprite
- 🎨 Export quality: Lossless

---

## 💪 Kết Luận

Với roadmap này, Aseprite MCP sẽ trở thành:
- **The most comprehensive** Aseprite automation tool
- **AI-powered** pixel art assistant
- **Professional grade** game development pipeline
- **Open source standard** cho Aseprite integration

**Từ 15% → 100% API coverage = 6.7x capability increase!**

---

**Prepared by:** Claude Code
**Date:** 2026-03-19
**Version:** 1.0
