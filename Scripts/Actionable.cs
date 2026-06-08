using Godot;
using System;
using DialogueManagerRuntime;
using System.Threading.Tasks;

public partial class Actionable : Area2D
{
	//Dialogue Resources
	[Export] public Resource DialogueResource;
	[Export] public string DialogueString = "start";
	
	//Connecting Sign
	public override void _Ready() {
		BodyEntered += OnBodyEntered;
	}
	// goal when player enters this area, you can press space to activate space
	public void Action()
	{
		GD.Print("action!");
		DialogueManager.ShowDialogueBalloon(DialogueResource, DialogueString);
	}
	
		

	
	private void OnBodyEntered(Node2D body) {
		GD.Print("Collided");
		if (Input.IsActionPressed("interact")) {
			GD.Print("button pressed");
			Action();
		}
		//if player presses the space button, the action function should activate
	}
}
