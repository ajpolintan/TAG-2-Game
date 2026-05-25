using Godot;
using System;

public partial class Battle : Control
{
	
	private ProgressBar _enemyHealthBar; 
	private Button _attackButton;

	// Called when the node enters the scene tree for the first time.
	public override void _Ready()
	{
		_enemyHealthBar = GetNode<ProgressBar>("Test");
		_attackButton = GetNode<Button>("PlayerPanel/Actions/Attack");
		
		if (_attackButton != null)
		{
			_attackButton.Pressed += OnAttackButtonPressed;
		}
	}

	public void OnAttackButtonPressed()
	{
		_enemyHealthBar.Value = _enemyHealthBar.Value - 20;
	}
	
	
	// Called every frame. 'delta' is the elapsed time since the previous frame.
	public override void _Process(double delta)
	{
	}
}
