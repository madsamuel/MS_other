#include "Game.h"
#include "GameConfig.h"
#include <cmath>
#include <random>
#include <iostream>
#include <sstream>

Game::Game() : window(sf::VideoMode(CANVAS_WIDTH, CANVAS_HEIGHT), "Mario Tower Defense") {
    window.setFramerateLimit(60);
    
    // Load font - try multiple paths
    std::vector<std::string> fontPaths = {
        "arial.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Arial.ttf"
    };
    
    bool fontLoaded = false;
    for (const auto& path : fontPaths) {
        if (font.loadFromFile(path)) {
            fontLoaded = true;
            break;
        }
    }
    
    if (!fontLoaded) {
        std::cerr << "Warning: Could not load font. Text rendering may not work properly." << std::endl;
    }
    
    setupPath();
    gameState.gold = INITIAL_GOLD;
    gameState.lives = INITIAL_LIVES;
}

Game::~Game() {
}

void Game::setupPath() {
    // Path is initialized in Path constructor
}

void Game::run() {
    sf::Clock clock;
    
    while (window.isOpen()) {
        float deltaTime = clock.restart().asSeconds();
        
        handleInput();
        update(deltaTime);
        render();
        
        if (gameState.gameWon || gameState.gameOver) {
            // Wait for window to close after game ends
            while (window.isOpen()) {
                sf::Event event;
                while (window.pollEvent(event)) {
                    if (event.type == sf::Event::Closed) {
                        window.close();
                    }
                }
            }
        }
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
            else if (event.key.code == sf::Keyboard::Num1) {
                gameState.selectedTowerIndex = 0; // Pipe
            }
            else if (event.key.code == sf::Keyboard::Num2) {
                gameState.selectedTowerIndex = 1; // Fireball
            }
            else if (event.key.code == sf::Keyboard::Num3) {
                gameState.selectedTowerIndex = 2; // BobBomb
            }
            else if (event.key.code == sf::Keyboard::Num4) {
                gameState.selectedTowerIndex = 3; // Mushroom
            }
        }
    }
}

void Game::placeTower(float x, float y) {
    if (gameState.selectedTowerIndex == -1 || path.isOnPath(x, y, PATH_TOLERANCE)) {
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
    int numEnemies = 5 + gameState.currentWave * 2;
    
    // Vary enemy types
    for (int i = 0; i < numEnemies; i++) {
        int typeIndex = (gameState.currentWave + i) % 5;
        EnemyType type = (EnemyType)typeIndex;
        
        if (gameState.currentWave % 3 == 0 && i == numEnemies - 1) {
            type = EnemyType::Boss;
        }
        
        spawnEnemy(type);
    }
    
    // Add bosses at end of level
    if (gameState.currentWave >= 3) { // 3 waves per level
        for (int i = 0; i < gameState.currentLevel; i++) {
            spawnEnemy(EnemyType::Boss);
        }
        gameState.currentLevel++;
        gameState.currentWave = 0;
        
        if (gameState.currentLevel > NUM_LEVELS) {
            gameState.gameWon = true;
        }
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
    float healthMult = 1.0f + (gameState.currentLevel - 1) * 0.3f + (gameState.currentWave - 1) * 0.1f;
    float speedMult = 1.0f + (gameState.currentLevel - 1) * 0.1f + (gameState.currentWave - 1) * 0.05f;
    float rewardMult = 1.0f + (gameState.currentLevel - 1) * 0.2f + (gameState.currentWave - 1) * 0.1f;
    
    auto enemy = std::make_shared<Enemy>(type, health * healthMult, speed * speedMult, reward, size);
    enemy->level = gameState.currentLevel;
    enemy->rewardMultiplier = rewardMult;
    
    if (!path.points.empty()) {
        enemy->x = path.points[0].x;
        enemy->y = path.points[0].y;
    }
    
    gameState.enemies.push_back(enemy);
}

void Game::update(float deltaTime) {
    if (gameState.isPaused) return;
    
    if (gameState.lives <= 0) {
        gameState.gameOver = true;
        return;
    }
    
    updateEnemies(deltaTime);
    updateTowers(deltaTime);
    updateProjectiles(deltaTime);
    updateExplosions(deltaTime);
    
    // Check wave completion
    if (gameState.waveInProgress && gameState.enemies.empty()) {
        gameState.waveInProgress = false;
    }
}

void Game::updateEnemies(float deltaTime) {
    for (auto it = gameState.enemies.begin(); it != gameState.enemies.end();) {
        auto enemy = *it;
        
        // Check if reached end of path
        if (enemy->pathIndex >= (int)path.points.size() - 1) {
            gameState.lives--;
            it = gameState.enemies.erase(it);
            continue;
        }
        
        // Move along path with speed multiplier
        float movementSpeed = enemy->speed * gameState.speedMultiplier * deltaTime * 60.0f;
        enemy->pathProgress += movementSpeed;
        
        // Find current segment
        const Vector2D& curr = path.points[enemy->pathIndex];
        const Vector2D& next = path.points[std::min((int)path.points.size() - 1, enemy->pathIndex + 1)];
        
        float dx = next.x - curr.x;
        float dy = next.y - curr.y;
        float dist = std::sqrt(dx * dx + dy * dy);
        
        // Move to next segment if we've traveled the segment distance
        while (enemy->pathProgress >= dist && enemy->pathIndex < (int)path.points.size() - 1) {
            enemy->pathProgress -= dist;
            enemy->pathIndex++;
            
            if (enemy->pathIndex >= (int)path.points.size() - 1) {
                break;
            }
            
            const Vector2D& c = path.points[enemy->pathIndex];
            const Vector2D& n = path.points[std::min((int)path.points.size() - 1, enemy->pathIndex + 1)];
            dx = n.x - c.x;
            dy = n.y - c.y;
            dist = std::sqrt(dx * dx + dy * dy);
        }
        
        // Update position based on current progress
        if (enemy->pathIndex < (int)path.points.size() - 1) {
            const Vector2D& c = path.points[enemy->pathIndex];
            const Vector2D& n = path.points[enemy->pathIndex + 1];
            
            float ddx = n.x - c.x;
            float ddy = n.y - c.y;
            float d = std::sqrt(ddx * ddx + ddy * ddy);
            
            if (d > 0) {
                enemy->x = c.x + (ddx / d) * enemy->pathProgress;
                enemy->y = c.y + (ddy / d) * enemy->pathProgress;
            }
        }
        
        // Check if health depleted
        if (enemy->health <= 0) {
            createExplosion(enemy->x, enemy->y);
            int reward = static_cast<int>(enemy->baseReward * enemy->rewardMultiplier);
            gameState.score += reward;
            gameState.gold += reward;
            it = gameState.enemies.erase(it);
        } else {
            ++it;
        }
    }
}

void Game::updateTowers(float deltaTime) {
    float timeStep = deltaTime * 1000.0f;
    
    for (auto& tower : gameState.towers) {
        tower->lastShot += timeStep;
        
        // Find target
        std::shared_ptr<Enemy> target = nullptr;
        float range = getTowerRange(tower->type);
        float minDist = range;
        
        for (auto& enemy : gameState.enemies) {
            float dx = tower->x - enemy->x;
            float dy = tower->y - enemy->y;
            float dist = std::sqrt(dx * dx + dy * dy);
            
            if (dist < minDist) {
                target = enemy;
                minDist = dist;
            }
        }
        
        // Shoot if target found and cooldown expired
        float fireRate = getTowerFireRate(tower->type);
        float cooldown = 1000.0f / fireRate;
        
        if (target && tower->lastShot >= cooldown) {
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
        
        // Check if target still exists
        if (!proj.targetEnemy) {
            it = gameState.projectiles.erase(it);
            continue;
        }
        
        // Calculate direction to target
        float dx = proj.targetEnemy->x - proj.x;
        float dy = proj.targetEnemy->y - proj.y;
        float dist = std::sqrt(dx * dx + dy * dy);
        
        // Check if reached target
        if (dist < 10) {
            proj.targetEnemy->health -= proj.damage;
            it = gameState.projectiles.erase(it);
        } else {
            // Move towards target
            float moveSpeed = 5.0f;
            proj.x += (dx / dist) * moveSpeed;
            proj.y += (dy / dist) * moveSpeed;
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
        sf::Vector2f start(path.points[i].x, path.points[i].y);
        sf::Vector2f end(path.points[i + 1].x, path.points[i + 1].y);
        
        float dx = end.x - start.x;
        float dy = end.y - start.y;
        float length = std::sqrt(dx * dx + dy * dy);
        
        if (length > 0) {
            sf::RectangleShape line(sf::Vector2f(length, 60.0f));
            line.setPosition(start);
            line.setFillColor(pathColor);
            float angle = std::atan2(dy, dx) * 180.0f / 3.14159f;
            line.setRotation(angle);
            window.draw(line);
        }
    }
}

void Game::drawTowers() {
    for (auto& tower : gameState.towers) {
        sf::Text towerText(getTowerIcon(tower->type), font, 32);
        towerText.setPosition(tower->x - 16, tower->y - 16);
        towerText.setFillColor(sf::Color::White);
        window.draw(towerText);
        
        // Draw range indicator (optional, light circle)
        float range = getTowerRange(tower->type);
        sf::CircleShape rangeCircle(range);
        rangeCircle.setPosition(tower->x - range, tower->y - range);
        rangeCircle.setFillColor(sf::Color::Transparent);
        rangeCircle.setOutlineThickness(1.0f);
        rangeCircle.setOutlineColor(sf::Color(200, 200, 200, 100));
        window.draw(rangeCircle);
    }
}

void Game::drawEnemies() {
    for (auto& enemy : gameState.enemies) {
        // Draw enemy sprite
        sf::Text enemyText(getEnemyIcon(enemy->type), font, static_cast<int>(24 * enemy->size));
        enemyText.setPosition(enemy->x - 12, enemy->y - 12);
        enemyText.setFillColor(sf::Color::White);
        window.draw(enemyText);
        
        // Draw health bar
        float barWidth = 30 * enemy->size;
        float barHeight = 4.0f;
        float barY = enemy->y - 20;
        
        sf::RectangleShape healthBack(sf::Vector2f(barWidth, barHeight));
        healthBack.setPosition(enemy->x - barWidth / 2, barY);
        healthBack.setFillColor(sf::Color::Red);
        window.draw(healthBack);
        
        float healthPercent = enemy->health / enemy->maxHealth;
        if (healthPercent < 0) healthPercent = 0;
        
        sf::RectangleShape healthFront(sf::Vector2f(barWidth * healthPercent, barHeight));
        healthFront.setPosition(enemy->x - barWidth / 2, barY);
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
        float progress = 1.0f - ((float)exp.lifetime / exp.maxLifetime);
        float radius = exp.maxRadius * progress;
        
        sf::CircleShape circle(radius);
        circle.setPosition(exp.x - radius, exp.y - radius);
        
        int alpha = static_cast<int>(200 * (1.0f - progress));
        circle.setFillColor(sf::Color(255, 150, 0, alpha));
        window.draw(circle);
    }
}

void Game::drawUI() {
    int charSize = 16;
    
    std::stringstream ss;
    ss << "Level: " << gameState.currentLevel;
    sf::Text levelText(ss.str(), font, charSize);
    levelText.setPosition(10, 10);
    levelText.setFillColor(sf::Color::Black);
    window.draw(levelText);
    
    ss.str("");
    ss.clear();
    ss << "Gold: " << gameState.gold;
    sf::Text goldText(ss.str(), font, charSize);
    goldText.setPosition(10, 40);
    goldText.setFillColor(sf::Color::Black);
    window.draw(goldText);
    
    ss.str("");
    ss.clear();
    ss << "Lives: " << gameState.lives;
    sf::Text livesText(ss.str(), font, charSize);
    livesText.setPosition(10, 70);
    livesText.setFillColor(sf::Color::Black);
    window.draw(livesText);
    
    ss.str("");
    ss.clear();
    ss << "Score: " << gameState.score;
    sf::Text scoreText(ss.str(), font, charSize);
    scoreText.setPosition(10, 100);
    scoreText.setFillColor(sf::Color::Black);
    window.draw(scoreText);
    
    ss.str("");
    ss.clear();
    ss << "Speed: " << gameState.speedMultiplier << "x (S to toggle)";
    sf::Text speedText(ss.str(), font, charSize);
    speedText.setPosition(10, 130);
    speedText.setFillColor(sf::Color::Black);
    window.draw(speedText);
    
    // Draw selected tower info
    sf::Text towerInfo("Towers: 1=Pipe(50G) 2=Fire(100G) 3=Bomb(150G) 4=Mush(120G)", font, 12);
    towerInfo.setPosition(10, CANVAS_HEIGHT - 40);
    towerInfo.setFillColor(sf::Color::Black);
    window.draw(towerInfo);
    
    sf::Text controls("Space=Wave  P=Pause  Click=Place Tower", font, 12);
    controls.setPosition(10, CANVAS_HEIGHT - 20);
    controls.setFillColor(sf::Color::Black);
    window.draw(controls);
    
    // Draw game status
    if (gameState.gameWon) {
        sf::Text wonText("YOU WON!", font, 48);
        wonText.setPosition(CANVAS_WIDTH / 2 - 100, CANVAS_HEIGHT / 2 - 50);
        wonText.setFillColor(sf::Color::Green);
        window.draw(wonText);
    }
    
    if (gameState.gameOver) {
        sf::Text overText("GAME OVER", font, 48);
        overText.setPosition(CANVAS_WIDTH / 2 - 120, CANVAS_HEIGHT / 2 - 50);
        overText.setFillColor(sf::Color::Red);
        window.draw(overText);
    }
    
    if (gameState.isPaused) {
        sf::Text pauseText("PAUSED", font, 48);
        pauseText.setPosition(CANVAS_WIDTH / 2 - 80, CANVAS_HEIGHT / 2 - 50);
        pauseText.setFillColor(sf::Color::Yellow);
        window.draw(pauseText);
    }
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
