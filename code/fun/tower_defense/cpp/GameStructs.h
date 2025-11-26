#pragma once

#include <vector>
#include <memory>

// Enum for tower types
enum class TowerType {
    Pipe = 0,
    Fireball = 1,
    BobBomb = 2,
    Mushroom = 3
};

// Enum for enemy types
enum class EnemyType {
    Goomba = 0,
    Koopa = 1,
    Piranha = 2,
    Bill = 3,
    BowserJr = 4,
    Boss = 5
};

// Forward declarations
class Enemy;

// Tower structure
struct Tower {
    TowerType type;
    float x, y;
    float lastShot;
    
    Tower(TowerType t, float px, float py) 
        : type(t), x(px), y(py), lastShot(0) {}
};

// Enemy structure
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
          speed(s), x(0), y(0), baseReward(r), rewardMultiplier(1.0f), 
          level(1), size(sz) {}
};

// Projectile structure
struct Projectile {
    float x, y;
    std::shared_ptr<Enemy> targetEnemy;
    TowerType towerType;
    float damage;
    
    Projectile(float px, float py, std::shared_ptr<Enemy> target, TowerType type, float dmg)
        : x(px), y(py), targetEnemy(target), towerType(type), damage(dmg) {}
};

// Particle structure
struct Particle {
    float x, y;
    float vx, vy;
    int lifetime;
    int maxLifetime;
    float size;
    
    Particle(float px, float py, float vx_in, float vy_in, int life, float sz)
        : x(px), y(py), vx(vx_in), vy(vy_in), lifetime(life), maxLifetime(life), size(sz) {}
};

// Explosion structure
struct Explosion {
    float x, y;
    float radius, maxRadius;
    int lifetime, maxLifetime;
    std::vector<Particle> particles;
};

// GameState structure
struct GameState {
    int currentLevel;
    int currentWave;
    int score;
    int gold;
    int lives;
    float speedMultiplier;
    bool isPaused;
    bool gameOver;
    bool gameWon;
    bool waveInProgress;
    int selectedTowerIndex;
    
    std::vector<std::shared_ptr<Tower>> towers;
    std::vector<std::shared_ptr<Enemy>> enemies;
    std::vector<Projectile> projectiles;
    std::vector<Explosion> explosions;
    
    GameState() 
        : currentLevel(1), currentWave(0), score(0), gold(100), lives(20), 
          speedMultiplier(1), isPaused(false), gameOver(false), gameWon(false),
          waveInProgress(false), selectedTowerIndex(-1) {}
};
