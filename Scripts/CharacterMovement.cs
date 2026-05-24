using Godot;
using System;

public partial class CharacterMovement : CharacterBody2D
{
	/// <summary>
	/// Handles the speed of the character movement
	/// </summary>
	
	/// <summary>
	/// ActionableFinder
	/// </summary>
	private Area2D _actionableFinder; 
	
	public float Speed;
	
	[Export]
	public float WalkSpeed { get; set; }
	
	[Export]
	public float RunSpeed { get; set; }
	
	public override void _Ready() {
		_actionableFinder = GetNode<Area2D>("ActionableFinder");
	}
	
	//Get Input Function
	public void GetInput() {
		 if (Input.IsActionJustPressed("interact")) {
			var actionables = _actionableFinder.GetOverlappingAreas();
				GD.Print(actionables.Count);
				if (actionables.Count > 0) {
					Actionable action = (Actionable) actionables[0];
					action.Action();
					return;
				}
		 }
		 Vector2 input_direction = Input.GetVector("left", "right", "up", "down");
		 Velocity = input_direction * Speed;
	} 
	
	//Character speed movement
	public override void _PhysicsProcess(double delta)
	{
		if (Input.IsActionPressed("run"))
		{
			Speed = RunSpeed;
		} else {
			Speed = WalkSpeed;
		}
		GetInput();
		MoveAndSlide();
	}
}
