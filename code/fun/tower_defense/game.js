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
    },
    cannon: {
        name: 'Cannon',
        cost: 180,
        damage: 35,
        range: 140,
        fireRate: 0.6,
        icon: '🏹',
        description: 'Anti-air tower, effective against flying enemies'
    }
};

// Road hazards - bombs and traps
const HAZARDS = {
    bomb: {
        name: 'Bomb',
        cost: 75,
        damage: 60,
        radius: 80,
        icon: '💣',
        description: 'Explodes when enemy passes, damages all nearby'
    },
    trap: {
        name: 'Spike Trap',
        cost: 50,
        damage: 40,
        slowDuration: 2000,
        icon: '🌹',
        description: 'Damages and slows enemies that hit it'
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
    },
    buzzy: {
        name: 'Buzzy Beetle',
        health: 25,
        speed: 1.5,
        reward: 35,
        icon: '🐝',
        damage: 2,
        size: 0.9,
        isFlying: true
    },
    lakitu: {
        name: 'Lakitu',
        health: 40,
        speed: 1.2,
        reward: 60,
        icon: '☁️',
        damage: 3,
        size: 1.1,
        isFlying: true
    },
    birdo: {
        name: 'Birdo',
        health: 35,
        speed: 1.8,
        reward: 50,
        icon: '🦅',
        damage: 4,
        size: 1.0,
        isFlying: true
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
            { type: 'koopa', count: 10, interval: 300 },
            { type: 'buzzy', count: 5, interval: 500 }
        ],
        initialGold: 250,
        multiplier: 1.25,
        hasBoss: false
    },
    { // Level 5
        waves: [
            { type: 'goomba', count: 18, interval: 150 },
            { type: 'piranha', count: 10, interval: 400 },
            { type: 'buzzy', count: 8, interval: 350 }
        ],
        initialGold: 200,
        multiplier: 1.35,
        hasBoss: false
    },
    { // Level 6
        waves: [
            { type: 'koopa', count: 15, interval: 200 },
            { type: 'bill', count: 10, interval: 250 },
            { type: 'lakitu', count: 6, interval: 400 }
        ],
        initialGold: 300,
        multiplier: 1.4,
        hasBoss: false
    },
    { // Level 7
        waves: [
            { type: 'piranha', count: 12, interval: 300 },
            { type: 'bill', count: 12, interval: 200 },
            { type: 'koopa', count: 10, interval: 250 },
            { type: 'lakitu', count: 8, interval: 300 }
        ],
        initialGold: 250,
        multiplier: 1.45,
        hasBoss: false
    },
    { // Level 8
        waves: [
            { type: 'bill', count: 15, interval: 150 },
            { type: 'piranha', count: 12, interval: 300 },
            { type: 'birdo', count: 7, interval: 350 }
        ],
        initialGold: 200,
        multiplier: 1.5,
        hasBoss: false
    },
    { // Level 9
        waves: [
            { type: 'koopa', count: 18, interval: 150 },
            { type: 'piranha', count: 14, interval: 250 },
            { type: 'bill', count: 10, interval: 200 },
            { type: 'birdo', count: 10, interval: 300 }
        ],
        initialGold: 250,
        multiplier: 1.55,
        hasBoss: false
    },
    { // Level 10 - Final Level
        waves: [
            { type: 'bill', count: 20, interval: 100 },
            { type: 'piranha', count: 15, interval: 200 },
            { type: 'lakitu', count: 12, interval: 250 },
            { type: 'birdo', count: 10, interval: 200 }
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
    hazards: [],
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
    selectedTowerIndex: null,
    endGateDamage: 0,
    moveMode: false,
    movingTowerIndex: null,
    selectedHazard: null
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
            document.querySelectorAll('.hazard-item').forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            gameState.selectedTower = item.dataset.tower;
            gameState.selectedHazard = null;
            gameState.selectedTowerIndex = null;
            document.getElementById('towerInfo').classList.add('hidden');
        });
    });
    
    // Hazard selection
    document.querySelectorAll('.hazard-item').forEach(item => {
        item.addEventListener('click', () => {
            document.querySelectorAll('.hazard-item').forEach(i => i.classList.remove('active'));
            document.querySelectorAll('.tower-item').forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            gameState.selectedHazard = item.dataset.hazard;
            gameState.selectedTower = null;
            gameState.selectedTowerIndex = null;
            document.getElementById('towerInfo').classList.add('hidden');
        });
    });
    
    // Canvas click for tower placement or tower selection
    canvas.addEventListener('click', (e) => {
        if (gameState.isPaused || !gameState.gameStarted) return;
        
        // If in move mode, try to place tower at new location
        if (gameState.moveMode) {
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            moveTowerToLocation(gameState.movingTowerIndex, x, y);
            return;
        }
        
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
        if (gameState.selectedTower) {
            placeTower(x, y);
            return;
        }
        
        // Place hazard on road
        if (gameState.selectedHazard) {
            placeHazard(x, y);
            return;
        }
    });
    
    // Canvas double-click for move mode
    canvas.addEventListener('dblclick', (e) => {
        if (gameState.isPaused || !gameState.gameStarted) return;
        
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        // Check if double-clicking on existing tower
        for (let i = 0; i < gameState.towers.length; i++) {
            const tower = gameState.towers[i];
            const dist = Math.sqrt((x - tower.x) ** 2 + (y - tower.y) ** 2);
            if (dist < 25) {
                enterMoveMode(i);
                return;
            }
        }
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
        targeting: null,
        upgradeLevel: 0
    });
    
    gameState.gold -= towerCost;
    updateUI();
}

// Place hazard on road
function placeHazard(x, y) {
    const hazardType = gameState.selectedHazard;
    const hazardCost = HAZARDS[hazardType].cost;
    
    if (gameState.gold < hazardCost) {
        alert('Not enough gold!');
        return;
    }
    
    // Check if hazard is on path (required for road hazards)
    if (!isOnPath(x, y, 40)) {
        alert('Hazard must be placed on the road!');
        return;
    }
    
    gameState.hazards.push({
        type: hazardType,
        x: x,
        y: y,
        active: true,
        triggered: false
    });
    
    gameState.gold -= hazardCost;
    updateUI();
}

// Check if position is on path - check distance to road line segments
function isOnPath(x, y, tolerance = 35) {
    for (let i = 0; i < gameState.path.length - 1; i++) {
        const p1 = gameState.path[i];
        const p2 = gameState.path[i + 1];
        
        // Calculate distance from point (x, y) to line segment p1-p2
        const dist = distanceToLineSegment(x, y, p1.x, p1.y, p2.x, p2.y);
        if (dist < tolerance) return true;
    }
    return false;
}

// Helper function: distance from point to line segment
function distanceToLineSegment(px, py, x1, y1, x2, y2) {
    const dx = x2 - x1;
    const dy = y2 - y1;
    const lengthSq = dx * dx + dy * dy;
    
    if (lengthSq === 0) {
        // Segment is a point
        return Math.sqrt((px - x1) ** 2 + (py - y1) ** 2);
    }
    
    let t = ((px - x1) * dx + (py - y1) * dy) / lengthSq;
    t = Math.max(0, Math.min(1, t));
    
    const closestX = x1 + t * dx;
    const closestY = y1 + t * dy;
    
    return Math.sqrt((px - closestX) ** 2 + (py - closestY) ** 2);
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
    const upgradeCosts = [Math.floor(TOWERS[tower.type].cost * 2), Math.floor(TOWERS[tower.type].cost * 3), Math.floor(TOWERS[tower.type].cost * 4)];
    const nextUpgradeCost = tower.upgradeLevel < 3 ? upgradeCosts[tower.upgradeLevel] : 'MAX';
    const currentDamage = getTowerDamage(tower);
    const upgradedRange = getTowerRange(tower);
    
    let upgradeButtonHTML = '';
    if (tower.upgradeLevel < 3) {
        upgradeButtonHTML = `<button id="upgradeTowerBtn" style="margin-top: 10px; padding: 8px 12px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;">Upgrade (${nextUpgradeCost}G)</button>`;
    } else {
        upgradeButtonHTML = `<div style="margin-top: 10px; color: #888; font-size: 12px;">Upgrade: MAX LEVEL</div>`;
    }
    
    document.getElementById('towerDetails').innerHTML = `
        <div style="margin-bottom: 10px;">
            <strong>${TOWERS[tower.type].name}</strong><br/>
            Cost: ${TOWERS[tower.type].cost}G<br/>
            Damage: ${currentDamage.toFixed(1)}<br/>
            Range: ${upgradedRange.toFixed(1)}<br/>
            Upgrade Level: ${tower.upgradeLevel}/3<br/>
            Sell Price: ${refund}G
        </div>
        ${upgradeButtonHTML}
    `;
    
    document.getElementById('towerInfo').classList.remove('hidden');
    document.querySelectorAll('.tower-item').forEach(i => i.classList.remove('active'));
    gameState.selectedTower = null;
    
    // Attach upgrade button listener if not at max level
    if (tower.upgradeLevel < 3) {
        setTimeout(() => {
            const upgradeBtn = document.getElementById('upgradeTowerBtn');
            if (upgradeBtn) {
                upgradeBtn.addEventListener('click', upgradeTower);
            }
        }, 0);
    }
}

// Enter move mode for a tower
function enterMoveMode(towerIndex) {
    gameState.moveMode = true;
    gameState.movingTowerIndex = towerIndex;
    gameState.selectedTowerIndex = towerIndex;
    
    document.getElementById('towerDetails').innerHTML = `
        <div style="margin-bottom: 10px; padding: 10px; background-color: #FFA500; border-radius: 4px;">
            <strong>MOVE MODE</strong><br/>
            Click to place tower at new location<br/>
            <button id="cancelMoveBtn" style="margin-top: 8px; padding: 6px 12px; background-color: #f44336; color: white; border: none; border-radius: 4px; cursor: pointer; width: 100%;">Cancel Move</button>
        </div>
    `;
    
    document.getElementById('towerInfo').classList.remove('hidden');
    
    // Attach cancel button listener
    setTimeout(() => {
        const cancelBtn = document.getElementById('cancelMoveBtn');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', cancelMoveMode);
        }
    }, 0);
}

// Exit move mode without moving
function cancelMoveMode() {
    gameState.moveMode = false;
    gameState.movingTowerIndex = null;
    deselectTower();
}

// Move tower to new location
function moveTowerToLocation(towerIndex, newX, newY) {
    const tower = gameState.towers[towerIndex];
    
    // Check if new location is valid (not on path)
    if (isOnPath(newX, newY)) {
        alert('Cannot place tower on path!');
        return;
    }
    
    // Update tower position
    tower.x = newX;
    tower.y = newY;
    
    // Exit move mode
    gameState.moveMode = false;
    gameState.movingTowerIndex = null;
    gameState.selectedTowerIndex = towerIndex;
    
    // Show updated tower info
    selectTower(towerIndex);
    updateUI();
}


// Deselect tower
function deselectTower() {
    gameState.selectedTowerIndex = null;
    document.getElementById('towerInfo').classList.add('hidden');
}

// Upgrade tower
function upgradeTower() {
    if (gameState.selectedTowerIndex === null) return;
    
    const tower = gameState.towers[gameState.selectedTowerIndex];
    if (tower.upgradeLevel >= 3) return; // Already at max level
    
    const upgradeCosts = [Math.floor(TOWERS[tower.type].cost * 2), Math.floor(TOWERS[tower.type].cost * 3), Math.floor(TOWERS[tower.type].cost * 4)];
    const upgradeCost = upgradeCosts[tower.upgradeLevel];
    
    if (gameState.gold < upgradeCost) {
        alert('Not enough gold to upgrade!');
        return;
    }
    
    gameState.gold -= upgradeCost;
    tower.upgradeLevel++;
    updateUI();
    selectTower(gameState.selectedTowerIndex); // Refresh tower info display
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
            // Enemy reached end - damage the gate
            gameState.endGateDamage += 1;
            gameState.lives--;
            gameState.enemies.splice(i, 1);
            updateUI();
            continue;
        }
        
        // Move along path
        const speedMultiplier = enemy.slowedUntil && Date.now() < enemy.slowedUntil ? 0.5 : 1;
        enemy.pathProgress += enemy.speed * speedMultiplier * gameState.speedMultiplier;
        
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
        
        // Check hazard collisions
        checkHazardCollisions(enemy, i);
        
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

// Check if enemy hits any hazards on the road
function checkHazardCollisions(enemy, enemyIndex) {
    for (let i = gameState.hazards.length - 1; i >= 0; i--) {
        const hazard = gameState.hazards[i];
        if (!hazard.active) continue;
        
        const dist = Math.sqrt((enemy.x - hazard.x) ** 2 + (enemy.y - hazard.y) ** 2);
        
        if (dist < 25) {  // Hazard collision radius
            if (hazard.type === 'bomb') {
                // Bomb explodes - damages all enemies in radius
                const bombDamage = HAZARDS['bomb'].damage;
                const explosionRadius = HAZARDS['bomb'].radius;
                
                for (let j = 0; j < gameState.enemies.length; j++) {
                    const targetEnemy = gameState.enemies[j];
                    const distToBomb = Math.sqrt((targetEnemy.x - hazard.x) ** 2 + (targetEnemy.y - hazard.y) ** 2);
                    if (distToBomb < explosionRadius) {
                        targetEnemy.health -= bombDamage;
                    }
                }
                
                // Create explosion effect
                gameState.explosions.push({
                    x: hazard.x,
                    y: hazard.y,
                    radius: 5,
                    maxRadius: explosionRadius,
                    lifetime: 30,
                    maxLifetime: 30,
                    particles: createExplosionParticles(hazard.x, hazard.y)
                });
                
                hazard.active = false;
            } else if (hazard.type === 'trap') {
                // Trap damages and slows enemy
                if (!hazard.triggered) {
                    enemy.health -= HAZARDS['trap'].damage;
                    if (!enemy.slowedUntil) {
                        enemy.slowedUntil = Date.now() + HAZARDS['trap'].slowDuration;
                        enemy.slowMultiplier = 0.5;
                    }
                    hazard.triggered = true;
                    
                    // Trap can trigger multiple times (resets after 1 second)
                    setTimeout(() => {
                        hazard.triggered = false;
                    }, 1000);
                }
            }
            
            updateUI();
        }
    }
    
    // Apply slow effect if active
    if (enemy.slowedUntil && Date.now() < enemy.slowedUntil) {
        // Slow is already applied via slowMultiplier in speed calculation
    } else if (enemy.slowedUntil) {
        enemy.slowMultiplier = 1;
        enemy.slowedUntil = null;
    }
}

// Get upgraded tower range based on upgrade level
function getTowerRange(tower) {
    const rangeMultipliers = [1, 1.1, 1.2, 1.4];
    return TOWERS[tower.type].range * rangeMultipliers[tower.upgradeLevel];
}

// Get upgraded tower damage based on upgrade level
function getTowerDamage(tower) {
    const damageMultipliers = [1, 1.1, 1.2, 1.4];
    return TOWERS[tower.type].damage * damageMultipliers[tower.upgradeLevel];
}

// Update towers
function updateTowers() {
    const timeStep = 16 * gameState.speedMultiplier;
    
    for (let tower of gameState.towers) {
        tower.lastShot += timeStep; // ~60fps or 2x with double speed
        
        // Find target - aim at the leading enemy (furthest along path)
        let target = null;
        let maxPathProgress = -1;
        
        // Cannon prioritizes flying enemies
        if (tower.type === 'cannon') {
            // First pass: look for flying enemies in range
            for (let enemy of gameState.enemies) {
                const dist = Math.sqrt((tower.x - enemy.x) ** 2 + (tower.y - enemy.y) ** 2);
                if (dist < getTowerRange(tower) && ENEMIES[enemy.type].isFlying) {
                    // Calculate path progress: pathIndex + pathProgress
                    const pathProgress = enemy.pathIndex + enemy.pathProgress;
                    if (pathProgress > maxPathProgress) {
                        maxPathProgress = pathProgress;
                        target = enemy;
                    }
                }
            }
            // If no flying enemies in range, target any enemy (still aiming at leading one)
            if (!target) {
                maxPathProgress = -1;
                for (let enemy of gameState.enemies) {
                    const dist = Math.sqrt((tower.x - enemy.x) ** 2 + (tower.y - enemy.y) ** 2);
                    if (dist < getTowerRange(tower)) {
                        const pathProgress = enemy.pathIndex + enemy.pathProgress;
                        if (pathProgress > maxPathProgress) {
                            maxPathProgress = pathProgress;
                            target = enemy;
                        }
                    }
                }
            }
        } else {
            // Other towers: target the leading enemy in range
            for (let enemy of gameState.enemies) {
                const dist = Math.sqrt((tower.x - enemy.x) ** 2 + (tower.y - enemy.y) ** 2);
                if (dist < getTowerRange(tower)) {
                    const pathProgress = enemy.pathIndex + enemy.pathProgress;
                    if (pathProgress > maxPathProgress) {
                        maxPathProgress = pathProgress;
                        target = enemy;
                    }
                }
            }
        }
        
        // Shoot
        if (target && tower.lastShot >= (1000 / TOWERS[tower.type].fireRate) / gameState.speedMultiplier) {
            gameState.projectiles.push({
                x: tower.x,
                y: tower.y,
                targetEnemy: target,
                towerType: tower.type,
                damage: getTowerDamage(tower)
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
            const projSpeed = 8 * gameState.speedMultiplier;  // Increased speed and account for game speed
            proj.x += (dx / dist) * projSpeed;
            proj.y += (dy / dist) * projSpeed;
        }
    }
}

// Draw start gate
function drawStartGate() {
    // Position at the top-left entrance where enemies enter
    const x = 40;
    const y = 120;
    
    // Draw arrow pointing right into the path
    ctx.fillStyle = '#FFD700';
    ctx.strokeStyle = '#FFD700';
    ctx.lineWidth = 3;
    
    // Arrow shaft
    ctx.beginPath();
    ctx.moveTo(x - 30, y);
    ctx.lineTo(x + 15, y);
    ctx.stroke();
    
    // Arrow head (pointing right)
    ctx.beginPath();
    ctx.moveTo(x + 15, y);
    ctx.lineTo(x + 5, y - 12);
    ctx.lineTo(x + 5, y + 12);
    ctx.closePath();
    ctx.fill();
}

// Draw end gate with damage progression
function drawEndGate() {
    // Position at the bottom-right exit where enemies leave
    const x = 884;
    const y = 680;
    
    // Damage level (0-100%)
    const damagePercent = Math.min(gameState.endGateDamage * 10, 100); // Each enemy = 10% damage
    
    // Draw checkered finish line pattern - vertical across the road
    const squareSize = 15;
    const cols = 2;  // 2 columns wide (across the road width)
    const rows = 4;  // 4 rows tall
    
    for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
            // Alternate between black and white to create checkered pattern
            const isBlack = (row + col) % 2 === 0;
            ctx.fillStyle = isBlack ? '#000000' : '#FFFFFF';
            ctx.fillRect(x - 15 + (col * squareSize), y - 30 + (row * squareSize), squareSize, squareSize);
        }
    }
    
    // Add border to finish line
    ctx.strokeStyle = '#FFD700';
    ctx.lineWidth = 3;
    ctx.strokeRect(x - 15, y - 30, cols * squareSize, rows * squareSize);
    
    // Draw damage indicator above the finish line
    if (damagePercent > 0) {
        // Damage bar background
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(x - 15, y - 50, cols * squareSize, 15);
        
        // Damage bar fill
        const damageColor = damagePercent > 70 ? '#DC143C' : damagePercent > 40 ? '#FFA500' : '#FFD700';
        ctx.fillStyle = damageColor;
        ctx.fillRect(x - 15, y - 50, (cols * squareSize * damagePercent) / 100, 15);
        
        // Damage text
        ctx.fillStyle = '#FFFFFF';
        ctx.font = 'bold 10px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(`${Math.floor(damagePercent)}%`, x, y - 42);
    }
}

// Draw everything
function draw() {
    // Clear canvas
    ctx.fillStyle = '#87ceeb';
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    
    // Draw path with road texture
    // Main road asphalt
    ctx.strokeStyle = '#2C2C2C';
    ctx.lineWidth = 62;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.beginPath();
    ctx.moveTo(gameState.path[0].x, gameState.path[0].y);
    for (let i = 1; i < gameState.path.length; i++) {
        ctx.lineTo(gameState.path[i].x, gameState.path[i].y);
    }
    ctx.stroke();
    
    // Road surface (lighter shade)
    ctx.strokeStyle = '#4A4A4A';
    ctx.lineWidth = 58;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.beginPath();
    ctx.moveTo(gameState.path[0].x, gameState.path[0].y);
    for (let i = 1; i < gameState.path.length; i++) {
        ctx.lineTo(gameState.path[i].x, gameState.path[i].y);
    }
    ctx.stroke();
    
    // Yellow center line markings
    ctx.strokeStyle = '#FFD700';
    ctx.lineWidth = 2;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.setLineDash([10, 10]);
    ctx.beginPath();
    ctx.moveTo(gameState.path[0].x, gameState.path[0].y);
    for (let i = 1; i < gameState.path.length; i++) {
        ctx.lineTo(gameState.path[i].x, gameState.path[i].y);
    }
    ctx.stroke();
    ctx.setLineDash([]);
    
    // Draw start gate
    drawStartGate();
    
    // Draw towers
    for (let i = 0; i < gameState.towers.length; i++) {
        const tower = gameState.towers[i];
        ctx.font = '32px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillStyle = '#000000';  // Reset fill style to black
        ctx.fillText(TOWERS[tower.type].icon, tower.x, tower.y);
        
        // Draw upgrade stars below tower
        if (tower.upgradeLevel > 0) {
            ctx.font = '14px Arial';
            ctx.fillStyle = '#FFD700';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'top';
            const stars = '⭐'.repeat(tower.upgradeLevel);
            ctx.fillText(stars, tower.x, tower.y + 20);
        }
        
        // Highlight selected tower and show range
        if (gameState.selectedTowerIndex === i) {
            // Draw range circle - slightly darker transparent
            ctx.fillStyle = 'rgba(0, 0, 0, 0.15)';
            ctx.beginPath();
            ctx.arc(tower.x, tower.y, getTowerRange(tower), 0, Math.PI * 2);
            ctx.fill();
            
            // If in move mode, draw special indicator
            if (gameState.moveMode) {
                ctx.strokeStyle = '#FF6B35';
                ctx.lineWidth = 4;
                ctx.setLineDash([5, 5]);
                ctx.beginPath();
                ctx.arc(tower.x, tower.y, 35, 0, Math.PI * 2);
                ctx.stroke();
                ctx.setLineDash([]);
            } else {
                // Draw tower selection ring
                ctx.strokeStyle = '#FFD700';
                ctx.lineWidth = 3;
                ctx.beginPath();
                ctx.arc(tower.x, tower.y, 28, 0, Math.PI * 2);
                ctx.stroke();
            }
        }
        
        // Draw range (debug)
        // ctx.strokeStyle = 'rgba(255, 0, 0, 0.2)';
        // ctx.beginPath();
        // ctx.arc(tower.x, tower.y, TOWERS[tower.type].range, 0, Math.PI * 2);
        // ctx.stroke();
    }
    
    // Draw hazards
    for (let hazard of gameState.hazards) {
        if (!hazard.active) continue;
        
        ctx.font = '24px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillStyle = '#000000';  // Reset fill style to black
        ctx.fillText(HAZARDS[hazard.type].icon, hazard.x, hazard.y);
        
        // Draw hazard radius indicator
        if (hazard.type === 'bomb') {
            ctx.strokeStyle = 'rgba(200, 100, 0, 0.3)';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.arc(hazard.x, hazard.y, HAZARDS['bomb'].radius, 0, Math.PI * 2);
            ctx.stroke();
        }
    }
    
    // Draw enemies
    for (let enemy of gameState.enemies) {
        const isBoss = enemy.type === 'boss';
        const isFlying = ENEMIES[enemy.type].isFlying;
        const fontSize = 24 * enemy.size;
        
        ctx.font = `${fontSize}px Arial`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        // Draw shadow under flying enemies
        if (isFlying) {
            ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
            ctx.beginPath();
            ctx.ellipse(enemy.x, enemy.y + 15 * enemy.size, 15 * enemy.size, 8 * enemy.size, 0, 0, Math.PI * 2);
            ctx.fill();
        }
        
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
    
    // Draw end gate (with damage) - drawn last so it appears on top of the road
    drawEndGate();
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
    gameState.hazards = [];
    gameState.currentWave = 0;
    gameState.waveInProgress = false;
    gameState.waveIndex = 0;
    gameState.gameStarted = true;
    gameState.gameLoopRunning = true;
    gameState.currentWaveData = [];
    gameState.enemySpawnIndex = 0;
    gameState.lastEnemySpawnTime = 0;
    gameState.endGateDamage = 0;
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
