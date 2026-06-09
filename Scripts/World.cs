using Godot;
using System;

// Class that manages global nodes throughout the World
public partial class World : Node2D
{
	
	public CharacterBody2D character;
	// Called when the node enters the scene tree for the first time.
	public override void _Ready()
	{
		character = GetNode<CharacterBody2D>("Player");
	}

	// Called every frame. 'delta' is the elapsed time since the previous frame.
	public override void _Process(double delta)
	{
	}
}
