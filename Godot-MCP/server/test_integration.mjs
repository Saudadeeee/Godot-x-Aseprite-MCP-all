/**
 * Integration test suite for all new MCP command handlers
 * Connects directly to Godot WebSocket server on port 9080
 * Run with: node test_integration.mjs
 */

import WebSocket from 'ws';

const WS_URL = 'ws://localhost:9080';
const TIMEOUT_MS = 8000;

let ws;
let pass = 0;
let fail = 0;
let commandId = 0;
const pending = new Map();

// ─── WebSocket helpers ───────────────────────────────────────────────────────

function connect() {
  return new Promise((resolve, reject) => {
    ws = new WebSocket(WS_URL);
    ws.on('open', () => resolve());
    ws.on('error', err => reject(err));
    ws.on('message', raw => {
      try {
        const msg = JSON.parse(raw.toString());
        const id = msg.commandId;
        if (id && pending.has(id)) {
          const { resolve } = pending.get(id);
          pending.delete(id);
          resolve(msg);
        }
      } catch {}
    });
  });
}

function sendCommand(type, params = {}) {
  return new Promise((resolve, reject) => {
    const id = `test_${++commandId}`;
    const timer = setTimeout(() => {
      pending.delete(id);
      reject(new Error(`Timeout after ${TIMEOUT_MS}ms for command: ${type}`));
    }, TIMEOUT_MS);

    pending.set(id, {
      resolve: (msg) => {
        clearTimeout(timer);
        resolve(msg);
      }
    });

    ws.send(JSON.stringify({ type, params, commandId: id }));
  });
}

// ─── Test helpers ────────────────────────────────────────────────────────────

function ok(name) {
  pass++;
  console.log(`  ✓ PASS: ${name}`);
}

function err(name, msg) {
  fail++;
  console.log(`  ✗ FAIL: ${name} → ${msg}`);
}

async function test(name, fn) {
  try {
    const result = await fn();
    if (result && result.status === 'error') {
      err(name, result.message || 'Server returned error');
    } else {
      ok(name);
    }
    return result;
  } catch (e) {
    err(name, e.message);
    return null;
  }
}

// ─── Open test scene ─────────────────────────────────────────────────────────

async function openTestScene() {
  const r = await sendCommand('open_scene', { path: 'res://test_mcp_full.tscn' });
  if (r.status === 'success') {
    console.log('  Scene opened: test_mcp_full.tscn');
    // Give editor time to fully load scene
    await new Promise(r => setTimeout(r, 3000));
    console.log('  Scene ready.\n');
  } else {
    console.log('  WARNING: Could not open test scene:', r.message);
    console.log('  Please open test_mcp_full.tscn manually in the editor\n');
    await new Promise(r => setTimeout(r, 2000));
  }
}

// ─── Tests ───────────────────────────────────────────────────────────────────

async function testEnvironment() {
  console.log('[Environment & Lighting]');

  await test('set_light_property: light_energy', () =>
    sendCommand('set_light_property', { node_path: 'DirectionalLight', property: 'light_energy', value: 2.5 })
  );

  await test('set_light_property: light_color', () =>
    sendCommand('set_light_property', { node_path: 'DirectionalLight', property: 'light_color', value: [1.0, 0.9, 0.7, 1.0] })
  );

  await test('configure_environment: fog_enabled', () =>
    sendCommand('configure_environment', { node_path: 'WorldEnvironment', property: 'fog_enabled', value: true })
  );

  await test('set_sky: procedural', () =>
    sendCommand('set_sky', {
      node_path: 'WorldEnvironment',
      sky_type: 'procedural',
      sky_top_color: [0.2, 0.4, 0.8],
      sky_horizon_color: [0.7, 0.8, 0.9],
      ground_bottom_color: [0.3, 0.2, 0.1]
    })
  );

  await test('set_fog: density + color', () =>
    sendCommand('set_fog', {
      node_path: 'WorldEnvironment',
      enabled: true,
      color_r: 0.8, color_g: 0.8, color_b: 0.9,
      density: 0.01
    })
  );

  await test('configure_camera: fov + projection', () =>
    sendCommand('configure_camera', {
      node_path: 'Camera3D',
      fov: 75.0,
      near: 0.1,
      far: 1000.0,
      projection: 'perspective'
    })
  );

  await test('get_environment_info', () =>
    sendCommand('get_environment_info', { node_path: 'WorldEnvironment' })
  );
}

async function testParticles() {
  console.log('\n[Particles]');

  await test('configure_particles: amount + lifetime', () =>
    sendCommand('configure_particles', {
      node_path: 'Particles',
      amount: 500,
      lifetime: 2.0,
      speed_scale: 1.5,
      one_shot: false,
      emitting: false
    })
  );

  await test('set_particle_material: direction', () =>
    sendCommand('set_particle_material', {
      node_path: 'Particles',
      property: 'direction',
      value: [0.0, 1.0, 0.0]
    })
  );

  await test('set_particle_emission_shape: sphere', () =>
    sendCommand('set_particle_emission_shape', {
      node_path: 'Particles',
      shape: 'sphere',
      radius: 2.0
    })
  );

  await test('get_particle_info', () =>
    sendCommand('get_particle_info', { node_path: 'Particles' })
  );
}

async function testMesh() {
  console.log('\n[Mesh / SurfaceTool]');

  await test('create_primitive_mesh: BoxMesh', () =>
    sendCommand('create_primitive_mesh', {
      node_path: 'MeshInstance',
      mesh_type: 'BoxMesh',
      size_x: 2.0,
      size_y: 1.0,
      size_z: 0.5
    })
  );

  await test('create_primitive_mesh: SphereMesh', () =>
    sendCommand('create_primitive_mesh', {
      node_path: 'MeshInstance',
      mesh_type: 'SphereMesh',
      size_x: 0.75,
      size_y: 1.5,
      radial_segments: 16,
      rings: 8
    })
  );

  await test('create_primitive_mesh: CylinderMesh', () =>
    sendCommand('create_primitive_mesh', {
      node_path: 'MeshInstance',
      mesh_type: 'CylinderMesh',
      size_x: 0.5,
      size_y: 2.0
    })
  );

  await test('create_array_mesh: triangle', () =>
    sendCommand('create_array_mesh', {
      node_path: 'MeshInstance',
      vertices: [0,0,0, 1,0,0, 0.5,1,0],
      normals:  [0,0,1, 0,0,1, 0,0,1],
      uvs:      [0,0,   1,0,   0.5,1],
      primitive_type: 'triangles'
    })
  );

  await test('get_mesh_info', () =>
    sendCommand('get_mesh_info', { node_path: 'MeshInstance' })
  );

  await test('create_mesh_from_height_map: 3x3', () =>
    sendCommand('create_mesh_from_height_map', {
      node_path: 'MeshInstance',
      width: 3, depth: 3,
      heights: [0,0.5,0, 0.5,1,0.5, 0,0.5,0],
      cell_size: 1.0,
      height_scale: 1.0
    })
  );

  await test('generate_mesh_normals: smooth', () =>
    sendCommand('generate_mesh_normals', { node_path: 'MeshInstance', smooth: true })
  );

  await test('set_mesh_surface_material: StandardMaterial3D', () =>
    sendCommand('set_mesh_surface_material', {
      node_path: 'MeshInstance',
      surface_index: 0,
      material_type: 'StandardMaterial3D'
    })
  );

  await test('save_mesh_to_file', () =>
    sendCommand('save_mesh_to_file', {
      node_path: 'MeshInstance',
      save_path: 'res://test_exported_mesh.tres'
    })
  );
}

async function testPath() {
  console.log('\n[Path3D]');

  await test('clear_path', () =>
    sendCommand('clear_path', { node_path: 'Path3D' })
  );

  await test('add_path_point: point 1', () =>
    sendCommand('add_path_point', { node_path: 'Path3D', x: 0, y: 0, z: 0, out_x: 2, out_y: 0, out_z: 0 })
  );

  await test('add_path_point: point 2', () =>
    sendCommand('add_path_point', { node_path: 'Path3D', x: 5, y: 3, z: 0, in_x: -2, in_y: 0, in_z: 0, out_x: 2, out_y: 0, out_z: 0 })
  );

  await test('add_path_point: point 3', () =>
    sendCommand('add_path_point', { node_path: 'Path3D', x: 10, y: 0, z: 0, in_x: -2, in_y: 0, in_z: 0 })
  );

  await test('get_path_info: 3 points', () =>
    sendCommand('get_path_info', { node_path: 'Path3D' })
  );

  await test('set_path_point: modify index 1', () =>
    sendCommand('set_path_point', { node_path: 'Path3D', index: 1, y: 5.0 })
  );

  await test('remove_path_point: remove index 1', () =>
    sendCommand('remove_path_point', { node_path: 'Path3D', index: 1 })
  );

  await test('set_curve_baked_resolution: 2.0', () =>
    sendCommand('set_curve_baked_resolution', { node_path: 'Path3D', bake_interval: 2.0 })
  );
}

async function testAnimationTree() {
  console.log('\n[AnimationTree]');

  // First create animations in the player
  await sendCommand('create_animation', {
    animation_player_path: 'AnimationPlayer',
    animation_name: 'idle',
    length: 1.0
  });
  await sendCommand('create_animation', {
    animation_player_path: 'AnimationPlayer',
    animation_name: 'walk',
    length: 0.8
  });

  await test('configure_animation_tree: state_machine root', () =>
    sendCommand('configure_animation_tree', {
      tree_path: 'AnimationTree',
      animation_player_path: '../AnimationPlayer',
      active: false,
      root_node_type: 'state_machine'
    })
  );

  await test('add_animation_tree_node: idle', () =>
    sendCommand('add_animation_tree_node', {
      tree_path: 'AnimationTree',
      node_type: 'animation',
      node_name: 'idle',
      animation_name: 'idle',
      position_x: 100, position_y: 100
    })
  );

  await test('add_animation_tree_node: walk', () =>
    sendCommand('add_animation_tree_node', {
      tree_path: 'AnimationTree',
      node_type: 'animation',
      node_name: 'walk',
      animation_name: 'walk',
      position_x: 300, position_y: 100
    })
  );

  await test('add_state_machine_transition: idle→walk', () =>
    sendCommand('add_state_machine_transition', {
      tree_path: 'AnimationTree',
      from_state: 'idle',
      to_state: 'walk',
      switch_mode: 'immediate',
      auto_advance: false
    })
  );

  await test('get_animation_tree_info', () =>
    sendCommand('get_animation_tree_info', { tree_path: 'AnimationTree' })
  );
}

async function testTheme() {
  console.log('\n[UI Theme]');

  await test('create_theme: save to disk', () =>
    sendCommand('create_theme', { save_path: 'res://test_theme_integration.tres' })
  );

  await test('set_theme_color: Label/font_color', () =>
    sendCommand('set_theme_color', {
      theme_path: 'res://test_theme_integration.tres',
      control_type: 'Label',
      color_name: 'font_color',
      r: 1.0, g: 0.2, b: 0.2, a: 1.0
    })
  );

  await test('set_theme_font_size: Button/font_size = 18', () =>
    sendCommand('set_theme_font_size', {
      theme_path: 'res://test_theme_integration.tres',
      control_type: 'Button',
      font_size_name: 'font_size',
      size: 18
    })
  );

  await test('set_theme_constant: VBoxContainer/separation = 10', () =>
    sendCommand('set_theme_constant', {
      theme_path: 'res://test_theme_integration.tres',
      control_type: 'VBoxContainer',
      constant_name: 'separation',
      value: 10
    })
  );

  await test('set_theme_stylebox: Button/normal (StyleBoxFlat)', () =>
    sendCommand('set_theme_stylebox', {
      theme_path: 'res://test_theme_integration.tres',
      control_type: 'Button',
      stylebox_name: 'normal',
      stylebox_type: 'flat',
      bg_r: 0.2, bg_g: 0.4, bg_b: 0.8, bg_a: 1.0,
      corner_radius: 6,
      border_width: 1,
      border_r: 1.0, border_g: 1.0, border_b: 1.0,
      content_margin: 8
    })
  );

  await test('get_theme_items', () =>
    sendCommand('get_theme_items', { theme_path: 'res://test_theme_integration.tres' })
  );
}

async function testProjectConfig() {
  console.log('\n[Project Config]');

  await test('set_project_setting: window_title', () =>
    sendCommand('set_project_setting', {
      setting_name: 'application/config/name',
      value: 'MCP Test Project'
    })
  );

  const r = await test('get_project_setting', () =>
    sendCommand('get_project_setting', { setting_name: 'application/config/name' })
  );

  await test('add_input_action: test_jump', () =>
    sendCommand('add_input_action', { action_name: 'test_mcp_jump', deadzone: 0.5 })
  );

  await test('add_input_event: KEY_SPACE', () =>
    sendCommand('add_input_event', {
      action_name: 'test_mcp_jump',
      event_type: 'key',
      keycode: 'KEY_SPACE'
    })
  );

  await test('list_input_actions', () =>
    sendCommand('list_input_actions', {})
  );

  await test('remove_input_action: test_jump', () =>
    sendCommand('remove_input_action', { action_name: 'test_mcp_jump' })
  );

  await test('add_audio_bus: TestBus', () =>
    sendCommand('add_audio_bus', { bus_name: 'TestBus' })
  );

  await test('set_bus_volume: -12 dB', () =>
    sendCommand('set_bus_volume', { bus_index: 1, volume_db: -12.0 })
  );

  await test('list_audio_buses', () =>
    sendCommand('list_audio_buses', {})
  );

  await test('set_physics_layer_name: 3d layer_1 = Ground', () =>
    sendCommand('set_physics_layer_name', {
      layer_type: '3d_physics',
      layer_number: 1,
      layer_name: 'Ground'
    })
  );
}

async function testImport() {
  console.log('\n[Import / Filesystem]');

  await test('list_filesystem_files: res://', () =>
    sendCommand('list_filesystem_files', { path: 'res://', recursive: false })
  );

  await test('scan_filesystem', () =>
    sendCommand('scan_filesystem', {})
  );
}

async function testPlayback() {
  console.log('\n[Playback Control]');

  await test('get_play_status', () =>
    sendCommand('get_play_status', {})
  );
}

async function testNavigation() {
  console.log('\n[Navigation]');

  // Add a NavigationRegion3D node first
  const addResult = await sendCommand('create_node', {
    node_type: 'NavigationRegion3D',
    node_name: 'NavRegion',
    parent_path: '.'
  });

  await test('configure_navigation_region: enabled', () =>
    sendCommand('configure_navigation_region', {
      node_path: 'NavRegion',
      enabled: true,
      navigation_layers: 1
    })
  );

  await test('set_navigation_mesh_property: cell_size', () =>
    sendCommand('set_navigation_mesh_property', {
      node_path: 'NavRegion',
      property: 'cell_size',
      value: 0.5
    })
  );

  await test('get_navigation_agent_info: (no agent, should error gracefully)', async () => {
    const r = await sendCommand('get_navigation_agent_info', { agent_path: 'NavAgentXXX_nonexistent' });
    // Expect an error since node doesn't exist - that's correct behavior
    if (r.status === 'error') return { status: 'success' };
    return r;
  });
}

async function testTween() {
  console.log('\n[Tween]');

  await test('create_tween_script: position tween', () =>
    sendCommand('create_tween_script', {
      node_path: 'MeshInstance',
      property: 'position',
      to_value: [5.0, 0.0, 0.0],
      duration: 1.0,
      ease_type: 'ease_in_out'
    })
  );

  await test('animate_node_property: MeshInstance.position', () =>
    sendCommand('animate_node_property', {
      node_path: 'MeshInstance',
      property: 'position',
      from_value: [0, 0, 0],
      to_value: [5, 0, 0],
      duration: 1.0,
      ease_type: 'ease_in_out'
    })
  );
}

// ─── Main ─────────────────────────────────────────────────────────────────────

async function main() {
  console.log('');
  console.log('═══════════════════════════════════════════════════════');
  console.log('  GODOT-MCP INTEGRATION TEST SUITE');
  console.log('  Connecting to ws://localhost:9080 ...');
  console.log('═══════════════════════════════════════════════════════\n');

  try {
    await connect();
    console.log('  Connected to Godot WebSocket server ✓\n');
  } catch (e) {
    console.error(`  FATAL: Cannot connect to Godot - ${e.message}`);
    console.error('  Make sure:');
    console.error('    1. Godot editor is running');
    console.error('    2. MCP addon is enabled (Project > Project Settings > Plugins)');
    process.exit(1);
  }

  await openTestScene();

  // Run all test categories
  await testEnvironment();
  await testParticles();
  await testMesh();
  await testPath();
  await testAnimationTree();
  await testTheme();
  await testProjectConfig();
  await testImport();
  await testPlayback();
  await testNavigation();
  await testTween();

  // Results
  const total = pass + fail;
  console.log('\n═══════════════════════════════════════════════════════');
  console.log(`  RESULTS: ${pass} PASSED / ${fail} FAILED / ${total} TOTAL`);
  if (fail === 0) {
    console.log('  ALL TESTS PASSED ✓');
  } else {
    console.log(`  ${fail} TESTS FAILED ✗`);
  }
  console.log('═══════════════════════════════════════════════════════\n');

  ws.close();
  process.exit(fail > 0 ? 1 : 0);
}

main().catch(e => {
  console.error('Unhandled error:', e);
  process.exit(1);
});
