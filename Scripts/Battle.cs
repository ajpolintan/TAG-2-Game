using Godot;
using System;

public partial class Battle : Control
{

	/// <summary>
	/// Enemy Resource
	/// </summary>
	[Export]
	public BaseEnemy Enemy { get; set; }
	
	private ProgressBar _enemyHealthBar; 
	private ProgressBar _playerHealthBar;

	private Button _attackButton;
	private Button _runButton;
	
	private Label _enemyName;
	private Sprite2D _enemyTexture;
	
	// Called when the node enters the scene tree for the first time.
	public override void _Ready()
	{
		 SignalBus.Instance.EmitSignal(SignalBus.SignalName.EnemyDefeated);
		_enemyHealthBar = GetNode<ProgressBar>("EnemyHealthBar");
		_playerHealthBar = GetNode<ProgressBar>("PlayerPanel/PlayerHealthBar");
		_attackButton = GetNode<Button>("PlayerPanel/Actions/Attack");
		_runButton = GetNode<Button>("PlayerPanel/Actions/Run");
		
		_enemyName = GetNode<Label>("EnemyName");
		_enemyTexture = GetNode<Sprite2D>("EnemyTexture");
		// Initialize Enemies
		setEnemy(Enemy); 
		if (_attackButton != null)
		{
			_attackButton.Pressed += OnAttackButtonPressed;
		}
			if (_runButton != null)
		{
			_runButton.Pressed += OnRunButtonPressed;
		}
	}

	private void setEnemy(BaseEnemy enemy) {
		_enemyName.Text = enemy.name;
		_enemyTexture.Texture = enemy.texture;
		GD.Print(enemy);
	}
	
	public void OnAttackButtonPressed()
	{
		_enemyHealthBar.Value = _enemyHealthBar.Value - 20;
		
		EnemyTurn();
	}
	
	public void OnRunButtonPressed()
	{
		GetTree().ChangeSceneToFile("res://Scenes/Main.tscn");
	}
	
	public void EnemyTurn() {
		_playerHealthBar.Value = _playerHealthBar.Value - 10;
	}
	
	
	// Called every frame. 'delta' is the elapsed time since the previous frame.
	public override void _Process(double delta)
	{
	}
}
