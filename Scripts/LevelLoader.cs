using Godot;
using System;
using System.Collections.Generic;
using System.Text.Json;

public partial class LevelLoader : Node
{	
	
  
 	public AudioStreamPlayer _audioPlayer;

   // Custom Texture to Put In
   [Export] public Texture2D texture { get; set; }
   [Export] public string JsonTileMapPath { get; set; }
	// Called when the node enters the scene tree for the first time.
	public override void _Ready()
	{
		SignalBus.Instance.ClearLevel += OnClearLevel;
		_audioPlayer = GetNode<AudioStreamPlayer>("AudioStreamPlayer");
		LoadJsonTileMap(JsonTileMapPath);
		GD.Print("Finished Loading Level");
	}
	
	public void LoadJsonTileMap(string jsonPath) {
		using var file = FileAccess.Open(jsonPath, FileAccess.ModeFlags.Read); 
		
		//json 
		string json = file.GetAsText();
	
		var options = new JsonSerializerOptions
		{
			PropertyNameCaseInsensitive = true
		};

		Person person = JsonSerializer.Deserialize<Person>(json, options);

		if (person == null)
		{
			GD.Print("Deserialization failed");
		}
		
		LoadJsonMusic(person.Music);
		
		for (int i = 0; i < person.Grid.Length; i++)
		{
			for (int j = 0; j < person.Grid[i].Length; j++)
			{
				AddChild(lookup(person.Grid[i][j], i * 32 + 16, j * 32 + 16));
			}
		}		
	}
	
	public void ClearLevel() { 
		foreach (Node n in GetChildren()) {
			n.QueueFree();
		}
	}
	
	//Run with ClearLevel Signal is emitted
	private void OnClearLevel() {
		GD.Print("Level Cleared");
		ClearLevel(); 	
	}

	public void LoadJsonMusic(string musicName) {
		 _audioPlayer.Stream = GD.Load<AudioStream>("res://Assets/Music/" + musicName);
		_audioPlayer.Play(); 
	}
	
	// Looks up a texture name and puts coords
	// Returns a Sprite2D
	public Sprite2D lookup(string textureName, float x, float y) {
		Sprite2D sprite = new Sprite2D();
		if (textureName == null) {
			sprite.Texture = GD.Load<Texture2D>("res://Assets/Art/Tiles/wood_floor.png"); 
		} else {
			sprite.Texture = GD.Load<Texture2D>("res://Assets/Art/Tiles/" + textureName); 
		}
		sprite.Position = new Vector2(x, y); 
		return sprite; 
	}
	
	//switch statement in a function
	// enum value is the input for the function. output is the actual texture to be loaded
	
	
	// Called every frame. 'delta' is the elapsed time since the previous frame.
	public override void _Process(double delta)
	{
	}
	//	sprite.Position = new Vector2(128, 128); 
}

public class Person
{
	public string Name { get; set; } = "";
	public string Music { get; set; } = "";
	public int Age { get; set; }
	public string[][] Grid { get; set; }
}
