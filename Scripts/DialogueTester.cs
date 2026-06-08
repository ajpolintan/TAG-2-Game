using Godot;
using DialogueManagerRuntime;
using System;
using System.Threading.Tasks;


public partial class DialogueTester : Node
{
	private Resource dialogue = GD.Load<Resource>("res://Dialogue/test.dialogue");
	// Called when the node enters the scene tree for the first time.
	public override void _Ready()
	{
		//function that starts the dialgoue
		DialogueManager.ShowDialogueBalloon(dialogue, "start");
	}

	// Called every frame. 'delta' is the elapsed time since the previous frame.
	public override void _Process(double delta)
	{
	}	
}
