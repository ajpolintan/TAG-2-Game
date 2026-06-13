using Godot;
using System;

public partial class DamageComponent : Area2D
{
	[Export] 
	public int damage; 
	
	// Called when the node enters the scene tree for the first time.
	public override void _Ready()
	{
		BodyEntered += OnBodyEntered;
	}

	private void OnBodyEntered(Node2D body) {
		GD.Print("Player got damaged!");
		PlayerData.Instance.currentHealth =  PlayerData.Instance.currentHealth - damage;
		GD.Print(PlayerData.Instance.currentHealth);
		GetParent().QueueFree();
	}
}
