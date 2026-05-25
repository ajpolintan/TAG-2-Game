using Godot;
using System;

public partial class SignalBus : Node
{
	public static SignalBus Instance { get; private set; }
	[Signal]
	public delegate void EnemyDefeatedEventHandler();
	
	public override void _Ready()
	{
		Instance = this;
	}

	// Called every frame. 'delta' is the elapsed time since the previous frame.
	public override void _Process(double delta)
	{
	}
}
