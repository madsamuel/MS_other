#pragma once

constexpr int CANVAS_WIDTH = 900;
constexpr int CANVAS_HEIGHT = 800;
constexpr float GAME_SPEED = 1.0f;

// Tower costs
constexpr int PIPE_COST = 50;
constexpr int FIREBALL_COST = 100;
constexpr int BOMBOMB_COST = 150;
constexpr int MUSHROOM_COST = 120;

// Tower ranges
constexpr float PIPE_RANGE = 80.0f;
constexpr float FIREBALL_RANGE = 120.0f;
constexpr float BOMBOMB_RANGE = 100.0f;
constexpr float MUSHROOM_RANGE = 100.0f;

// Tower fire rates (per second)
constexpr float PIPE_FIRERATE = 1.0f;
constexpr float FIREBALL_FIRERATE = 0.8f;
constexpr float BOMBOMB_FIRERATE = 0.5f;
constexpr float MUSHROOM_FIRERATE = 1.2f;

// Tower damage
constexpr int PIPE_DAMAGE = 10;
constexpr int FIREBALL_DAMAGE = 25;
constexpr int BOMBOMB_DAMAGE = 50;
constexpr int MUSHROOM_DAMAGE = 15;

// Enemy stats
constexpr int INITIAL_LIVES = 20;
constexpr int INITIAL_GOLD = 500;
constexpr float PATH_TOLERANCE = 60.0f;
