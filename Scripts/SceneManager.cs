using Godot;
using System;
using System.Threading.Tasks;

// This class handles all the transitions between scenes
public partial class SceneManager : CanvasLayer
{
	
	public static SceneManager Instance { get; private set; }
	
	AnimationPlayer animPlayer;
	ColorRect transitionColor;
	// Called when the node enters the scene tree for the first time.
	public override void _Ready()
	{
		
		Instance = this;
		animPlayer = GetNode<AnimationPlayer>("TransitionAnimation");
		transitionColor = GetNode<ColorRect>("TransitionColor");
		transitionColor.Visible = false;
	}

	//Running this will change the scene and also will affect transitions
	public async Task ChangeScene(string scene) {
		transitionColor.Visible = true;
		animPlayer.Play("transition_out");
		//Wait until Animation is finished to Change Scene
		await ToSignal(animPlayer, AnimationPlayer.SignalName.AnimationFinished);
		SignalBus.Instance.EmitSignal(SignalBus.SignalName.ClearLevel);
		GetTree().ChangeSceneToFile(scene);
		animPlayer.PlayBackwards("transition_out");
		await ToSignal(animPlayer, AnimationPlayer.SignalName.AnimationFinished);
		transitionColor.Visible = false;
	}
}
