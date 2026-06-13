using Godot;
using System;

public partial class BaseSkill : Resource
{
	
	/// Create An Array for Skills
	/// <summary>
	/// Name of the Item
	/// </summary>
	[Export] public string name { get; set; }
	[Export] public Texture2D texture { get; set; }
	
	public BaseSkill() {
		name = "";
		texture = null;
	}
	

}
