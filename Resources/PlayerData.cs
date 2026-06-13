using Godot;
using System;
using System.Collections.Generic;

//This class will contain all the necesary Data for the Player including hp, xp, unlocked moves etc..
public partial class PlayerData : Node
{
	public int currentXP;
	public int currentHealth;
	public int currentAttack;
	
	//goals have a List of Skill Resources
	// skills [slash, heal, splash]
	// play(slash.animation)

	public static PlayerData Instance { get; private set; } 
	
	
	// Called when the node enters the scene tree for the first time.
	public override void _Ready()
	{
		Instance = this;
		currentHealth = 80; 
	}

	// Called every frame. 'delta' is the elapsed time since the previous frame.
	public override void _Process(double delta)
	{
	}
}
