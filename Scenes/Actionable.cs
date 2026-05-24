using Godot;
using System;
using DialogueManagerRuntime;
using System.Threading.Tasks;

public partial class Actionable : Area2D
{
	[Export] public Resource DialogueResource;
	[Export] public string DialogueString = "start";
	
	public override void _Ready() {
		BodyEntered += OnBodyEntered;
	}
	// goal when player enters this area, you can press space to activate space
	public void Action()
	{
		DialogueManager.ShowDialogueBalloon(DialogueResource, DialogueString);
	}
	
	private void OnBodyEntered(Node2D body) {
		GD.Print("Collided");
	}
}
