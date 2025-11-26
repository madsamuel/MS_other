#pragma once

// Canvas dimensions
const int CANVAS_WIDTH = 900;
const int CANVAS_HEIGHT = 800;

// Tower types and costs
const float PIPE_COST = 50.0f;
const float FIREBALL_COST = 100.0f;
const float BOMBOMB_COST = 150.0f;
const float MUSHROOM_COST = 120.0f;

// Tower ranges
const float PIPE_RANGE = 80.0f;
const float FIREBALL_RANGE = 120.0f;
const float BOMBOMB_RANGE = 100.0f;
const float MUSHROOM_RANGE = 100.0f;

// Tower damage
const float PIPE_DAMAGE = 10.0f;
const float FIREBALL_DAMAGE = 25.0f;
const float BOMBOMB_DAMAGE = 50.0f;
const float MUSHROOM_DAMAGE = 15.0f;

// Tower fire rates (shots per second)
const float PIPE_FIRERATE = 1.0f;
const float FIREBALL_FIRERATE = 0.8f;
const float BOMBOMB_FIRERATE = 0.5f;
const float MUSHROOM_FIRERATE = 1.2f;

// Game constants
const int PATH_TOLERANCE = 60;
const float SELL_REFUND = 0.75f;
const int INITIAL_GOLD = 100;
const int INITIAL_LIVES = 20;
const int NUM_LEVELS = 10;
