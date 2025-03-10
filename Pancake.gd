extends Area2D

var dragging = false

func _input_event(viewport, event, shape_idx):
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
		dragging = event.pressed  # True on press, false on release

func _process(delta):
	if dragging:
		position = get_global_mouse_position()
