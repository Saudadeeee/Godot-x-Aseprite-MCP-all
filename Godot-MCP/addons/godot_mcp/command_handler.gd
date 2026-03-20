@tool
class_name MCPCommandHandler
extends Node

var _websocket_server
var _command_processors = []

func _ready():
	print("Command handler initializing...")
	await get_tree().process_frame
	_websocket_server = get_parent()
	print("WebSocket server reference set: ", _websocket_server)
	
	# Initialize command processors
	_initialize_command_processors()
	
	print("Command handler initialized and ready to process commands")

func _initialize_command_processors():
	# Create and add all command processors
	var node_commands = MCPNodeCommands.new()
	var script_commands = MCPScriptCommands.new()
	var scene_commands = MCPSceneCommands.new()
	var project_commands = MCPProjectCommands.new()
	var editor_commands = MCPEditorCommands.new()
	var editor_script_commands = MCPEditorScriptCommands.new()  # Add our new processor
	var playback_commands = MCPPlaybackCommands.new()
	var project_config_commands = MCPProjectConfigCommands.new()
	var tilemap_commands = MCPTileMapCommands.new()
	var navigation_commands = MCPNavigationCommands.new()
	var particle_commands = MCPParticleCommands.new()
	var environment_commands = MCPEnvironmentCommands.new()
	var animation_tree_commands = MCPAnimationTreeCommands.new()
	var skeleton_commands = MCPSkeletonCommands.new()
	var theme_commands = MCPThemeCommands.new()
	var tween_commands = MCPTweenCommands.new()
	var path_commands = MCPPathCommands.new()
	var mesh_commands = MCPMeshCommands.new()
	var animation_commands = MCPAnimationCommands.new()
	var material_commands = MCPMaterialCommands.new()
	var import_commands = MCPImportCommands.new()

	# Set server reference for all processors
	node_commands._websocket_server = _websocket_server
	script_commands._websocket_server = _websocket_server
	scene_commands._websocket_server = _websocket_server
	project_commands._websocket_server = _websocket_server
	editor_commands._websocket_server = _websocket_server
	editor_script_commands._websocket_server = _websocket_server
	playback_commands._websocket_server = _websocket_server
	project_config_commands._websocket_server = _websocket_server
	tilemap_commands._websocket_server = _websocket_server
	navigation_commands._websocket_server = _websocket_server
	particle_commands._websocket_server = _websocket_server
	environment_commands._websocket_server = _websocket_server
	animation_tree_commands._websocket_server = _websocket_server
	skeleton_commands._websocket_server = _websocket_server
	theme_commands._websocket_server = _websocket_server
	tween_commands._websocket_server = _websocket_server
	path_commands._websocket_server = _websocket_server
	mesh_commands._websocket_server = _websocket_server
	animation_commands._websocket_server = _websocket_server
	material_commands._websocket_server = _websocket_server
	import_commands._websocket_server = _websocket_server

	# Add them to our processor list
	_command_processors.append(node_commands)
	_command_processors.append(script_commands)
	_command_processors.append(scene_commands)
	_command_processors.append(project_commands)
	_command_processors.append(editor_commands)
	_command_processors.append(editor_script_commands)
	_command_processors.append(playback_commands)
	_command_processors.append(project_config_commands)
	_command_processors.append(tilemap_commands)
	_command_processors.append(navigation_commands)
	_command_processors.append(particle_commands)
	_command_processors.append(environment_commands)
	_command_processors.append(animation_tree_commands)
	_command_processors.append(skeleton_commands)
	_command_processors.append(theme_commands)
	_command_processors.append(tween_commands)
	_command_processors.append(path_commands)
	_command_processors.append(mesh_commands)
	_command_processors.append(animation_commands)
	_command_processors.append(material_commands)
	_command_processors.append(import_commands)

	# Add them as children for proper lifecycle management
	add_child(node_commands)
	add_child(script_commands)
	add_child(scene_commands)
	add_child(project_commands)
	add_child(editor_commands)
	add_child(editor_script_commands)
	add_child(playback_commands)
	add_child(project_config_commands)
	add_child(tilemap_commands)
	add_child(navigation_commands)
	add_child(particle_commands)
	add_child(environment_commands)
	add_child(animation_tree_commands)
	add_child(skeleton_commands)
	add_child(theme_commands)
	add_child(tween_commands)
	add_child(path_commands)
	add_child(mesh_commands)
	add_child(animation_commands)
	add_child(material_commands)
	add_child(import_commands)

func _handle_command(client_id: int, command: Dictionary) -> void:
	var command_type = command.get("type", "")
	var params = command.get("params", {})
	var command_id = command.get("commandId", "")
	
	print("Processing command: %s" % command_type)
	
	# Try each processor until one handles the command
	for processor in _command_processors:
		if processor.process_command(client_id, command_type, params, command_id):
			return
	
	# If no processor handled the command, send an error
	_send_error(client_id, "Unknown command: %s" % command_type, command_id)

func _send_error(client_id: int, message: String, command_id: String) -> void:
	var response = {
		"status": "error",
		"message": message
	}
	
	if not command_id.is_empty():
		response["commandId"] = command_id
	
	_websocket_server.send_response(client_id, response)
	print("Error: %s" % message)
