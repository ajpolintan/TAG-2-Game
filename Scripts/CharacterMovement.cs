using Godot;
using System;

public partial class CharacterMovement : CharacterBody2D
{
	/// <summary>
	/// Handles the speed of the character movement
	/// </summary>
	
	public float Speed;
	
	[Export]
	public float WalkSpeed { get; set; }
	
	[Export]
	public float RunSpeed { get; set; }
	
	//Get Input Function
	public void GetInput() {
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
