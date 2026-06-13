using Godot;
using System;

public partial class Battle : Control
{

	/// <summary>
	/// Enemy Resource
	/// </summary>
	[Export]
	public BaseEnemy Enemy { get; set; }
	
	[Export]
	public int TURN_COOLDOWN;
	///
	/// Progress Bar Nodes
	///
	private ProgressBar _enemyHealthBar; 
	private ProgressBar _playerHealthBar;

	/// Attack Button Nodes
	private Button _attackButton;
	private Button _runButton;
	
	/// Labels
	private Label _enemyName;
	private Sprite2D _enemyTexture;
	
	// Handles the damage from the enemy
	private int _enemyDamage;
	
	public override void _Ready()
	{	
		// Connect the Enemy Defeated Signal to a Custom Function in The Script
		SignalBus.Instance.EnemyDefeated += OnEnemyDefeated;
		
		// Get the Nodes
		_enemyHealthBar = GetNode<ProgressBar>("EnemyHealthBar");
		_playerHealthBar = GetNode<ProgressBar>("PlayerPanel/PlayerHealthBar");
		_attackButton = GetNode<Button>("PlayerPanel/Actions/Attack");
		_runButton = GetNode<Button>("PlayerPanel/Actions/Run");
		
		_enemyName = GetNode<Label>("EnemyName");
		_enemyTexture = GetNode<Sprite2D>("EnemyTexture");
	
		// Initialize Player 
		setPlayer();
		// Initialize Enemies
		setEnemy(Enemy); 
		
		//Connecting Signals to Custom Functions
		if (_attackButton != null)
		{
			_attackButton.Pressed += OnAttackButtonPressed;
		}
			if (_runButton != null)
		{
			_runButton.Pressed += OnRunButtonPressed;
		}
	}

	private void setPlayer() {
		_playerHealthBar.Value = PlayerData.Instance.currentHealth;
	}
	// Sets up the enemy text, texture, and damage
	private void setEnemy(BaseEnemy enemy) {
		_enemyName.Text = enemy.name;
		_enemyTexture.Texture = enemy.texture;
		_enemyDamage = enemy.damage;
		GD.Print(enemy);
	}
	
	//Plays whenever the Enemy Defeated Signal is Run
	private void OnEnemyDefeated() {
		GD.Print("Hello");
		SceneManager.Instance.ChangeScene("res://Scenes/WinScreen.tscn");
	}
	
	public async void OnAttackButtonPressed()
	{
		_enemyHealthBar.Value = _enemyHealthBar.Value - 20;
			
		if (_enemyHealthBar.Value <= 0) {
			//Emit The Enemy Defeated Signal
			SignalBus.Instance.EmitSignal(SignalBus.SignalName.EnemyDefeated);
		}
		await ToSignal(GetTree().CreateTimer(TURN_COOLDOWN), SceneTreeTimer.SignalName.Timeout);
		EnemyTurn();
		
		if (_playerHealthBar.Value <= 0) {
			SignalBus.Instance.EmitSignal(SignalBus.SignalName.PlayerDefeated);
		}
	}
	
	public void OnRunButtonPressed()
	{
		SceneManager.Instance.ChangeScene("res://Scenes/Main.tscn");
	}
	
	public void EnemyTurn() {
		_playerHealthBar.Value = _playerHealthBar.Value - _enemyDamage;
	}
}
