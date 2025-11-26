#include "Game.h"
#include "GameConfig.h"
#include <cmath>
#include <random>
#include <iostream>

Game::Game() : window(sf::VideoMode(CANVAS_WIDTH, CANVAS_HEIGHT), "Mario Tower Defense") {
    window.setFramerateLimit(60);
    
    // Load font (you'll need to provide a font file)
    if (!font.loadFromFile("arial.ttf")) {
        std::cerr << "Warning: Could not load font. Text rendering may not work properly." << std::endl;
    }
    
    setupPath();
}

Game::~Game() {
}

void Game::setupPath() {
    // Path is initialized in Path constructor
}

void Game::run() {
    sf::Clock clock;
    
    while (window.isOpen() && !gameState.gameWon && !gameState.gameOver) {
        float deltaTime = clock.restart().asSeconds();
        
        handleInput();
        update(deltaTime);
        render();
    }
}

void Game::handleInput() {
    sf::Event event;
    while (window.pollEvent(event)) {
        if (event.type == sf::Event::Closed) {
            window.close();
        }
        else if (event.type == sf::Event::MouseButtonPressed) {
            float x = event.mouseButton.x;
            float y = event.mouseButton.y;
            placeTower(x, y);
        }
        else if (event.type == sf::Event::KeyPressed) {
            if (event.key.code == sf::Keyboard::Space) {
                startWave();
            }
            else if (event.key.code == sf::Keyboard::S) {
                cycleSpeed();
            }
            else if (event.key.code == sf::Keyboard::P) {
                gameState.isPaused = !gameState.isPaused;
            }
        }
    }
}

void Game::placeTower(float x, float y) {
    if (gameState.selectedTowerIndex == -1 || path.isOnPath(x, y)) {
        return;
    }
    
    float cost = getTowerCost((TowerType)gameState.selectedTowerIndex);
    if (gameState.gold >= cost) {
        gameState.towers.push_back(std::make_shared<Tower>((TowerType)gameState.selectedTowerIndex, x, y));
        gameState.gold -= cost;
    }
}

void Game::startWave() {
    if (gameState.waveInProgress) return;
    
    gameState.waveInProgress = true;
    gameState.currentWave++;
    
    // Spawn enemies for this wave
    // For now, spawn a simple wave of Goombas
    for (int i = 0; i < 5 + gameState.currentWave * 2; i++) {
        spawnEnemy(EnemyType::Goomba);
    }
}

void Game::cycleSpeed() {
    if (gameState.speedMultiplier == 1) {
        gameState.speedMultiplier = 2;
    } else if (gameState.speedMultiplier == 2) {
        gameState.speedMultiplier = 4;
    } else {
        gameState.speedMultiplier = 1;
    }
}

void Game::spawnEnemy(EnemyType type) {
    float health = 10;
    float speed = 1.0f;
    int reward = 10;
    float size = 1.0f;
    
    switch (type) {
        case EnemyType::Goomba:
            health = 10; speed = 1.0f; reward = 10; size = 1.0f;
            break;
        case EnemyType::Koopa:
            health = 20; speed = 0.8f; reward = 15; size = 1.0f;
            break;
        case EnemyType::Piranha:
            health = 30; speed = 0.6f; reward = 20; size = 1.0f;
            break;
        case EnemyType::Bill:
            health = 15; speed = 2.0f; reward = 25; size = 1.0f;
            break;
        case EnemyType::BowserJr:
            health = 50; speed = 0.5f; reward = 50; size = 1.0f;
            break;
        case EnemyType::Boss:
            health = 100; speed = 0.4f; reward = 200; size = 1.8f;
            break;
    }
    
    // Apply level scaling
    float healthMult = 1.0f + (gameState.currentLevel - 1) * 0.3f;
    float speedMult = 1.0f + (gameState.currentLevel - 1) * 0.1f;
    float rewardMult = 1.0f + (gameState.currentLevel - 1) * 0.2f;
    
    auto enemy = std::make_shared<Enemy>(type, health * healthMult, speed * speedMult, reward, size);
    enemy->level = gameState.currentLevel;
    enemy->rewardMultiplier = rewardMult;
    enemy->x = path.points[0].x;
    enemy->y = path.points[0].y;
    
    gameState.enemies.push_back(enemy);
}

void Game::update(float deltaTime) {
    if (gameState.isPaused) return;
    
    updateEnemies(deltaTime);
    updateTowers(deltaTime);
    updateProjectiles(deltaTime);
    updateExplosions(deltaTime);
    
    // Check wave completion
    if (gameState.waveInProgress && gameState.enemies.empty()) {
        gameState.waveInProgress = false;
        if (gameState.currentLevel >= 10) {
            gameState.gameWon = true;
        }
    }
}

void Game::updateEnemies(float deltaTime) {
    for (auto it = gameState.enemies.begin(); it != gameState.enemies.end();) {
        auto& enemy = *it;
        
        if (enemy->pathIndex >= (int)path.points.size() - 1) {
            gameState.lives--;
            it = gameState.enemies.erase(it);
            continue;
        }
        
        // Move along path
        enemy->pathProgress += enemy->speed * gameState.speedMultiplier * deltaTime * 60.0f; // Scale for 60fps baseline
        
        const auto& curr = path.points[enemy->pathIndex];
        const auto& next = path.points[std::min((int)path.points.size() - 1, enemy->pathIndex + 1)];
        
        float dx = next.x - curr.x;
        float dy = next.y - curr.y;
        float dist = std::sqrt(dx * dx + dy * dy);
        
        if (enemy->pathProgress >= dist) {
            enemy->pathProgress -= dist;
            enemy->pathIndex++;
        }
        
        if (enemy->pathIndex < (int)path.points.size()) {
            const auto& c = path.points[enemy->pathIndex];
            const auto& n = path.points[std::min((int)path.points.size() - 1, enemy->pathIndex + 1)];
            
            float ddx = n.x - c.x;
            float ddy = n.y - c.y;
            float d = std::sqrt(ddx * ddx + ddy * ddy);
            
            enemy->x = c.x + (ddx / d) * enemy->pathProgress;
            enemy->y = c.y + (ddy / d) * enemy->pathProgress;
        }
        
        if (enemy->health <= 0) {
            createExplosion(enemy->x, enemy->y);
            int reward = enemy->baseReward * enemy->rewardMultiplier;
            gameState.score += reward;
            gameState.gold += reward;
            it = gameState.enemies.erase(it);
        } else {
            ++it;
        }
    }
}

void Game::updateTowers(float deltaTime) {
    float timeStep = deltaTime * 1000.0f * gameState.speedMultiplier;
    
    for (auto& tower : gameState.towers) {
        tower->lastShot += timeStep;
        
        // Find target
        std::shared_ptr<Enemy> target = nullptr;
        float minDist = getTowerRange(tower->type);
        
        for (auto& enemy : gameState.enemies) {
            float dx = tower->x - enemy->x;
            float dy = tower->y - enemy->y;
            float dist = std::sqrt(dx * dx + dy * dy);
            
            if (dist < minDist) {
                target = enemy;
                minDist = dist;
            }
        }
        
        // Shoot
        if (target && tower->lastShot >= 1000.0f / getTowerFireRate(tower->type)) {
            gameState.projectiles.push_back(
                Projectile(tower->x, tower->y, target, tower->type, getTowerDamage(tower->type))
            );
            tower->lastShot = 0;
        }
    }
}

void Game::updateProjectiles(float deltaTime) {
    for (auto it = gameState.projectiles.begin(); it != gameState.projectiles.end();) {
        auto& proj = *it;
        
        if (!proj.targetEnemy) {
            it = gameState.projectiles.erase(it);
            continue;
        }
        
        float dx = proj.targetEnemy->x - proj.x;
        float dy = proj.targetEnemy->y - proj.y;
        float dist = std::sqrt(dx * dx + dy * dy);
        
        if (dist < 10) {
            proj.targetEnemy->health -= proj.damage;
            it = gameState.projectiles.erase(it);
        } else {
            proj.x += (dx / dist) * 5.0f;
            proj.y += (dy / dist) * 5.0f;
            ++it;
        }
    }
}

void Game::updateExplosions(float deltaTime) {
    for (auto it = gameState.explosions.begin(); it != gameState.explosions.end();) {
        auto& exp = *it;
        exp.lifetime--;
        
        if (exp.lifetime <= 0) {
            it = gameState.explosions.erase(it);
        } else {
            ++it;
        }
    }
}

void Game::createExplosion(float x, float y) {
    Explosion exp;
    exp.x = x;
    exp.y = y;
    exp.radius = 5.0f;
    exp.maxRadius = 40.0f;
    exp.lifetime = 30;
    exp.maxLifetime = 30;
    gameState.explosions.push_back(exp);
}

void Game::render() {
    window.clear(sf::Color(135, 206, 235)); // Sky blue
    
    drawPath();
    drawTowers();
    drawEnemies();
    drawProjectiles();
    drawExplosions();
    drawUI();
    
    window.display();
}

void Game::drawPath() {
    sf::Color pathColor(139, 115, 85); // Brown
    
    for (size_t i = 0; i < path.points.size() - 1; i++) {
        sf::RectangleShape line(sf::Vector2f(
            std::sqrt(std::pow(path.points[i+1].x - path.points[i].x, 2) + 
                     std::pow(path.points[i+1].y - path.points[i].y, 2)),
            60.0f
        ));
        
        line.setPosition(path.points[i]);
        float angle = std::atan2(path.points[i+1].y - path.points[i].y, 
                                path.points[i+1].x - path.points[i].x) * 180.0f / 3.14159f;
        line.setRotation(angle);
        line.setFillColor(pathColor);
        window.draw(line);
    }
}

void Game::drawTowers() {
    for (auto& tower : gameState.towers) {
        sf::Text towerText(getTowerIcon(tower->type), font, 32);
        towerText.setPosition(tower->x - 16, tower->y - 16);
        window.draw(towerText);
    }
}

void Game::drawEnemies() {
    for (auto& enemy : gameState.enemies) {
        sf::Text enemyText(getEnemyIcon(enemy->type), font, 24 * enemy->size);
        enemyText.setPosition(enemy->x - 12, enemy->y - 12);
        window.draw(enemyText);
        
        // Draw health bar
        float barWidth = 30 * enemy->size;
        float barHeight = 4.0f;
        float barY = enemy->y - 20;
        
        sf::RectangleShape healthBack(sf::Vector2f(barWidth, barHeight));
        healthBack.setPosition(enemy->x - barWidth/2, barY);
        healthBack.setFillColor(sf::Color::Red);
        window.draw(healthBack);
        
        sf::RectangleShape healthFront(sf::Vector2f(barWidth * (enemy->health / enemy->maxHealth), barHeight));
        healthFront.setPosition(enemy->x - barWidth/2, barY);
        healthFront.setFillColor(sf::Color::Green);
        window.draw(healthFront);
    }
}

void Game::drawProjectiles() {
    for (auto& proj : gameState.projectiles) {
        sf::CircleShape circle(4);
        circle.setPosition(proj.x - 4, proj.y - 4);
        circle.setFillColor(sf::Color::Yellow);
        window.draw(circle);
    }
}

void Game::drawExplosions() {
    for (auto& exp : gameState.explosions) {
        float radius = exp.maxRadius * (1.0f - (float)exp.lifetime / exp.maxLifetime);
        sf::CircleShape circle(radius);
        circle.setPosition(exp.x - radius, exp.y - radius);
        circle.setFillColor(sf::Color(255, 150, 0, 150));
        window.draw(circle);
    }
}

void Game::drawUI() {
    sf::Text levelText("Level: " + std::to_string(gameState.currentLevel), font, 20);
    levelText.setPosition(10, 10);
    levelText.setFillColor(sf::Color::White);
    window.draw(levelText);
    
    sf::Text goldText("Gold: " + std::to_string(gameState.gold), font, 20);
    goldText.setPosition(10, 40);
    goldText.setFillColor(sf::Color::White);
    window.draw(goldText);
    
    sf::Text livesText("Lives: " + std::to_string(gameState.lives), font, 20);
    livesText.setPosition(10, 70);
    livesText.setFillColor(sf::Color::White);
    window.draw(livesText);
    
    sf::Text scoreText("Score: " + std::to_string(gameState.score), font, 20);
    scoreText.setPosition(10, 100);
    scoreText.setFillColor(sf::Color::White);
    window.draw(scoreText);
}

float Game::getTowerCost(TowerType type) {
    switch (type) {
        case TowerType::Pipe: return PIPE_COST;
        case TowerType::Fireball: return FIREBALL_COST;
        case TowerType::BobBomb: return BOMBOMB_COST;
        case TowerType::Mushroom: return MUSHROOM_COST;
    }
    return 0;
}

float Game::getTowerRange(TowerType type) {
    switch (type) {
        case TowerType::Pipe: return PIPE_RANGE;
        case TowerType::Fireball: return FIREBALL_RANGE;
        case TowerType::BobBomb: return BOMBOMB_RANGE;
        case TowerType::Mushroom: return MUSHROOM_RANGE;
    }
    return 0;
}

float Game::getTowerDamage(TowerType type) {
    switch (type) {
        case TowerType::Pipe: return PIPE_DAMAGE;
        case TowerType::Fireball: return FIREBALL_DAMAGE;
        case TowerType::BobBomb: return BOMBOMB_DAMAGE;
        case TowerType::Mushroom: return MUSHROOM_DAMAGE;
    }
    return 0;
}

float Game::getTowerFireRate(TowerType type) {
    switch (type) {
        case TowerType::Pipe: return PIPE_FIRERATE;
        case TowerType::Fireball: return FIREBALL_FIRERATE;
        case TowerType::BobBomb: return BOMBOMB_FIRERATE;
        case TowerType::Mushroom: return MUSHROOM_FIRERATE;
    }
    return 0;
}

std::string Game::getTowerIcon(TowerType type) {
    switch (type) {
        case TowerType::Pipe: return "P";
        case TowerType::Fireball: return "F";
        case TowerType::BobBomb: return "B";
        case TowerType::Mushroom: return "M";
    }
    return "?";
}

std::string Game::getEnemyIcon(EnemyType type) {
    switch (type) {
        case EnemyType::Goomba: return "G";
        case EnemyType::Koopa: return "K";
        case EnemyType::Piranha: return "P";
        case EnemyType::Bill: return "L";
        case EnemyType::BowserJr: return "J";
        case EnemyType::Boss: return "X";
    }
    return "?";
}
