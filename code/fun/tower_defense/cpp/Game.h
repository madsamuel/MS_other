#pragma once

#include <SFML/Graphics.hpp>
#include <vector>
#include <memory>
#include <string>
#include "GameStructs.h"
#include "Path.h"
#include "GameConfig.h"

class Game {
public:
    Game();
    ~Game();
    
    void run();
    void handleInput();
    void update(float deltaTime);
    void render();

private:
    sf::RenderWindow window;
    GameState gameState;
    Path path;
    sf::Font font;
    
    // Game logic
    void setupPath();
    void placeTower(float x, float y);
    void startWave();
    void cycleSpeed();
    void spawnEnemy(EnemyType type);
    void updateEnemies(float deltaTime);
    void updateTowers(float deltaTime);
    void updateProjectiles(float deltaTime);
    void updateExplosions(float deltaTime);
    
    // Rendering
    void drawPath();
    void drawTowers();
    void drawEnemies();
    void drawProjectiles();
    void drawExplosions();
    void drawUI();
    
    // Utilities
    void createExplosion(float x, float y);
    float getTowerCost(TowerType type);
    float getTowerRange(TowerType type);
    float getTowerDamage(TowerType type);
    float getTowerFireRate(TowerType type);
    std::string getTowerIcon(TowerType type);
    std::string getEnemyIcon(EnemyType type);
};
