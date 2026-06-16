using Godot;
using System;
using System.Threading.Tasks;

public partial class Player : CharacterBody2D
{
	/// <summary>
	/// Handles the speed of the character movement
	/// </summary>
	
	/// <summary>
	/// ActionableFinder
	/// </summary>
	private Area2D _actionableFinder; 
	
	private AnimatedSprite2D _animatedSprite;
	
	public float Speed;
	
	[Export]
	public float WalkSpeed { get; set; }
	
	[Export]
	public float RunSpeed { get; set; }
	
	public Vector2 input_direction;
	
	public override void _Ready() {
		_actionableFinder = GetNode<Area2D>("ActionableFinder");
		_animatedSprite = GetNode<AnimatedSprite2D>("AnimatedSprite2D");
		_animatedSprite.Play("idle");
		SignalBus.Instance.PlayerDefeated += OnPlayerDefeated;

	}
	
	//Get Input from the Nathan Hoad Tutorial
	public override void _UnhandledInput(InputEvent @event) {
		 if (Input.IsActionJustPressed("interact")) {
			var actionables = _actionableFinder.GetOverlappingAreas();
				GD.Print(actionables.Count);
				if (actionables.Count > 0) {
					Actionable action = (Actionable) actionables[0];
					action.Action();
					input_direction = Vector2.Zero;
					return;
				}
		 }
		input_direction = Input.GetVector("left", "right", "up", "down");
		// go right
	
	} 
	
	private void HandleAnimation() {
		if (input_direction.X > 0) {
			_animatedSprite.Play("walk");
			_animatedSprite.FlipH = true;
		} else if  (input_direction.X < 0) {
			_animatedSprite.Play("walk");
			_animatedSprite.FlipH = false;
		} else if (input_direction.Y > 0) {
			_animatedSprite.Play("walk_down");
		} else if (input_direction.Y < 0) {
			_animatedSprite.Play("walk_up");
		} 
		else {
			_animatedSprite.Play("idle");
		}
	}
	
	public async Task Battle()
	{
	  SceneManager.Instance.ChangeScene("res://Scenes/Level2.tscn");
	}
	
	//Character speed movement
	public override void _PhysicsProcess(double delta)
	{
		HandleAnimation();
		if (Input.IsActionPressed("run"))
		{
			Speed = RunSpeed;
		} else {
			Speed = WalkSpeed;
		}
		Velocity = input_direction * Speed;
		MoveAndSlide();
	}
	
	// CONNECTED TO PLAYER DEFEATED SIGNAL
	private void OnPlayerDefeated() {
		GD.Print("Player has died!");
		SceneManager.Instance.ChangeScene("res://Scenes/GameOver.tscn");
	}

}
