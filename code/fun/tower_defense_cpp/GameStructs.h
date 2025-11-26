#pragma once
#include <vector>
#include <memory>
#include <SFML/Graphics.hpp>

enum class TowerType {
    Pipe,
    Fireball,
    BobBomb,
    Mushroom
};

enum class EnemyType {
    Goomba,
    Koopa,
    Piranha,
    Bill,
    BowserJr,
    Boss
};

struct Tower {
    TowerType type;
    float x, y;
    float lastShot;
    
    Tower(TowerType t, float px, float py) : type(t), x(px), y(py), lastShot(0) {}
};

struct Enemy {
    EnemyType type;
    int pathIndex;
    float pathProgress;
    float health;
    float maxHealth;
    float speed;
    float x, y;
    int baseReward;
    float rewardMultiplier;
    int level;
    float size;
    
    Enemy(EnemyType t, float h, float s, int r, float sz) 
        : type(t), pathIndex(0), pathProgress(0), health(h), maxHealth(h), 
          speed(s), x(0), y(0), baseReward(r), rewardMultiplier(1.0f), level(1), size(sz) {}
};

struct Projectile {
    float x, y;
    std::shared_ptr<Enemy> targetEnemy;
    TowerType towerType;
    int damage;
    
    Projectile(float px, float py, std::shared_ptr<Enemy> target, TowerType t, int d)
        : x(px), y(py), targetEnemy(target), towerType(t), damage(d) {}
};

struct Particle {
    float x, y;
    float vx, vy;
    int lifetime;
    int maxLifetime;
    float size;
};

struct Explosion {
    float x, y;
    float radius;
    float maxRadius;
    int lifetime;
    int maxLifetime;
    std::vector<Particle> particles;
};

struct GameState {
    int currentLevel;
    int score;
    int gold;
    int lives;
    bool isPaused;
    bool gameOver;
    bool gameWon;
    TowerType selectedTower;
    int selectedTowerIndex;
    int currentWave;
    bool waveInProgress;
    int speedMultiplier;
    
    std::vector<std::shared_ptr<Tower>> towers;
    std::vector<std::shared_ptr<Enemy>> enemies;
    std::vector<Projectile> projectiles;
    std::vector<Explosion> explosions;
    
    GameState() : currentLevel(1), score(0), gold(500), lives(20), 
                  isPaused(false), gameOver(false), gameWon(false),
                  selectedTowerIndex(-1), currentWave(0), waveInProgress(false),
                  speedMultiplier(1) {}
};
