using Godot;
using System;

// Class that manages all the signals. This is a global autoloaded script that can be used anywhere 
public partial class SignalBus : Node
{
	public static SignalBus Instance { get; private set; }
	
	//Signal Used Whenever An Enemy is Defeated
	[Signal]
	public delegate void EnemyDefeatedEventHandler();
	
	[Signal]
	public delegate void PlayerDefeatedEventHandler();
	
	public override void _Ready()
	{
		Instance = this;
	}

	// Called every frame. 'delta' is the elapsed time since the previous frame.
	public override void _Process(double delta)
	{
	}
}
