using Godot;
using System;
	/// <summary>
	/// The main menu when you launch the game. When you push Play Game the first level will load.
	/// </summary>
public partial class MainMenu : Node
{
	/// <summary>
	/// TargetScene is the next scene to load when pushing the button. Just drag and drop the scene
	/// into the MainMenu TargetScene setting in the Inspector.
	/// </summary>
	[Export]
	public PackedScene TargetScene { get; set; }

	/// <summary>
	/// When the scene is first ran this code is executed. Here the PlayButton is found and connects 
	/// to the OnButtonPressed() function.
	/// </summary>
	public override void _Ready()
	{
		Button button = GetNode<Button>("PlayButton"); 
		if (button != null)
		{
			button.Pressed += OnButtonPressed;
		}
	}

	/// <summary>
	/// When the button is pressed this function runs and changes scene to the 
	/// target scene.
	/// </summary>
	private void OnButtonPressed()
	{
		SceneManager.Instance.ChangeScene("res://Scenes/Main.tscn");

	}
}
