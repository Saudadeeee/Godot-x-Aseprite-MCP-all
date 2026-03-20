# Testing Guide

## Prerequisites

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Set Aseprite path:**
   ```bash
   # Windows
   set ASEPRITE_PATH=C:\Path\To\Aseprite.exe

   # Linux/macOS
   export ASEPRITE_PATH=/path/to/aseprite
   ```

## Running Tests

### Quick Test (5 functions)
```bash
uv run tests/quick_test.py
```

This runs a quick smoke test with:
- Create canvas
- Set layer opacity
- Rename layer
- Create palette
- Make selection

**Output:** Creates `quick_test.aseprite` you can open in Aseprite.

---

### Full Phase 1 Test (16 functions)
```bash
uv run tests/test_phase1.py
```

This tests all 16 Phase 1 functions:
- ✅ 6 Layer operations
- ✅ 4+ Palette operations
- ✅ 5 Selection operations

**Output:** Creates `test_canvas.aseprite` with visual results.

---

## Manual Testing

You can also test functions manually via MCP server:

1. **Start the MCP server:**
   ```bash
   uv run -m aseprite_mcp
   ```

2. **Use with Claude Desktop** or any MCP client

3. **Test commands like:**
   - "Create a 200x200 canvas named test.aseprite"
   - "Set the opacity of Layer 1 to 128"
   - "Create a palette with colors #FF0000, #00FF00, #0000FF"

---

## Troubleshooting

### "Aseprite not found"
- Check `ASEPRITE_PATH` environment variable
- Verify Aseprite is installed
- Try full path: `export ASEPRITE_PATH=/usr/local/bin/aseprite`

### "ModuleNotFoundError: No module named 'mcp'"
- Run `uv sync` to install dependencies

### Test file not created
- Check Aseprite is working: `aseprite --version`
- Check write permissions in test directory
- Run with verbose output: `uv run tests/quick_test.py --verbose`

---

## Test Coverage

### Phase 1 (✅ Implemented)
- [x] Layer operations (6 functions)
- [x] Palette management (5 functions)
- [x] Selection operations (5 functions)

### Phase 2 (🚧 In Progress)
- [ ] Image transformation (8 functions)
- [ ] Advanced drawing (7 functions)
- [ ] Cel operations (5 functions)
- [ ] Sprite sheet export (4 functions)

---

## Writing New Tests

Add tests to `tests/test_phase2.py`:

```python
async def test_new_function():
    result = await your_function(args)
    assert "Success" in result
```

Run with:
```bash
uv run tests/test_phase2.py
```
