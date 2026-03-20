/**
 * Integration test suite for all new MCP command handlers
 * Run: node test_integration.cjs
 */

'use strict';
const WebSocket = require('ws');

const WS_URL = 'ws://localhost:9080';
const CMD_TIMEOUT = 10000;

let ws;
let pass = 0, fail = 0;
let cmdId = 0;
const pending = new Map();

// ─── helpers ─────────────────────────────────────────────────────────────────

function connect() {
  return new Promise((resolve, reject) => {
    ws = new WebSocket(WS_URL, { perMessageDeflate: false });
    const t = setTimeout(() => reject(new Error('Connection timeout')), 8000);
    ws.on('open', () => { clearTimeout(t); resolve(); });
    ws.on('error', err => { clearTimeout(t); reject(err); });
    ws.on('message', raw => {
      try {
        const msg = JSON.parse(raw.toString());
        if (msg.commandId && pending.has(msg.commandId)) {
          const { resolve, timer } = pending.get(msg.commandId);
          clearTimeout(timer);
          pending.delete(msg.commandId);
          resolve(msg);
        }
      } catch {}
    });
  });
}

function cmd(type, params = {}) {
  return new Promise((resolve, reject) => {
    const id = `t${++cmdId}`;
    const timer = setTimeout(() => {
      pending.delete(id);
      reject(new Error(`Timeout: ${type}`));
    }, CMD_TIMEOUT);
    pending.set(id, { resolve, timer });
    ws.send(JSON.stringify({ type, params, commandId: id }));
  });
}

function ok(name) { pass++; console.log(`  ✓ ${name}`); }
function ko(name, msg) { fail++; console.log(`  ✗ ${name} → ${msg}`); }

async function t(name, fn) {
  try {
    const r = await fn();
    if (r && r.status === 'error') { ko(name, r.message || 'error'); }
    else { ok(name); }
    return r;
  } catch (e) { ko(name, e.message); return null; }
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// ─── scene setup ─────────────────────────────────────────────────────────────

async function openScene() {
  const r = await cmd('open_scene', { path: 'res://test_mcp_full.tscn' });
  if (r.status === 'success') {
    console.log('  ✓ Scene opened: test_mcp_full.tscn');
    await sleep(2500);
  } else {
    console.log('  ! WARNING: Could not open scene:', r.message);
    await sleep(500);
  }
}

// ─── Environment & Lighting ───────────────────────────────────────────────────

async function testEnvironment() {
  console.log('\n[Environment & Lighting]');

  await t('set_light_property: light_energy=2.5', () =>
    cmd('set_light_property', { node_path: 'DirectionalLight', property: 'light_energy', value: 2.5 }));

  await t('set_light_property: light_color', () =>
    cmd('set_light_property', { node_path: 'DirectionalLight', property: 'light_color', value: [1.0, 0.9, 0.7, 1.0] }));

  await t('configure_environment: fog_enabled=true', () =>
    cmd('configure_environment', { node_path: 'WorldEnvironment', property: 'fog_enabled', value: true }));

  await t('set_sky: procedural sky', () =>
    cmd('set_sky', {
      node_path: 'WorldEnvironment', sky_type: 'procedural',
      sky_top_color: [0.1, 0.3, 0.8], sky_horizon_color: [0.6, 0.8, 0.9],
      ground_bottom_color: [0.2, 0.15, 0.1]
    }));

  await t('set_fog: enabled + density', () =>
    cmd('set_fog', {
      node_path: 'WorldEnvironment', enabled: true,
      color_r: 0.8, color_g: 0.8, color_b: 0.9, density: 0.01
    }));

  await t('configure_camera: fov=75, perspective', () =>
    cmd('configure_camera', {
      node_path: 'Camera3D', fov: 75.0, near: 0.1, far: 1000.0, projection: 'perspective'
    }));

  await t('get_environment_info', () =>
    cmd('get_environment_info', { node_path: 'WorldEnvironment' }));
}

// ─── Particles ────────────────────────────────────────────────────────────────

async function testParticles() {
  console.log('\n[Particles]');

  await t('configure_particles: amount=500, lifetime=2.0', () =>
    cmd('configure_particles', {
      node_path: 'Particles', amount: 500, lifetime: 2.0,
      speed_scale: 1.5, emitting: false
    }));

  await t('set_particle_material: direction [0,1,0]', () =>
    cmd('set_particle_material', {
      node_path: 'Particles', property: 'direction', value: [0.0, 1.0, 0.0]
    }));

  await t('set_particle_emission_shape: sphere r=2', () =>
    cmd('set_particle_emission_shape', {
      node_path: 'Particles', shape: 'sphere', radius: 2.0
    }));

  await t('restart_particles', () =>
    cmd('restart_particles', { node_path: 'Particles' }));

  await t('get_particle_info', async () => {
    const r = await cmd('get_particle_info', { node_path: 'Particles' });
    if (r.status === 'success') {
      console.log(`     amount=${r.result.amount}, lifetime=${r.result.lifetime}`);
    }
    return r;
  });
}

// ─── Mesh ─────────────────────────────────────────────────────────────────────

async function testMesh() {
  console.log('\n[Mesh / SurfaceTool]');

  await t('create_primitive_mesh: BoxMesh 2x1x0.5', () =>
    cmd('create_primitive_mesh', {
      node_path: 'MeshInstance', mesh_type: 'BoxMesh',
      size_x: 2.0, size_y: 1.0, size_z: 0.5
    }));

  await t('create_primitive_mesh: SphereMesh r=0.75', () =>
    cmd('create_primitive_mesh', {
      node_path: 'MeshInstance', mesh_type: 'SphereMesh',
      size_x: 0.75, size_y: 1.5, radial_segments: 16, rings: 8
    }));

  await t('create_primitive_mesh: CylinderMesh', () =>
    cmd('create_primitive_mesh', {
      node_path: 'MeshInstance', mesh_type: 'CylinderMesh',
      size_x: 0.5, size_y: 2.0
    }));

  await t('create_primitive_mesh: PlaneMesh', () =>
    cmd('create_primitive_mesh', {
      node_path: 'MeshInstance', mesh_type: 'PlaneMesh',
      size_x: 4.0, size_y: 4.0
    }));

  await t('create_primitive_mesh: TorusMesh', () =>
    cmd('create_primitive_mesh', {
      node_path: 'MeshInstance', mesh_type: 'TorusMesh',
      size_x: 1.0, size_y: 0.3
    }));

  await t('create_array_mesh: custom triangle', () =>
    cmd('create_array_mesh', {
      node_path: 'MeshInstance',
      vertices: [0,0,0, 1,0,0, 0.5,1,0],
      normals:  [0,0,1, 0,0,1, 0,0,1],
      uvs:      [0,0,   1,0,   0.5,1],
      primitive_type: 'triangles'
    }));

  await t('get_mesh_info', async () => {
    const r = await cmd('get_mesh_info', { node_path: 'MeshInstance' });
    if (r.status === 'success') console.log(`     surfaces=${r.result.surface_count}`);
    return r;
  });

  await t('create_mesh_from_height_map: 3x3 grid', () =>
    cmd('create_mesh_from_height_map', {
      node_path: 'MeshInstance', width: 3, depth: 3,
      heights: [0,0.5,0, 0.5,1,0.5, 0,0.5,0],
      cell_size: 1.0, height_scale: 1.0
    }));

  await t('generate_mesh_normals: smooth', () =>
    cmd('generate_mesh_normals', { node_path: 'MeshInstance', smooth: true }));

  await t('set_mesh_surface_material: StandardMaterial3D', () =>
    cmd('set_mesh_surface_material', {
      node_path: 'MeshInstance', surface_index: 0, material_type: 'StandardMaterial3D'
    }));

  await t('save_mesh_to_file: .tres', () =>
    cmd('save_mesh_to_file', {
      node_path: 'MeshInstance', save_path: 'res://test_exported_mesh.tres'
    }));
}

// ─── Path ─────────────────────────────────────────────────────────────────────

async function testPath() {
  console.log('\n[Path3D]');

  await t('clear_path', () => cmd('clear_path', { node_path: 'Path3D' }));

  await t('add_path_point: p0 (0,0,0)', () =>
    cmd('add_path_point', { node_path: 'Path3D', x: 0, y: 0, z: 0, out_x: 2 }));

  await t('add_path_point: p1 (5,3,0)', () =>
    cmd('add_path_point', { node_path: 'Path3D', x: 5, y: 3, z: 0, in_x: -2, out_x: 2 }));

  await t('add_path_point: p2 (10,0,0)', () =>
    cmd('add_path_point', { node_path: 'Path3D', x: 10, y: 0, z: 0, in_x: -2 }));

  await t('get_path_info: 3 points + length', async () => {
    const r = await cmd('get_path_info', { node_path: 'Path3D' });
    if (r.status === 'success')
      console.log(`     points=${r.result.point_count}, length=${r.result.baked_length.toFixed(2)}`);
    return r;
  });

  await t('set_path_point: index 1 y=5', () =>
    cmd('set_path_point', { node_path: 'Path3D', index: 1, y: 5.0 }));

  await t('remove_path_point: index 1', () =>
    cmd('remove_path_point', { node_path: 'Path3D', index: 1 }));

  await t('set_curve_baked_resolution: 2.0', () =>
    cmd('set_curve_baked_resolution', { node_path: 'Path3D', bake_interval: 2.0 }));

  // Add PathFollow3D child
  await cmd('create_node', { node_type: 'PathFollow3D', node_name: 'PathFollow', parent_path: 'Path3D' });
  await t('configure_path_follow: progress_ratio=0.5', () =>
    cmd('configure_path_follow', {
      node_path: 'Path3D/PathFollow', progress_ratio: 0.5, loop: false, rotation_mode: 'xyz'
    }));
}

// ─── AnimationTree ────────────────────────────────────────────────────────────

async function testAnimationTree() {
  console.log('\n[AnimationTree]');

  // Ensure animations exist in player
  for (const [name, len] of [['idle', 1.0], ['walk', 0.8], ['run', 0.6]]) {
    const r = await cmd('create_animation', {
      animation_player_path: 'AnimationPlayer', animation_name: name, length: len
    });
    // ignore "already exists" errors
  }

  await t('configure_animation_tree: StateMachine root', () =>
    cmd('configure_animation_tree', {
      tree_path: 'AnimationTree',
      animation_player_path: '../AnimationPlayer',
      active: false,
      root_node_type: 'state_machine'
    }));

  await t('add_animation_tree_node: idle', () =>
    cmd('add_animation_tree_node', {
      tree_path: 'AnimationTree', node_type: 'animation',
      node_name: 'idle', animation_name: 'idle', position_x: 50, position_y: 100
    }));

  await t('add_animation_tree_node: walk', () =>
    cmd('add_animation_tree_node', {
      tree_path: 'AnimationTree', node_type: 'animation',
      node_name: 'walk', animation_name: 'walk', position_x: 250, position_y: 100
    }));

  await t('add_animation_tree_node: run', () =>
    cmd('add_animation_tree_node', {
      tree_path: 'AnimationTree', node_type: 'animation',
      node_name: 'run', animation_name: 'run', position_x: 450, position_y: 100
    }));

  await t('add_state_machine_transition: idle→walk', () =>
    cmd('add_state_machine_transition', {
      tree_path: 'AnimationTree', from_state: 'idle', to_state: 'walk',
      switch_mode: 'immediate', auto_advance: false
    }));

  await t('add_state_machine_transition: walk→run', () =>
    cmd('add_state_machine_transition', {
      tree_path: 'AnimationTree', from_state: 'walk', to_state: 'run',
      switch_mode: 'at_end', auto_advance: false
    }));

  await t('add_state_machine_transition: run→idle', () =>
    cmd('add_state_machine_transition', {
      tree_path: 'AnimationTree', from_state: 'run', to_state: 'idle',
      switch_mode: 'immediate'
    }));

  await t('get_animation_tree_info', async () => {
    const r = await cmd('get_animation_tree_info', { tree_path: 'AnimationTree' });
    if (r.status === 'success')
      console.log(`     root=${r.result.root_type}, states=[${(r.result.states||[]).join(',')}]`);
    return r;
  });

  // BlendTree test
  await cmd('create_node', { node_type: 'AnimationTree', node_name: 'AnimationTreeBlend', parent_path: '.' });
  await t('configure_animation_tree: BlendTree root', () =>
    cmd('configure_animation_tree', {
      tree_path: 'AnimationTreeBlend',
      animation_player_path: '../AnimationPlayer',
      active: false, root_node_type: 'blend_tree'
    }));

  await t('add_animation_tree_node: blend2 output', () =>
    cmd('add_animation_tree_node', {
      tree_path: 'AnimationTreeBlend', node_type: 'animation',
      node_name: 'idle_anim', animation_name: 'idle', position_x: 100, position_y: 100
    }));

  await t('connect_animation_tree_nodes: idle_anim→output', () =>
    cmd('connect_animation_tree_nodes', {
      tree_path: 'AnimationTreeBlend',
      from_node: 'idle_anim', to_node: 'output', to_input: 0
    }));
}

// ─── Theme ────────────────────────────────────────────────────────────────────

async function testTheme() {
  console.log('\n[UI Theme]');
  const THEME = 'res://test_theme_integration.tres';

  await t('create_theme: save to disk', () =>
    cmd('create_theme', { save_path: THEME }));

  await t('set_theme_color: Label/font_color=red', () =>
    cmd('set_theme_color', {
      theme_path: THEME, control_type: 'Label', color_name: 'font_color',
      r: 1.0, g: 0.2, b: 0.2, a: 1.0
    }));

  await t('set_theme_font_size: Button/font_size=18', () =>
    cmd('set_theme_font_size', {
      theme_path: THEME, control_type: 'Button',
      font_size_name: 'font_size', size: 18
    }));

  await t('set_theme_constant: VBoxContainer/separation=10', () =>
    cmd('set_theme_constant', {
      theme_path: THEME, control_type: 'VBoxContainer',
      constant_name: 'separation', value: 10
    }));

  await t('set_theme_stylebox: Button/normal (StyleBoxFlat rounded)', () =>
    cmd('set_theme_stylebox', {
      theme_path: THEME, control_type: 'Button', stylebox_name: 'normal',
      stylebox_type: 'flat', bg_r: 0.2, bg_g: 0.4, bg_b: 0.8, bg_a: 1.0,
      corner_radius: 6, border_width: 1,
      border_r: 1.0, border_g: 1.0, border_b: 1.0, content_margin: 8
    }));

  await t('set_theme_stylebox: Button/hover (StyleBoxFlat)', () =>
    cmd('set_theme_stylebox', {
      theme_path: THEME, control_type: 'Button', stylebox_name: 'hover',
      stylebox_type: 'flat', bg_r: 0.3, bg_g: 0.5, bg_b: 0.9,
      corner_radius: 6, content_margin: 8
    }));

  await t('get_theme_items: verify contents', async () => {
    const r = await cmd('get_theme_items', { theme_path: THEME });
    if (r.status === 'success') {
      const items = r.result;
      const colorCount = Object.keys(items.colors || {}).length;
      const sbCount = Object.keys(items.styleboxes || {}).length;
      console.log(`     colors=${colorCount}, styleboxes=${sbCount}, constants=${Object.keys(items.constants||{}).length}`);
    }
    return r;
  });

  // Assign theme to a Control
  await cmd('create_node', { node_type: 'Control', node_name: 'UIControl', parent_path: '.' });
  await t('assign_theme_to_node: UIControl', () =>
    cmd('assign_theme_to_node', { node_path: 'UIControl', theme_path: THEME }));
}

// ─── Project Config ───────────────────────────────────────────────────────────

async function testProjectConfig() {
  console.log('\n[Project Config]');

  await t('set_project_setting: app name', () =>
    cmd('set_project_setting', {
      setting_name: 'application/config/name', value: 'Godot MCP Test'
    }));

  await t('get_project_setting: app name', async () => {
    const r = await cmd('get_project_setting', { setting_name: 'application/config/name' });
    if (r.status === 'success') console.log(`     value="${r.result.value}"`);
    return r;
  });

  await t('list_project_settings: display/ prefix', async () => {
    const r = await cmd('list_project_settings', { prefix: 'display/' });
    if (r.status === 'success')
      console.log(`     found ${r.result.settings ? r.result.settings.length : 0} settings`);
    return r;
  });

  await t('add_input_action: test_mcp_jump', () =>
    cmd('add_input_action', { action_name: 'test_mcp_jump', deadzone: 0.5 }));

  await t('add_input_event: KEY_SPACE to test_mcp_jump', () =>
    cmd('add_input_event', {
      action_name: 'test_mcp_jump', event_type: 'key', keycode: 'KEY_SPACE'
    }));

  await t('list_input_actions', async () => {
    const r = await cmd('list_input_actions', {});
    if (r.status === 'success')
      console.log(`     ${r.result.action_count} actions total`);
    return r;
  });

  await t('remove_input_action: test_mcp_jump', () =>
    cmd('remove_input_action', { action_name: 'test_mcp_jump' }));

  await t('add_audio_bus: TestMCPBus', () =>
    cmd('add_audio_bus', { bus_name: 'TestMCPBus' }));

  await t('set_bus_volume: -12 dB', () =>
    cmd('set_bus_volume', { bus_index: 1, volume_db: -12.0 }));

  await t('list_audio_buses', async () => {
    const r = await cmd('list_audio_buses', {});
    if (r.status === 'success')
      console.log(`     ${r.result.bus_count} buses: [${(r.result.buses||[]).map(b=>b.name).join(', ')}]`);
    return r;
  });

  await t('set_physics_layer_name: 3d layer_1=Ground', () =>
    cmd('set_physics_layer_name', {
      layer_type: '3d_physics', layer_number: 1, layer_name: 'Ground'
    }));
}

// ─── Import ───────────────────────────────────────────────────────────────────

async function testImport() {
  console.log('\n[Import / Filesystem]');

  await t('list_filesystem_files: res:// non-recursive', async () => {
    const r = await cmd('list_filesystem_files', { path: 'res://', recursive: false });
    if (r.status === 'success')
      console.log(`     count=${r.result.count}`);
    return r;
  });

  await t('scan_filesystem', () => cmd('scan_filesystem', {}));
}

// ─── Playback ─────────────────────────────────────────────────────────────────

async function testPlayback() {
  console.log('\n[Playback Control]');

  await t('get_play_status', async () => {
    const r = await cmd('get_play_status', {});
    if (r.status === 'success')
      console.log(`     is_playing=${r.result.is_playing}`);
    return r;
  });
}

// ─── Navigation ───────────────────────────────────────────────────────────────

async function testNavigation() {
  console.log('\n[Navigation]');

  // Add NavigationRegion3D to the scene
  await cmd('create_node', {
    node_type: 'NavigationRegion3D', node_name: 'NavRegion', parent_path: '.'
  });

  await t('configure_navigation_region: enabled + layers', () =>
    cmd('configure_navigation_region', {
      node_path: 'NavRegion', enabled: true,
      navigation_layers: 1, enter_cost: 0.0, travel_cost: 1.0
    }));

  await t('set_navigation_mesh_property: cell_size=0.25', () =>
    cmd('set_navigation_mesh_property', {
      node_path: 'NavRegion', property: 'cell_size', value: 0.25
    }));

  await t('bake_navigation_mesh', () =>
    cmd('bake_navigation_mesh', { node_path: 'NavRegion' }));

  // Add NavigationAgent3D
  await cmd('create_node', {
    node_type: 'CharacterBody3D', node_name: 'Character', parent_path: '.'
  });
  await cmd('create_node', {
    node_type: 'NavigationAgent3D', node_name: 'NavAgent', parent_path: 'Character'
  });

  await t('get_navigation_agent_info', async () => {
    const r = await cmd('get_navigation_agent_info', {
      agent_path: 'Character/NavAgent'
    });
    if (r.status === 'success')
      console.log(`     class=${r.result.node_class}`);
    return r;
  });

  await t('set_navigation_target', () =>
    cmd('set_navigation_target', {
      agent_path: 'Character/NavAgent',
      target_x: 10.0, target_y: 0.0, target_z: 10.0
    }));
}

// ─── Skeleton ─────────────────────────────────────────────────────────────────

async function testSkeleton() {
  console.log('\n[Skeleton / IK]');

  // Add Skeleton3D
  await cmd('create_node', {
    node_type: 'Skeleton3D', node_name: 'Skeleton3D', parent_path: '.'
  });

  await t('get_skeleton_info: empty skeleton', async () => {
    const r = await cmd('get_skeleton_info', { node_path: 'Skeleton3D' });
    if (r.status === 'success')
      console.log(`     bone_count=${r.result.bone_count}`);
    return r;
  });

  await t('reset_bone_poses: empty skeleton', () =>
    cmd('reset_bone_poses', { node_path: 'Skeleton3D' }));

  // Add SkeletonIK3D
  await cmd('create_node', {
    node_type: 'SkeletonIK3D', node_name: 'SkeletonIK3D', parent_path: 'Skeleton3D'
  });

  await t('configure_skeleton_ik', () =>
    cmd('configure_skeleton_ik', {
      ik_node_path: 'Skeleton3D/SkeletonIK3D',
      max_iterations: 10,
      min_distance: 0.01,
      interpolation: 1.0
    }));
}

// ─── Tween ────────────────────────────────────────────────────────────────────

async function testTween() {
  console.log('\n[Tween]');

  await t('create_tween_script: position ease_in_out', async () => {
    const r = await cmd('create_tween_script', {
      node_path: 'MeshInstance', property: 'position',
      to_value: [5.0, 0.0, 0.0], duration: 1.5,
      ease_type: 'ease_in_out', loop: false
    });
    if (r.status === 'success' && r.result.code)
      console.log(`     code lines=${r.result.code.split('\n').length}`);
    return r;
  });

  await t('animate_node_property: MeshInstance.position', () =>
    cmd('animate_node_property', {
      node_path: 'MeshInstance', property: 'position',
      from_value: [0, 0, 0], to_value: [5, 2, 0],
      duration: 1.0, ease_type: 'ease_in_out'
    }));

  await t('animate_node_property: MeshInstance.scale', () =>
    cmd('animate_node_property', {
      node_path: 'MeshInstance', property: 'scale',
      from_value: [1, 1, 1], to_value: [2, 2, 2],
      duration: 0.5, ease_type: 'ease_out'
    }));
}

// ─── Legacy: existing tools regression ───────────────────────────────────────

async function testExistingTools() {
  console.log('\n[Regression: Existing Tools]');

  await t('list_nodes: scene root', async () => {
    const r = await cmd('list_nodes', { parent_path: '.' });
    if (r.status === 'success')
      console.log(`     ${r.result.nodes ? r.result.nodes.length : 0} root nodes`);
    return r;
  });

  await t('create_animation: test_anim', () =>
    cmd('create_animation', {
      animation_player_path: 'AnimationPlayer',
      animation_name: 'test_legacy', length: 2.0
    }));

  await t('list_animations', async () => {
    const r = await cmd('list_animations', { animation_player_path: 'AnimationPlayer' });
    if (r.status === 'success')
      console.log(`     animations: [${(r.result.animations||[]).join(', ')}]`);
    return r;
  });

  await t('set_tile_cell: (no TileMap - expect error)', async () => {
    const r = await cmd('set_tile_cell', {
      tilemap_path: 'NonExistentTileMap', layer: 0,
      coords_x: 0, coords_y: 0, source_id: 0, atlas_coords_x: 0, atlas_coords_y: 0
    });
    // Expected error because no TileMap - that's correct behavior
    if (r.status === 'error') return { status: 'success' };
    return r;
  });
}

// ─── Main ─────────────────────────────────────────────────────────────────────

async function main() {
  console.log('\n╔═══════════════════════════════════════════════════════╗');
  console.log('║   GODOT-MCP FULL INTEGRATION TEST SUITE               ║');
  console.log('║   Connecting to ws://localhost:9080 ...                ║');
  console.log('╚═══════════════════════════════════════════════════════╝');

  try {
    await connect();
    console.log('\n  Connected to Godot WebSocket server ✓');
  } catch (e) {
    console.error(`\n  FATAL: Cannot connect to Godot → ${e.message}`);
    console.error('  Ensure: Godot editor is running + MCP addon enabled');
    process.exit(1);
  }

  await openScene();

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
  await testSkeleton();
  await testTween();
  await testExistingTools();

  const total = pass + fail;
  console.log('\n╔═══════════════════════════════════════════════════════╗');
  console.log(`║  RESULTS: ${String(pass).padEnd(3)} PASSED / ${String(fail).padEnd(3)} FAILED / ${String(total).padEnd(3)} TOTAL`.padEnd(56) + '║');
  if (fail === 0) {
    console.log('║  ALL TESTS PASSED ✓                                   ║');
  } else {
    console.log(`║  ${fail} test(s) FAILED - see ✗ above for details`.padEnd(56) + '║');
  }
  console.log('╚═══════════════════════════════════════════════════════╝\n');

  ws.close();
  process.exit(fail > 0 ? 1 : 0);
}

main().catch(e => { console.error('Fatal:', e); process.exit(1); });
