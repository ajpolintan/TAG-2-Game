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
	
	public float Speed;
	
	[Export]
	public float WalkSpeed { get; set; }
	
	[Export]
	public float RunSpeed { get; set; }
	
	public Vector2 input_direction;
	
	public override void _Ready() {
		_actionableFinder = GetNode<Area2D>("ActionableFinder");
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
	} 
	
	// CONNECTED TO PLAYER DEFEATED SIGNAL
	private void OnPlayerDefeated() {
		GD.Print("Player has died!");
		SceneManager.Instance.ChangeScene("res://Scenes/GameOver.tscn");
	}
	
	public async Task Battle()
	{
	 //SkillTree.Instance.UseSkill(
	  SceneManager.Instance.ChangeScene("res://Scenes/Battle.tscn");
	 // GetTree().ChangeSceneToFile("res://Scenes/Battle.tscn");
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
		Velocity = input_direction * Speed;
		MoveAndSlide();
	}
}
