using Godot;

public class DraggableObject : Area2D
{
	private bool dragging = false;

	public override void _InputEvent(Viewport viewport, InputEvent @event, int shapeIdx)
	{
		if (@event is InputEventMouseButton mouseEvent && mouseEvent.ButtonIndex == (int)ButtonList.Left)
		{
			dragging = mouseEvent.Pressed; // True on press, false on release
		}
	}

	public override void _Process(float delta)
	{
		if (dragging)
		{
			Position = GetGlobalMousePosition();
		}
	}
}
