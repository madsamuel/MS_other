// Game constants
const CANVAS_WIDTH = 900;
const CANVAS_HEIGHT = 800;
const GAME_SPEED = 1;

// Tower definitions
const TOWERS = {
    pipe: {
        name: 'Pipe',
        cost: 50,
        damage: 10,
        range: 80,
        fireRate: 1,
        icon: '🔴',
        description: 'Basic tower with steady fire'
    },
    fireball: {
        name: 'Fireball',
        cost: 100,
        damage: 25,
        range: 120,
        fireRate: 0.8,
        icon: '🔥',
        description: 'Deals extra damage with splash'
    },
    'bob-omb': {
        name: 'Bob-omb',
        cost: 150,
        damage: 50,
        range: 100,
        fireRate: 0.5,
        icon: '💣',
        description: 'Explosive tower with area damage'
    },
    mushroom: {
        name: 'Mushroom',
        cost: 120,
        damage: 15,
        range: 100,
        fireRate: 1.2,
        icon: '🍄',
        description: 'Slows enemies and deals damage'
    }
};

// Enemy definitions
const ENEMIES = {
    goomba: {
        name: 'Goomba',
        health: 10,
        speed: 1,
        reward: 10,
        icon: '👹',
        damage: 1,
        size: 1
    },
    koopa: {
        name: 'Koopa Troopa',
        health: 20,
        speed: 0.8,
        reward: 15,
        icon: '🐢',
        damage: 2,
        size: 1
    },
    piranha: {
        name: 'Piranha Plant',
        health: 30,
        speed: 0.6,
        reward: 20,
        icon: '🌱',
        damage: 3,
        size: 1
    },
    bowser: {
        name: 'Bowser Jr',
        health: 50,
        speed: 0.5,
        reward: 50,
        icon: '🦖',
        damage: 5,
        size: 1
    },
    bill: {
        name: 'Bullet Bill',
        health: 15,
        speed: 2,
        reward: 25,
        icon: '🔫',
        damage: 2,
        size: 1
    },
    boss: {
        name: 'King Bowser',
        health: 100,
        speed: 0.4,
        reward: 200,
        icon: '👑',
        damage: 8,
        size: 1.8
    }
};

// Level waves
const LEVELS = [
    { // Level 1
        waves: [
            { type: 'goomba', count: 5, interval: 500 },
            { type: 'goomba', count: 8, interval: 400 }
        ],
        initialGold: 500,
        multiplier: 1,
        hasBoss: false
    },
    { // Level 2
        waves: [
            { type: 'goomba', count: 10, interval: 300 },
            { type: 'koopa', count: 5, interval: 500 }
        ],
        initialGold: 300,
        multiplier: 1.1,
        hasBoss: false
    },
    { // Level 3
        waves: [
            { type: 'koopa', count: 8, interval: 400 },
            { type: 'goomba', count: 10, interval: 250 }
        ],
        initialGold: 200,
        multiplier: 1.2,
        hasBoss: false
    },
    { // Level 4
        waves: [
            { type: 'piranha', count: 8, interval: 400 },
            { type: 'koopa', count: 10, interval: 300 }
        ],
        initialGold: 250,
        multiplier: 1.25,
        hasBoss: false
    },
    { // Level 5
        waves: [
            { type: 'goomba', count: 18, interval: 150 },
            { type: 'piranha', count: 10, interval: 400 }
        ],
        initialGold: 200,
        multiplier: 1.35,
        hasBoss: false
    },
    { // Level 6
        waves: [
            { type: 'koopa', count: 15, interval: 200 },
            { type: 'bill', count: 10, interval: 250 }
        ],
        initialGold: 300,
        multiplier: 1.4,
        hasBoss: false
    },
    { // Level 7
        waves: [
            { type: 'piranha', count: 12, interval: 300 },
            { type: 'bill', count: 12, interval: 200 },
            { type: 'koopa', count: 10, interval: 250 }
        ],
        initialGold: 250,
        multiplier: 1.45,
        hasBoss: false
    },
    { // Level 8
        waves: [
            { type: 'bill', count: 15, interval: 150 },
            { type: 'piranha', count: 12, interval: 300 }
        ],
        initialGold: 200,
        multiplier: 1.5,
        hasBoss: false
    },
    { // Level 9
        waves: [
            { type: 'koopa', count: 18, interval: 150 },
            { type: 'piranha', count: 14, interval: 250 },
            { type: 'bill', count: 10, interval: 200 }
        ],
        initialGold: 250,
        multiplier: 1.55,
        hasBoss: false
    },
    { // Level 10 - Final Level
        waves: [
            { type: 'bill', count: 20, interval: 100 },
            { type: 'piranha', count: 15, interval: 200 }
        ],
        initialGold: 300,
        multiplier: 1.6,
        hasBoss: false
    }
];

// Game state
const gameState = {
    currentLevel: 1,
    score: 0,
    gold: 500,
    lives: 20,
    isPaused: false,
    gameOver: false,
    gameWon: false,
    selectedTower: null,
    towers: [],
    enemies: [],
    projectiles: [],
    explosions: [],
    path: [],
    currentWave: 0,
    waveInProgress: false,
    waveIndex: 0,
    currentWaveData: [],
    enemySpawnIndex: 0,
    lastEnemySpawnTime: 0,
    gameStarted: false,
    gameLoopRunning: false,
    speedMultiplier: 1,
    selectedTowerIndex: null
};

// Canvas and context
let canvas;
let ctx;

// Initialize game
function init() {
    canvas = document.getElementById('gameCanvas');
    canvas.width = CANVAS_WIDTH;
    canvas.height = CANVAS_HEIGHT;
    ctx = canvas.getContext('2d');
    
    setupPathway();
    attachEventListeners();
    showMenu();
}

// Setup the path for enemies
function setupPathway() {
    gameState.path = [
        { x: -50, y: 120 },   // off-screen start (top-left)
        { x: 820, y: 120 },   // long right across top
        
        // First vertical drop and loop
        { x: 820, y: 230 },   // down right
        { x: 75, y: 230 },    // left across middle-upper
        
        // Second loop
        { x: 75, y: 310 },    // down left
        { x: 820, y: 310 },   // right across middle
        
        // Third loop
        { x: 820, y: 390 },   // down right
        { x: 150, y: 390 },   // left across middle-lower
        
        // Fourth loop
        { x: 150, y: 480 },   // down left
        { x: 820, y: 480 },   // right across
        
        // Fifth loop
        { x: 820, y: 560 },   // down right
        { x: 75, y: 560 },    // left across lower
        
        // Final segments to exit
        { x: 75, y: 680 },    // down to bottom
        { x: 950, y: 680 },   // right across bottom
        { x: 950, y: 850 }    // off-screen exit (bottom)
    ];
}

// Attach event listeners
function attachEventListeners() {
    // Tower selection
    document.querySelectorAll('.tower-item').forEach(item => {
        item.addEventListener('click', () => {
            document.querySelectorAll('.tower-item').forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            gameState.selectedTower = item.dataset.tower;
            gameState.selectedTowerIndex = null;
            document.getElementById('towerInfo').classList.add('hidden');
        });
    });
    
    // Canvas click for tower placement or tower selection
    canvas.addEventListener('click', (e) => {
        if (gameState.isPaused || !gameState.gameStarted) return;
        
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        // Check if clicking on existing tower
        let clickedTower = -1;
        for (let i = 0; i < gameState.towers.length; i++) {
            const tower = gameState.towers[i];
            const dist = Math.sqrt((x - tower.x) ** 2 + (y - tower.y) ** 2);
            if (dist < 25) {
                clickedTower = i;
                break;
            }
        }
        
        if (clickedTower >= 0) {
            selectTower(clickedTower);
            return;
        }
        
        // Place new tower
        if (!gameState.selectedTower) return;
        placeTower(x, y);
    });
    
    // Buttons
    document.getElementById('startWaveBtn').addEventListener('click', startWave);
    document.getElementById('pauseBtn').addEventListener('click', togglePause);
    document.getElementById('speedBtn').addEventListener('click', cycleSpeed);
    document.getElementById('saveBtn').addEventListener('click', saveGame);
    document.getElementById('loadBtn').addEventListener('click', loadGame);
    document.getElementById('resetBtn').addEventListener('click', resetGame);
    document.getElementById('sellTowerBtn').addEventListener('click', sellSelectedTower);
    document.getElementById('cancelBtn').addEventListener('click', deselectTower);
    
    // Menu buttons
    document.getElementById('newGameBtn').addEventListener('click', newGame);
    document.getElementById('loadGameBtn').addEventListener('click', loadGame);
    document.getElementById('retryBtn').addEventListener('click', newGame);
    document.getElementById('menuBtn').addEventListener('click', showMenu);
}

// Place tower on canvas
function placeTower(x, y) {
    const towerType = gameState.selectedTower;
    const towerCost = TOWERS[towerType].cost;
    
    if (gameState.gold < towerCost) {
        alert('Not enough gold!');
        return;
    }
    
    // Check if tower placement is valid (not on path)
    if (isOnPath(x, y)) {
        alert('Cannot place tower on path!');
        return;
    }
    
    gameState.towers.push({
        type: towerType,
        x: x,
        y: y,
        lastShot: 0,
        targeting: null
    });
    
    gameState.gold -= towerCost;
    updateUI();
}

// Check if position is on path
function isOnPath(x, y, tolerance = 30) {
    for (let point of gameState.path) {
        const dist = Math.sqrt((x - point.x) ** 2 + (y - point.y) ** 2);
        if (dist < tolerance) return true;
    }
    return false;
}

// Start wave
function startWave() {
    if (gameState.waveInProgress || gameState.gameOver || gameState.gameWon) return;
    
    gameState.waveInProgress = true;
    gameState.waveIndex = 0;
    gameState.currentWave++;
    gameState.enemySpawnIndex = 0;
    gameState.lastEnemySpawnTime = 0;
    gameState.currentWaveData = [];
    
    // Show wave notification
    showWaveNotification(`WAVE ${gameState.currentWave}`);
    
    // Build wave data from all waves in current level with scaling
    const level = LEVELS[gameState.currentLevel - 1];
    let lastSpawnTime = 0;
    
    for (let waveIdx = 0; waveIdx < level.waves.length; waveIdx++) {
        const wave = level.waves[waveIdx];
        // Scale enemy count based on wave number (but NOT boss enemies)
        const scaledCount = wave.type === 'boss' 
            ? wave.count 
            : Math.ceil(wave.count * (1 + (gameState.currentWave - 1) * 0.15));
        
        for (let i = 0; i < scaledCount; i++) {
            // Add randomization to spawn timing (±50% of interval)
            const randomVariation = (Math.random() - 0.5) * wave.interval;
            const spawnTime = lastSpawnTime + i * wave.interval + randomVariation;
            
            gameState.currentWaveData.push({
                type: wave.type,
                spawnTime: Math.max(0, spawnTime) // Ensure no negative spawn times
            });
        }
        
        lastSpawnTime += scaledCount * wave.interval;
        
        // Add a boss at the end of each wave
        gameState.currentWaveData.push({
            type: 'boss',
            spawnTime: lastSpawnTime + 500
        });
        
        lastSpawnTime += 500;
    }
    
    // Add additional bosses at the end of the level (one for each level number)
    for (let i = 0; i < gameState.currentLevel; i++) {
        gameState.currentWaveData.push({
            type: 'boss',
            spawnTime: lastSpawnTime + (i + 1) * 1000
        });
    }
    
    // Sort by spawn time to maintain proper order
    gameState.currentWaveData.sort((a, b) => a.spawnTime - b.spawnTime);
    
    document.getElementById('startWaveBtn').disabled = true;
    
    if (!gameState.gameLoopRunning) {
        gameState.gameLoopRunning = true;
        gameLoop();
    }
}

// Select tower to sell
function selectTower(index) {
    gameState.selectedTowerIndex = index;
    const tower = gameState.towers[index];
    const refund = Math.floor(TOWERS[tower.type].cost * 0.75);
    
    document.getElementById('towerDetails').innerHTML = `
        <div style="margin-bottom: 10px;">
            <strong>${TOWERS[tower.type].name}</strong><br/>
            Cost: ${TOWERS[tower.type].cost}G<br/>
            Sell Price: ${refund}G
        </div>
    `;
    
    document.getElementById('towerInfo').classList.remove('hidden');
    document.querySelectorAll('.tower-item').forEach(i => i.classList.remove('active'));
    gameState.selectedTower = null;
}

// Deselect tower
function deselectTower() {
    gameState.selectedTowerIndex = null;
    document.getElementById('towerInfo').classList.add('hidden');
}

// Sell selected tower
function sellSelectedTower() {
    if (gameState.selectedTowerIndex === null) return;
    
    const tower = gameState.towers[gameState.selectedTowerIndex];
    const refund = Math.floor(TOWERS[tower.type].cost * 0.75);
    
    gameState.gold += refund;
    gameState.towers.splice(gameState.selectedTowerIndex, 1);
    gameState.selectedTowerIndex = null;
    
    document.getElementById('towerInfo').classList.add('hidden');
    updateUI();
}

// Toggle double speed
// Cycle through game speeds: 1x -> 2x -> 4x -> 1x
function cycleSpeed() {
    const speedBtn = document.getElementById('speedBtn');
    
    // Cycle: 1 -> 2 -> 4 -> 1
    if (gameState.speedMultiplier === 1) {
        gameState.speedMultiplier = 2;
        speedBtn.textContent = 'Speed: 2x';
        speedBtn.classList.add('active');
    } else if (gameState.speedMultiplier === 2) {
        gameState.speedMultiplier = 4;
        speedBtn.textContent = 'Speed: 4x';
        speedBtn.classList.add('active');
    } else {
        gameState.speedMultiplier = 1;
        speedBtn.textContent = 'Speed: 1x';
        speedBtn.classList.remove('active');
    }
}

// Reset game
function resetGame() {
    if (!confirm('Are you sure you want to reset? Progress will be lost.')) return;
    newGame();
}

// Show wave notification
function showWaveNotification(message) {
    const notification = document.getElementById('waveNotification');
    document.getElementById('waveMessage').textContent = message;
    notification.classList.remove('hidden');
    
    // Hide after 1.5 seconds
    setTimeout(() => {
        notification.classList.add('hidden');
    }, 1500);
}

// Toggle pause
function togglePause() {
    if (!gameState.gameStarted) return;
    gameState.isPaused = !gameState.isPaused;
    
    const pauseDisplay = document.querySelector('.game-paused');
    if (gameState.isPaused) {
        if (!pauseDisplay) {
            const div = document.createElement('div');
            div.className = 'game-paused show';
            div.innerHTML = '<h2>PAUSED</h2>';
            document.getElementById('gameContainer').appendChild(div);
        } else {
            pauseDisplay.classList.add('show');
        }
    } else {
        pauseDisplay?.classList.remove('show');
        gameLoop();
    }
}

// Main game loop
function gameLoop() {
    if (gameState.isPaused || gameState.gameOver || gameState.gameWon) {
        requestAnimationFrame(gameLoop);
        return;
    }
    
    const timeStep = 16 * gameState.speedMultiplier; // Speed multiplier: 1x, 2x, or 4x
    
    // Spawn enemies from current wave
    if (gameState.waveInProgress && gameState.enemySpawnIndex < gameState.currentWaveData.length) {
        const enemyData = gameState.currentWaveData[gameState.enemySpawnIndex];
        if (gameState.lastEnemySpawnTime >= enemyData.spawnTime) {
            spawnEnemy(enemyData.type);
            gameState.enemySpawnIndex++;
        }
        gameState.lastEnemySpawnTime += timeStep; // ~60fps or ~30fps with 2x speed
    }
    
    // Update enemies
    updateEnemies();
    
    // Update towers
    updateTowers();
    
    // Update projectiles
    updateProjectiles();
    
    // Update explosions
    updateExplosions();
    
    // Draw everything
    draw();
    
    // Check wave completion
    if (gameState.waveInProgress && gameState.enemySpawnIndex >= gameState.currentWaveData.length && gameState.enemies.length === 0) {
        gameState.waveInProgress = false;
        
        // Check if all waves in current level are complete
        const currentLevelDef = LEVELS[gameState.currentLevel - 1];
        if (gameState.currentWave >= currentLevelDef.waves.length) {
            // Level complete - advance to next level
            if (gameState.currentLevel >= 10) {
                winGame();
            } else {
                gameState.currentLevel++;
                gameState.currentWave = 0;
                showWaveNotification(`LEVEL ${gameState.currentLevel}`);
                updateUI();
            }
        } else {
            updateUI();
        }
        
        document.getElementById('startWaveBtn').disabled = false;
    }
    
    // Game over condition
    if (gameState.lives <= 0) {
        gameOver();
    }
    
    requestAnimationFrame(gameLoop);
}

// Create explosion particles
function createExplosionParticles(x, y) {
    const particles = [];
    const particleCount = 12;
    
    for (let i = 0; i < particleCount; i++) {
        const angle = (i / particleCount) * Math.PI * 2;
        const speed = 3 + Math.random() * 2;
        
        particles.push({
            x: x,
            y: y,
            vx: Math.cos(angle) * speed,
            vy: Math.sin(angle) * speed,
            lifetime: 30,
            maxLifetime: 30,
            size: 4 + Math.random() * 4
        });
    }
    
    return particles;
}

// Update explosions
function updateExplosions() {
    for (let i = gameState.explosions.length - 1; i >= 0; i--) {
        const explosion = gameState.explosions[i];
        
        // Update main explosion circle
        explosion.lifetime--;
        explosion.radius = (explosion.maxRadius * (1 - explosion.lifetime / explosion.maxLifetime));
        
        // Update particles
        for (let j = explosion.particles.length - 1; j >= 0; j--) {
            const particle = explosion.particles[j];
            particle.x += particle.vx;
            particle.y += particle.vy;
            particle.lifetime--;
            particle.vy += 0.2; // gravity
        }
        
        // Remove dead particles
        explosion.particles = explosion.particles.filter(p => p.lifetime > 0);
        
        // Remove dead explosion
        if (explosion.lifetime <= 0) {
            gameState.explosions.splice(i, 1);
        }
    }
}

// Spawn wave enemies
function spawnEnemy(enemyType) {
    const enemyDef = ENEMIES[enemyType];
    const level = gameState.currentLevel;
    
    // Scale enemy stats by level and wave
    const healthMultiplier = 1 + (level - 1) * 0.3 + (gameState.currentWave - 1) * 0.1;
    const speedMultiplier = 1 + (level - 1) * 0.1 + (gameState.currentWave - 1) * 0.05;
    const rewardMultiplier = 1 + (level - 1) * 0.2 + (gameState.currentWave - 1) * 0.1;
    
    gameState.enemies.push({
        type: enemyType,
        pathIndex: 0,
        pathProgress: 0,
        health: enemyDef.health * healthMultiplier,
        maxHealth: enemyDef.health * healthMultiplier,
        speed: enemyDef.speed * GAME_SPEED * speedMultiplier,
        x: gameState.path[0].x,
        y: gameState.path[0].y,
        baseReward: enemyDef.reward,
        rewardMultiplier: rewardMultiplier,
        level: level,
        size: enemyDef.size || 1
    });
}

// Update enemies
function updateEnemies() {
    for (let i = gameState.enemies.length - 1; i >= 0; i--) {
        const enemy = gameState.enemies[i];
        
        if (enemy.pathIndex >= gameState.path.length - 1) {
            // Enemy reached end
            gameState.lives--;
            gameState.enemies.splice(i, 1);
            updateUI();
            continue;
        }
        
        // Move along path
        enemy.pathProgress += enemy.speed;
        
        const currentPoint = gameState.path[enemy.pathIndex];
        const nextPoint = gameState.path[enemy.pathIndex + 1];
        
        const dx = nextPoint.x - currentPoint.x;
        const dy = nextPoint.y - currentPoint.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        
        if (enemy.pathProgress >= dist) {
            enemy.pathProgress -= dist;
            enemy.pathIndex++;
        }
        
        if (enemy.pathIndex < gameState.path.length) {
            const curr = gameState.path[enemy.pathIndex];
            const next = gameState.path[Math.min(enemy.pathIndex + 1, gameState.path.length - 1)];
            
            const dx = next.x - curr.x;
            const dy = next.y - curr.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            
            enemy.x = curr.x + (dx / dist) * enemy.pathProgress;
            enemy.y = curr.y + (dy / dist) * enemy.pathProgress;
        }
        
        // Remove if dead
        if (enemy.health <= 0) {
            // Create explosion animation
            gameState.explosions.push({
                x: enemy.x,
                y: enemy.y,
                radius: 5,
                maxRadius: 40,
                lifetime: 30,
                maxLifetime: 30,
                particles: createExplosionParticles(enemy.x, enemy.y)
            });
            
            // Award scaled gold and score
            const reward = Math.floor(ENEMIES[enemy.type].reward * enemy.rewardMultiplier);
            gameState.score += reward;
            gameState.gold += reward;
            gameState.enemies.splice(i, 1);
            updateUI();
        }
    }
}

// Update towers
function updateTowers() {
    const timeStep = 16 * gameState.speedMultiplier;
    
    for (let tower of gameState.towers) {
        tower.lastShot += timeStep; // ~60fps or 2x with double speed
        
        // Find target
        let target = null;
        for (let enemy of gameState.enemies) {
            const dist = Math.sqrt((tower.x - enemy.x) ** 2 + (tower.y - enemy.y) ** 2);
            if (dist < TOWERS[tower.type].range) {
                target = enemy;
                break;
            }
        }
        
        // Shoot
        if (target && tower.lastShot >= 1000 / TOWERS[tower.type].fireRate) {
            gameState.projectiles.push({
                x: tower.x,
                y: tower.y,
                targetEnemy: target,
                towerType: tower.type,
                damage: TOWERS[tower.type].damage
            });
            tower.lastShot = 0;
        }
    }
}

// Update projectiles
function updateProjectiles() {
    for (let i = gameState.projectiles.length - 1; i >= 0; i--) {
        const proj = gameState.projectiles[i];
        
        if (!proj.targetEnemy || proj.targetEnemy.health <= 0) {
            gameState.projectiles.splice(i, 1);
            continue;
        }
        
        // Move towards target
        const dx = proj.targetEnemy.x - proj.x;
        const dy = proj.targetEnemy.y - proj.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        
        if (dist < 10) {
            // Hit
            proj.targetEnemy.health -= proj.damage;
            
            // Area damage for certain towers
            if (proj.towerType === 'bob-omb') {
                for (let enemy of gameState.enemies) {
                    const splashDist = Math.sqrt((proj.x - enemy.x) ** 2 + (proj.y - enemy.y) ** 2);
                    if (splashDist < 60 && enemy !== proj.targetEnemy) {
                        enemy.health -= proj.damage * 0.5;
                    }
                }
            }
            
            gameState.projectiles.splice(i, 1);
        } else {
            proj.x += (dx / dist) * 5;
            proj.y += (dy / dist) * 5;
        }
    }
}

// Draw everything
function draw() {
    // Clear canvas
    ctx.fillStyle = '#87ceeb';
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    
    // Draw path
    ctx.strokeStyle = '#8B7355';
    ctx.lineWidth = 60;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.beginPath();
    ctx.moveTo(gameState.path[0].x, gameState.path[0].y);
    for (let i = 1; i < gameState.path.length; i++) {
        ctx.lineTo(gameState.path[i].x, gameState.path[i].y);
    }
    ctx.stroke();
    
    // Draw towers
    for (let i = 0; i < gameState.towers.length; i++) {
        const tower = gameState.towers[i];
        ctx.font = '32px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(TOWERS[tower.type].icon, tower.x, tower.y);
        
        // Highlight selected tower
        if (gameState.selectedTowerIndex === i) {
            ctx.strokeStyle = '#FFD700';
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.arc(tower.x, tower.y, 28, 0, Math.PI * 2);
            ctx.stroke();
        }
        
        // Draw range (debug)
        // ctx.strokeStyle = 'rgba(255, 0, 0, 0.2)';
        // ctx.beginPath();
        // ctx.arc(tower.x, tower.y, TOWERS[tower.type].range, 0, Math.PI * 2);
        // ctx.stroke();
    }
    
    // Draw enemies
    for (let enemy of gameState.enemies) {
        const isBoss = enemy.type === 'boss';
        const fontSize = 24 * enemy.size;
        
        // Draw boss background glow
        if (isBoss) {
            ctx.fillStyle = 'rgba(255, 100, 0, 0.3)';
            ctx.beginPath();
            ctx.arc(enemy.x, enemy.y, (fontSize / 2) + 15, 0, Math.PI * 2);
            ctx.fill();
            
            // Outer ring
            ctx.strokeStyle = '#ff6600';
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.arc(enemy.x, enemy.y, (fontSize / 2) + 12, 0, Math.PI * 2);
            ctx.stroke();
        }
        
        ctx.font = `${fontSize}px Arial`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(ENEMIES[enemy.type].icon, enemy.x, enemy.y);
        
        // Draw health bar (scaled for boss size)
        const barWidth = 30 * enemy.size;
        const barHeight = isBoss ? 8 : 4;
        const barY = enemy.y - (20 + 5 * enemy.size);
        
        // Boss health bar has border
        if (isBoss) {
            ctx.strokeStyle = '#ffd700';
            ctx.lineWidth = 2;
            ctx.strokeRect(enemy.x - barWidth / 2 - 1, barY - 1, barWidth + 2, barHeight + 2);
        }
        
        ctx.fillStyle = 'red';
        ctx.fillRect(enemy.x - barWidth / 2, barY, barWidth, barHeight);
        ctx.fillStyle = '#00ff00';
        ctx.fillRect(enemy.x - barWidth / 2, barY, (barWidth * enemy.health) / enemy.maxHealth, barHeight);
        
        // Boss label above health bar
        if (isBoss) {
            ctx.fillStyle = '#ff6600';
            ctx.font = 'bold 12px Arial';
            ctx.fillText('👑', enemy.x, barY - 10);
            ctx.font = `${fontSize}px Arial`;
        }
    }
    
    // Draw projectiles
    for (let proj of gameState.projectiles) {
        ctx.fillStyle = '#FFD700';
        ctx.beginPath();
        ctx.arc(proj.x, proj.y, 4, 0, Math.PI * 2);
        ctx.fill();
    }
    
    // Draw explosions
    for (let explosion of gameState.explosions) {
        // Draw main explosion circle
        const alpha = explosion.lifetime / explosion.maxLifetime;
        ctx.fillStyle = `rgba(255, 150, 0, ${alpha * 0.6})`;
        ctx.beginPath();
        ctx.arc(explosion.x, explosion.y, explosion.radius, 0, Math.PI * 2);
        ctx.fill();
        
        // Draw border
        ctx.strokeStyle = `rgba(255, 100, 0, ${alpha * 0.8})`;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(explosion.x, explosion.y, explosion.radius, 0, Math.PI * 2);
        ctx.stroke();
        
        // Draw particles
        for (let particle of explosion.particles) {
            const particleAlpha = particle.lifetime / particle.maxLifetime;
            ctx.fillStyle = `rgba(255, 200, 0, ${particleAlpha * 0.8})`;
            ctx.beginPath();
            ctx.arc(particle.x, particle.y, particle.size * particleAlpha, 0, Math.PI * 2);
            ctx.fill();
        }
    }
}

// Update UI
function updateUI() {
    document.getElementById('levelDisplay').textContent = gameState.currentLevel;
    document.getElementById('scoreDisplay').textContent = gameState.score;
    document.getElementById('goldDisplay').textContent = gameState.gold;
    document.getElementById('livesDisplay').textContent = gameState.lives;
    document.getElementById('waveStatus').textContent = `Wave: ${gameState.currentWave}/${LEVELS[gameState.currentLevel - 1].waves.length}`;
}

// New game
function newGame() {
    gameState.currentLevel = 1;
    gameState.score = 0;
    gameState.gold = 500;
    gameState.lives = 20;
    gameState.isPaused = false;
    gameState.gameOver = false;
    gameState.gameWon = false;
    gameState.selectedTower = null;
    gameState.towers = [];
    gameState.enemies = [];
    gameState.projectiles = [];
    gameState.explosions = [];
    gameState.currentWave = 0;
    gameState.waveInProgress = false;
    gameState.waveIndex = 0;
    gameState.gameStarted = true;
    gameState.gameLoopRunning = true;
    gameState.currentWaveData = [];
    gameState.enemySpawnIndex = 0;
    gameState.lastEnemySpawnTime = 0;
    gameState.speedMultiplier = 1;
    gameState.selectedTowerIndex = null;
    
    document.getElementById('menu').classList.add('hidden');
    document.getElementById('gameOverMenu').classList.add('hidden');
    document.querySelector('.game-paused')?.remove();
    document.getElementById('towerInfo').classList.add('hidden');
    document.getElementById('speedBtn').classList.remove('active');
    document.getElementById('speedBtn').textContent = 'Speed: 1x';
    
    updateUI();
    gameLoop();
}

// Save game
function saveGame() {
    const saveData = {
        currentLevel: gameState.currentLevel,
        score: gameState.score,
        gold: gameState.gold,
        lives: gameState.lives,
        towers: gameState.towers.map(t => ({ type: t.type, x: t.x, y: t.y })),
        enemies: gameState.enemies,
        currentWave: gameState.currentWave,
        timestamp: new Date().toLocaleString()
    };
    
    localStorage.setItem('marioTDSave', JSON.stringify(saveData));
    alert('Game saved successfully!');
}

// Load game
function loadGame() {
    const saveData = localStorage.getItem('marioTDSave');
    if (!saveData) {
        alert('No save file found!');
        return;
    }
    
    const data = JSON.parse(saveData);
    gameState.currentLevel = data.currentLevel;
    gameState.score = data.score;
    gameState.gold = data.gold;
    gameState.lives = data.lives;
    gameState.towers = data.towers;
    gameState.enemies = data.enemies;
    gameState.currentWave = data.currentWave;
    gameState.gameStarted = true;
    gameState.gameOver = false;
    gameState.gameWon = false;
    
    document.getElementById('menu').classList.add('hidden');
    document.getElementById('gameOverMenu').classList.add('hidden');
    
    updateUI();
    gameLoop();
}

// Game over
function gameOver() {
    gameState.gameOver = true;
    const menuDiv = document.getElementById('gameOverMenu');
    document.getElementById('gameOverTitle').textContent = 'GAME OVER!';
    document.getElementById('gameOverStats').innerHTML = `
        <p>Final Score: ${gameState.score}</p>
        <p>Level Reached: ${gameState.currentLevel}</p>
        <p>Waves Completed: ${gameState.currentWave}</p>
    `;
    menuDiv.classList.remove('hidden');
}

// Win game
function winGame() {
    gameState.gameWon = true;
    const menuDiv = document.getElementById('gameOverMenu');
    document.getElementById('gameOverTitle').textContent = 'YOU WIN!';
    document.getElementById('gameOverStats').innerHTML = `
        <p>Final Score: ${gameState.score}</p>
        <p>Levels Completed: ${gameState.currentLevel}</p>
        <p>Gold Remaining: ${gameState.gold}</p>
    `;
    menuDiv.classList.remove('hidden');
}

// Show menu
function showMenu() {
    gameState.gameStarted = false;
    document.getElementById('menu').classList.remove('hidden');
    document.getElementById('gameOverMenu').classList.add('hidden');
}

// Start the game
window.addEventListener('DOMContentLoaded', init);
