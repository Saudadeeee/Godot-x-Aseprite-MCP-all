# Hướng Dẫn Sử Dụng Aseprite MCP Server

## Tổng Quan Dự Án

**Aseprite MCP** là một MCP (Model Context Protocol) server cho phép các AI assistant tương tác và điều khiển Aseprite thông qua các lệnh lập trình. Project sử dụng Python 3.13 và FastMCP để triển khai server.

### Cấu Trúc Thư Mục

```
aseprite-mcp/
├── aseprite_mcp/              # Package Python chính
│   ├── __init__.py            # Khởi tạo MCP server
│   ├── __main__.py            # Entry point để chạy server
│   ├── core/                  # Chức năng cốt lõi
│   │   ├── __init__.py
│   │   └── commands.py        # Wrapper để thực thi lệnh Aseprite
│   └── tools/                 # Triển khai các MCP tools
│       ├── __init__.py
│       ├── canvas.py          # Quản lý canvas và layer cơ bản
│       ├── drawing.py         # Công cụ vẽ
│       ├── export.py          # Chức năng xuất file
│       ├── layer_advanced.py  # Layer operations nâng cao
│       ├── palette.py         # Color & palette management
│       └── selection.py       # Selection operations
├── scripts/                   # Scripts tiện ích
│   ├── docker-entrypoint.sh
│   └── install-aseprite-steam.sh
├── tests/                     # Thư mục test
├── Dockerfile                 # Docker image definition
├── docker-compose.yml         # Docker Compose config
├── pyproject.toml             # Cấu hình project Python
├── requirements.txt           # Dependencies bổ sung
└── sample.env                 # Template biến môi trường
```

---

## 1. Core Module (`aseprite_mcp/core/commands.py`)

### Class: `AsepriteCommand`

Helper class để thực thi các lệnh Aseprite thông qua subprocess.

#### Phương thức:

#### 1.1. `run_command(args: list) -> tuple[bool, str]`

**Mô tả:** Chạy lệnh Aseprite với xử lý lỗi.

**Tham số:**
- `args` (list): Danh sách các tham số dòng lệnh

**Trả về:**
- `tuple[bool, str]`: (success, output)

**Sử dụng:**
- Sử dụng biến môi trường `ASEPRITE_PATH` hoặc mặc định 'aseprite'
- Thực thi trong batch mode
- Bắt lỗi subprocess và xử lý encoding

---

#### 1.2. `execute_lua_script(script_content: str, filename: str = None) -> tuple[bool, str]`

**Mô tả:** Thực thi script Lua trong Aseprite.

**Tham số:**
- `script_content` (str): Nội dung script Lua
- `filename` (str, optional): File Aseprite cần mở trước khi chạy script

**Trả về:**
- `tuple[bool, str]`: (success, output)

**Cơ chế hoạt động:**
1. Tạo file .lua tạm thời với nội dung script
2. Mở file Aseprite (nếu có)
3. Chạy trong batch mode
4. Dọn dẹp file tạm sau khi thực thi

---

## 2. Canvas Tools (`aseprite_mcp/tools/canvas.py`)

### 2.1. `create_canvas(width: int, height: int, filename: str = "canvas.aseprite") -> str`

**Mô tả:** Tạo canvas Aseprite mới với kích thước được chỉ định.

**Tham số:**
- `width` (int): Chiều rộng canvas (pixels)
- `height` (int): Chiều cao canvas (pixels)
- `filename` (str): Tên file đầu ra (mặc định: "canvas.aseprite")

**Trả về:**
- `str`: Thông báo thành công hoặc lỗi

**Ví dụ:**
```python
create_canvas(800, 600, "my_art.aseprite")
```

---

### 2.2. `add_layer(filename: str, layer_name: str) -> str`

**Mô tả:** Thêm layer mới vào file Aseprite đã tồn tại.

**Tham số:**
- `filename` (str): Tên file Aseprite cần chỉnh sửa
- `layer_name` (str): Tên của layer mới

**Trả về:**
- `str`: Thông báo thành công hoặc lỗi

**Đặc điểm:**
- Kiểm tra file tồn tại trước khi thực thi
- Sử dụng transaction để đảm bảo tính nguyên tử
- Tự động lưu file sau khi chỉnh sửa

**Ví dụ:**
```python
add_layer("my_art.aseprite", "Background")
```

---

### 2.3. `add_frame(filename: str) -> str`

**Mô tả:** Thêm frame mới vào file Aseprite (cho animation).

**Tham số:**
- `filename` (str): Tên file Aseprite cần chỉnh sửa

**Trả về:**
- `str`: Thông báo thành công hoặc lỗi

**Đặc điểm:**
- Tạo frame animation mới
- Tự động lưu file sau khi thêm frame

**Ví dụ:**
```python
add_frame("my_animation.aseprite")
```

---

## 3. Drawing Tools (`aseprite_mcp/tools/drawing.py`)

### 3.1. `draw_pixels(filename: str, pixels: list) -> str`

**Mô tả:** Vẽ các pixel riêng lẻ lên canvas.

**Tham số:**
- `filename` (str): Tên file Aseprite cần chỉnh sửa
- `pixels` (list): Danh sách dict với các key:
  - `x` (int): Tọa độ X
  - `y` (int): Tọa độ Y
  - `color` (str): Mã màu hex (vd: "#FF0000")

**Trả về:**
- `str`: Thông báo thành công hoặc lỗi

**Cơ chế:**
- Chuyển đổi màu hex sang RGB
- Chỉnh sửa image của cel đang hoạt động

**Ví dụ:**
```python
pixels = [
    {"x": 10, "y": 10, "color": "#FF0000"},
    {"x": 11, "y": 10, "color": "#00FF00"},
    {"x": 12, "y": 10, "color": "#0000FF"}
]
draw_pixels("canvas.aseprite", pixels)
```

---

### 3.2. `draw_line(filename: str, x1: int, y1: int, x2: int, y2: int, color: str = "#000000", thickness: int = 1) -> str`

**Mô tả:** Vẽ đường thẳng giữa hai điểm.

**Tham số:**
- `filename` (str): Tên file Aseprite
- `x1` (int): Tọa độ X điểm bắt đầu
- `y1` (int): Tọa độ Y điểm bắt đầu
- `x2` (int): Tọa độ X điểm kết thúc
- `y2` (int): Tọa độ Y điểm kết thúc
- `color` (str): Mã màu hex (mặc định: "#000000")
- `thickness` (int): Độ dày đường (mặc định: 1)

**Trả về:**
- `str`: Thông báo thành công hoặc lỗi

**Ví dụ:**
```python
draw_line("canvas.aseprite", 10, 10, 100, 100, "#FF0000", 3)
```

---

### 3.3. `draw_rectangle(filename: str, x: int, y: int, width: int, height: int, color: str = "#000000", fill: bool = False) -> str`

**Mô tả:** Vẽ hình chữ nhật (viền hoặc tô đầy).

**Tham số:**
- `filename` (str): Tên file Aseprite
- `x` (int): Tọa độ X góc trên-trái
- `y` (int): Tọa độ Y góc trên-trái
- `width` (int): Chiều rộng hình chữ nhật
- `height` (int): Chiều cao hình chữ nhật
- `color` (str): Mã màu hex (mặc định: "#000000")
- `fill` (bool): Tô đầy hay không (mặc định: False)

**Trả về:**
- `str`: Thông báo thành công hoặc lỗi

**Ví dụ:**
```python
# Vẽ viền
draw_rectangle("canvas.aseprite", 50, 50, 100, 80, "#0000FF", False)

# Tô đầy
draw_rectangle("canvas.aseprite", 200, 200, 150, 100, "#FF00FF", True)
```

---

### 3.4. `fill_area(filename: str, x: int, y: int, color: str = "#000000") -> str`

**Mô tả:** Tô màu vùng bằng công cụ paint bucket (flood fill).

**Tham số:**
- `filename` (str): Tên file Aseprite
- `x` (int): Tọa độ X điểm bắt đầu tô
- `y` (int): Tọa độ Y điểm bắt đầu tô
- `color` (str): Mã màu hex (mặc định: "#000000")

**Trả về:**
- `str`: Thông báo thành công hoặc lỗi

**Ví dụ:**
```python
fill_area("canvas.aseprite", 100, 100, "#FFFF00")
```

---

### 3.5. `draw_circle(filename: str, center_x: int, center_y: int, radius: int, color: str = "#000000", fill: bool = False) -> str`

**Mô tả:** Vẽ hình tròn/ellipse.

**Tham số:**
- `filename` (str): Tên file Aseprite
- `center_x` (int): Tọa độ X tâm
- `center_y` (int): Tọa độ Y tâm
- `radius` (int): Bán kính (pixels)
- `color` (str): Mã màu hex (mặc định: "#000000")
- `fill` (bool): Tô đầy hay không (mặc định: False)

**Trả về:**
- `str`: Thông báo thành công hoặc lỗi

**Ví dụ:**
```python
# Vẽ viền tròn
draw_circle("canvas.aseprite", 400, 300, 50, "#00FF00", False)

# Vẽ tròn tô đầy
draw_circle("canvas.aseprite", 200, 150, 75, "#FF0000", True)
```

---

## 4. Export Tools (`aseprite_mcp/tools/export.py`)

### 4.1. `export_sprite(filename: str, output_filename: str, format: str = "png") -> str`

**Mô tả:** Xuất file Aseprite sang các định dạng khác.

**Tham số:**
- `filename` (str): Tên file Aseprite nguồn
- `output_filename` (str): Tên file đầu ra
- `format` (str): Định dạng xuất (mặc định: "png")

**Định dạng hỗ trợ:**
- `png` - PNG image
- `gif` - Animated GIF
- `jpg` / `jpeg` - JPEG image
- Và các định dạng khác mà Aseprite hỗ trợ

**Đặc điểm:**
- Tự động thêm extension nếu thiếu
- Hỗ trợ xuất animation (GIF)
- Sử dụng lệnh `--save-as` của Aseprite

**Ví dụ:**
```python
# Xuất sang PNG
export_sprite("my_art.aseprite", "output.png", "png")

# Xuất animation sang GIF
export_sprite("my_animation.aseprite", "animation.gif", "gif")
```

---

## 5. Advanced Layer Operations (`aseprite_mcp/tools/layer_advanced.py`)

### 5.1. `set_layer_opacity(filename: str, layer_name: str, opacity: int) -> str`

**Mô tả:** Đặt độ trong suốt của layer.

**Tham số:**
- `filename` (str): Tên file Aseprite cần chỉnh sửa
- `layer_name` (str): Tên layer cần chỉnh sửa
- `opacity` (int): Độ trong suốt (0-255, 255 = hoàn toàn không trong suốt)

**Trả về:**
- `str`: Thông báo thành công hoặc lỗi

**Ví dụ:**
```python
# Đặt layer semi-transparent
set_layer_opacity("my_art.aseprite", "Background", 128)

# Đặt layer hoàn toàn trong suốt
set_layer_opacity("my_art.aseprite", "Watermark", 50)
```

---

### 5.2. `set_layer_blend_mode(filename: str, layer_name: str, blend_mode: str) -> str`

**Mô tả:** Đặt blend mode của layer.

**Tham số:**
- `filename` (str): Tên file Aseprite
- `layer_name` (str): Tên layer
- `blend_mode` (str): Blend mode

**Blend modes hỗ trợ:**
- `normal` - Normal blending
- `multiply` - Multiply
- `screen` - Screen
- `overlay` - Overlay
- `darken` - Darken
- `lighten` - Lighten
- `color_dodge` - Color Dodge
- `color_burn` - Color Burn
- `hard_light` - Hard Light
- `soft_light` - Soft Light
- `difference` - Difference
- `exclusion` - Exclusion
- `hue` - Hue
- `saturation` - Saturation
- `color` - Color
- `luminosity` - Luminosity
- `addition` - Addition
- `subtract` - Subtract
- `divide` - Divide

**Ví dụ:**
```python
set_layer_blend_mode("composite.aseprite", "Highlights", "screen")
set_layer_blend_mode("composite.aseprite", "Shadows", "multiply")
```

---

### 5.3. `toggle_layer_visibility(filename: str, layer_name: str, visible: bool) -> str`

**Mô tả:** Ẩn hoặc hiện layer.

**Tham số:**
- `filename` (str): Tên file Aseprite
- `layer_name` (str): Tên layer
- `visible` (bool): True để hiện, False để ẩn

**Ví dụ:**
```python
# Ẩn layer
toggle_layer_visibility("my_art.aseprite", "Sketch", False)

# Hiện layer
toggle_layer_visibility("my_art.aseprite", "Final", True)
```

---

### 5.4. `create_layer_group(filename: str, group_name: str) -> str`

**Mô tả:** Tạo layer group để tổ chức các layers.

**Tham số:**
- `filename` (str): Tên file Aseprite
- `group_name` (str): Tên group mới

**Ví dụ:**
```python
create_layer_group("my_art.aseprite", "Character")
create_layer_group("my_art.aseprite", "Background")
```

---

### 5.5. `move_layer_to_group(filename: str, layer_name: str, group_name: str) -> str`

**Mô tả:** Di chuyển layer vào group.

**Tham số:**
- `filename` (str): Tên file Aseprite
- `layer_name` (str): Tên layer cần di chuyển
- `group_name` (str): Tên group đích

**Ví dụ:**
```python
# Move layer vào group
move_layer_to_group("my_art.aseprite", "Head", "Character")
move_layer_to_group("my_art.aseprite", "Body", "Character")
```

---

### 5.6. `rename_layer(filename: str, old_name: str, new_name: str) -> str`

**Mô tả:** Đổi tên layer.

**Tham số:**
- `filename` (str): Tên file Aseprite
- `old_name` (str): Tên layer hiện tại
- `new_name` (str): Tên mới cho layer

**Ví dụ:**
```python
rename_layer("my_art.aseprite", "Layer 1", "Background")
```

---

## 6. Color & Palette Management (`aseprite_mcp/tools/palette.py`)

### 6.1. `create_palette(filename: str, colors: list) -> str`

**Mô tả:** Tạo palette mới từ danh sách màu hex.

**Tham số:**
- `filename` (str): Tên file Aseprite
- `colors` (list): Danh sách màu hex (vd: ["#FF0000", "#00FF00", "#0000FF"])

**Ví dụ:**
```python
# Tạo palette 8-bit style
colors = ["#000000", "#FFFFFF", "#FF0000", "#00FF00", "#0000FF", "#FFFF00"]
create_palette("pixel_art.aseprite", colors)
```

---

### 6.2. `get_palette_colors(filename: str) -> str`

**Mô tả:** Lấy tất cả màu trong palette hiện tại.

**Tham số:**
- `filename` (str): Tên file Aseprite

**Trả về:**
- Danh sách màu hex

**Ví dụ:**
```python
colors = get_palette_colors("my_art.aseprite")
# Output: "Palette colors: #FF0000, #00FF00, #0000FF, ..."
```

---

### 6.3. `add_color_to_palette(filename: str, color: str) -> str`

**Mô tả:** Thêm màu mới vào palette.

**Tham số:**
- `filename` (str): Tên file Aseprite
- `color` (str): Màu hex cần thêm (vd: "#FF0000")

**Ví dụ:**
```python
add_color_to_palette("pixel_art.aseprite", "#8B4513")
```

---

### 6.4. `replace_color(filename: str, old_color: str, new_color: str) -> str`

**Mô tả:** Thay thế tất cả pixels có màu cũ bằng màu mới trong toàn bộ sprite.

**Tham số:**
- `filename` (str): Tên file Aseprite
- `old_color` (str): Màu cần thay thế (hex)
- `new_color` (str): Màu mới (hex)

**Ví dụ:**
```python
# Đổi tất cả màu đỏ thành xanh
replace_color("my_art.aseprite", "#FF0000", "#00FF00")
```

---

### 6.5. `load_palette_from_file(filename: str, palette_file: str) -> str`

**Mô tả:** Load palette từ file external (.gpl, .ase, .aseprite, .act).

**Tham số:**
- `filename` (str): Tên file Aseprite cần áp dụng palette
- `palette_file` (str): Đường dẫn đến file palette

**Ví dụ:**
```python
load_palette_from_file("my_art.aseprite", "palettes/retro_8bit.gpl")
```

---

## 7. Selection Operations (`aseprite_mcp/tools/selection.py`)

### 7.1. `select_rectangle(filename: str, x: int, y: int, width: int, height: int) -> str`

**Mô tả:** Tạo selection hình chữ nhật.

**Tham số:**
- `filename` (str): Tên file Aseprite
- `x` (int): Tọa độ X góc trên-trái
- `y` (int): Tọa độ Y góc trên-trái
- `width` (int): Chiều rộng selection
- `height` (int): Chiều cao selection

**Ví dụ:**
```python
# Select vùng 100x100 tại vị trí (50, 50)
select_rectangle("my_art.aseprite", 50, 50, 100, 100)
```

---

### 7.2. `select_all(filename: str) -> str`

**Mô tả:** Select toàn bộ canvas.

**Tham số:**
- `filename` (str): Tên file Aseprite

**Ví dụ:**
```python
select_all("my_art.aseprite")
```

---

### 7.3. `deselect(filename: str) -> str`

**Mô tả:** Bỏ tất cả selection.

**Tham số:**
- `filename` (str): Tên file Aseprite

**Ví dụ:**
```python
deselect("my_art.aseprite")
```

---

### 7.4. `invert_selection(filename: str) -> str`

**Mô tả:** Đảo ngược selection (select tất cả trừ vùng đang select).

**Tham số:**
- `filename` (str): Tên file Aseprite

**Ví dụ:**
```python
invert_selection("my_art.aseprite")
```

---

### 7.5. `delete_selection(filename: str) -> str`

**Mô tả:** Xóa nội dung trong vùng selection (clear thành transparent).

**Tham số:**
- `filename` (str): Tên file Aseprite

**Ví dụ:**
```python
# Select rồi delete
select_rectangle("my_art.aseprite", 10, 10, 50, 50)
delete_selection("my_art.aseprite")
```

---

## 8. Cấu Hình Môi Trường

### Biến Môi Trường (Environment Variables)

Tạo file `.env` từ `sample.env`:

```bash
# Đường dẫn đến Aseprite executable
ASEPRITE_PATH=/path/to/aseprite

# (Optional) Thông tin Steam để cài đặt tự động
STEAM_USERNAME=your_username
STEAM_PASSWORD=your_password
STEAM_GUARD_CODE=your_code

# Cấu hình Steam
STEAM_APPID=431730
STEAM_INSTALL_DIR=/opt/steamapps
```

---

## 9. Docker Setup

### 6.1. Build Docker Image

**Linux/macOS:**
```bash
./build-docker.sh
```

**Windows:**
```powershell
.\build-docker.ps1
```

### 6.2. Run với Docker Compose

**Production:**
```bash
docker-compose up
```

**Development:**
```bash
docker-compose --profile dev up aseprite-mcp-dev
```

### 6.3. Dockerfile Chi Tiết

**Base Image:** ghcr.io/homebrew/brew:latest
**Python Version:** 3.13
**Package Manager:** uv
**Additional Tools:** steamcmd

**Tính năng:**
- Cài đặt Aseprite từ Steam (optional) tại runtime
- Cấu hình qua biến môi trường
- Non-root user support

---

## 10. Cài Đặt Local

### Yêu Cầu
- Python >= 3.13
- Aseprite đã cài đặt

### Các Bước Cài Đặt

1. **Clone repository:**
```bash
git clone <repository-url>
cd aseprite-mcp
```

2. **Cài đặt uv (nếu chưa có):**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. **Cài đặt dependencies:**
```bash
uv sync
```

4. **Chạy server:**
```bash
uv run -m aseprite_mcp
```

---

## 11. Dependencies

### Core Dependencies (pyproject.toml)
- `httpx >= 0.28.1`
- `mcp[cli] >= 1.6.0`

### Development Dependencies (requirements.txt)
- `typing_extensions >= 4.12.2`
- `python-dotenv >= 1.0.0`
- `pytest >= 8.0.0`
- `black >= 24.0.0`
- `flake8 >= 7.0.0`

---

## 12. Cơ Chế Hoạt Động

### 9.1. MCP Server Implementation

- **Server Name:** "aseprite"
- **Transport:** stdio (standard input/output)
- **Framework:** FastMCP
- **Tools Registration:** Decorator `@mcp.tool()`
- **Execution Model:** Asynchronous (async functions)

### 9.2. Lua Script Execution

Tất cả các thao tác sử dụng Lua scripts được thực thi trong batch mode của Aseprite:

1. Python tạo Lua script động
2. Lưu vào file tạm thời
3. Aseprite chạy script trong batch mode
4. Dọn dẹp file tạm

### 9.3. Color Handling

- Input: Hex color codes (vd: "#FF0000")
- Conversion: Hex → RGB trong Python
- Usage: RGB values trong Lua scripts

---

## 13. CI/CD

### GitHub Actions Workflow

**File:** `.github/workflows/docker-build.yml`

**Triggers:**
- Push to `main` / `develop`
- Tags: `v*`
- Pull requests to `main`

**Features:**
- Multi-platform builds (linux/amd64, linux/arm64)
- Auto-publish to GitHub Container Registry
- Build caching
- Metadata extraction

---

## 14. Scripts Tiện Ích

### 11.1. docker-entrypoint.sh

**Chức năng:**
- Kiểm tra Steam credentials
- Cài đặt Aseprite qua Steam (optional)
- Thiết lập ASEPRITE_PATH
- Khởi chạy MCP server

### 11.2. install-aseprite-steam.sh

**Chức năng:**
- Cài đặt Aseprite (App ID: 431730) qua SteamCMD
- Yêu cầu STEAM_USERNAME và STEAM_PASSWORD
- Hỗ trợ STEAM_GUARD_CODE
- Validate installation
- Export ASEPRITE_PATH

---

## 15. Các Lưu Ý Kỹ Thuật

### 12.1. Transaction-based Operations
- Các thao tác layer sử dụng transaction để đảm bảo tính nguyên tử
- Rollback tự động khi có lỗi

### 12.2. File Validation
- Kiểm tra file tồn tại trước khi thực hiện thao tác
- Error handling cho các trường hợp file không hợp lệ

### 12.3. Temporary File Cleanup
- Tất cả file tạm được dọn dẹp tự động
- Sử dụng try-finally để đảm bảo cleanup

### 12.4. Batch Mode Execution
- Aseprite chạy ở background (không GUI)
- Tối ưu cho automation và scripting

---

## 16. Troubleshooting

### Lỗi Thường Gặp

1. **"Aseprite not found"**
   - Kiểm tra ASEPRITE_PATH
   - Đảm bảo Aseprite đã cài đặt đúng

2. **"File not found"**
   - Kiểm tra đường dẫn file
   - Đảm bảo file .aseprite tồn tại

3. **"Lua script execution failed"**
   - Kiểm tra syntax Lua script
   - Xem log output để debug

4. **Docker build failed**
   - Kiểm tra Docker daemon đang chạy
   - Kiểm tra disk space
   - Review build logs

---

## 17. Tài Liệu Tham Khảo

- **README.md**: Hướng dẫn tổng quan và quick start
- **DOCKER.md**: Hướng dẫn Docker chi tiết
- **DOCKER_SETUP_SUMMARY.md**: Tóm tắt Docker implementation
- **License**: MIT License

---

## 18. Roadmap & Future Features

Các tính năng có thể được thêm vào trong tương lai:
- Hỗ trợ nhiều loại brush và texture hơn
- Animation utilities nâng cao
- Palette management
- Sprite sheet generation
- Tích hợp với các AI image generation tools
- WebSocket transport cho real-time updates

---

**Version:** 0.1.0
**Author:** Aseprite MCP Team
**License:** MIT
**Created:** 2026-03-19
