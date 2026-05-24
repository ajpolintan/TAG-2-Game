using Godot;
using System;
/// <summary>
/// The Pause Menu is a canvas Layer that appears when ESC is pressed.
/// It pauses the game.
/// </summary>
public partial class PauseMenu : CanvasLayer
{
	/// <summary>
	/// Called when the node enters the scene tree.
	/// </summary>
	public override void _Ready()
	{
		GetNode<Button>("VBoxContainer/ResumeButton").Pressed += OnResumePressed;
		GetNode<Button>("VBoxContainer/QuitButton").Pressed += OnQuitPressed;
	}

	/// <summary>
	/// Reads input that GODOT provides.
	/// </summary>
	/// <param name="inputEvent"> The keypress detected. </param>
	public override void _Input(InputEvent inputEvent)
	{
		if (inputEvent.IsActionPressed("exit_pause_menu"))
		{
			GD.Print("Escape is pressed!");
			if (GetTree().Paused)
			{
				ResumeGame();
			}
			else
			{
				PauseGame();
			}
		}
	}
	/// <summary>
	/// Sets game to pause state and makes the PauseMenu visable.
	/// </summary>
	private void PauseGame()
	{
		GetTree().Paused = true;
		Visible = true;
	}
	/// <summary>
	/// Unpauses the game and makes the PauseMenu disappear.
	/// </summary>
	private void ResumeGame()
	{
		GetTree().Paused = false;
		Visible = false;
	}
	/// <summary>
	/// Connects to the resume game button and resumes the game.
	/// </summary>
	private void OnResumePressed()
	{
		ResumeGame();
	}
	/// <summary>
	/// Connects to Quit button and exits the game.
	/// </summary>
	private void OnQuitPressed()
	{
		GetTree().Quit();
	}
}
