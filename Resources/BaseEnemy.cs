using Godot;
using System;

public partial class BaseEnemy : Resource
{
	/// <summary>
	/// Name of the Item
	/// </summary>
	[Export] public string name { get; set; }
	[Export] public Texture2D texture { get; set; }
	[Export] public int health { get; set; }
	[Export] public int damage { get; set; }
	
	public BaseEnemy() {
		name = "";
		texture = null;
		health = 0;
		damage = 0;
	}
}
