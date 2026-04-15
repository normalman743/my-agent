const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

const tileSize = 32; // 更大单元格，适配大地图
const map = [
  [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
  [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
  [1,0,1,1,1,1,1,0,1,1,1,1,1,0,1],
  [1,0,1,0,0,0,1,0,1,0,0,0,1,0,1],
  [1,0,1,0,1,0,1,1,1,0,1,0,1,0,1],
  [1,0,0,0,1,0,0,0,0,0,1,0,0,0,1],
  [1,1,1,0,1,1,1,0,1,1,1,0,1,1,1],
  [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
  [1,0,1,1,1,1,1,0,1,1,1,1,1,0,1],
  [1,0,1,0,0,0,1,0,1,0,0,0,1,0,1],
  [1,0,1,0,1,0,1,1,1,0,1,0,1,0,1],
  [1,0,0,0,1,0,0,0,0,0,1,0,0,0,1],
  [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
];

canvas.width = map[0].length * tileSize;
canvas.height = map.length * tileSize;

let pacman = {
  x: 1,
  y: 1,
  direction: 'right',
  score: 0
};

let gameRunning = false;
let gameOver = false;

// 鬼魂初始位置和状态
let ghost1 = { x: map[0].length - 2, y: map.length - 2, color: '#ff4b4b', lastMoveTime: 0 };
let ghost2 = { x: map[0].length - 2, y: map.length - 2, color: '#4b8bff', lastMoveTime: 0 };

function resetGame() {
  pacman = { x: 1, y: 1, direction: 'right', score: 0 };
  ghost1 = { x: map[0].length - 2, y: map.length - 2, color: '#ff4b4b', lastMoveTime: 0 };
  ghost2 = { x: map[0].length - 2, y: map.length - 2, color: '#4b8bff', lastMoveTime: 0 };
  for (let row = 0; row < map.length; row++) {
    for (let col = 0; col < map[row].length; col++) {
      if (map[row][col] === 2) map[row][col] = 0;
    }
  }
  ensureDotExists();
  updateScore();
  freezeItem = null;
  freezeActive = false;
  freezeEndTime = 0;
  spawnFreezeItem();
  gameRunning = true;
  gameOver = false;
}

function showStartScreen() {
  document.getElementById('start-screen').style.display = 'flex';
  document.getElementById('gameover-screen').style.display = 'none';
  document.getElementById('mode-select-screen').style.display = 'none';
}
function hideStartScreen() {
  document.getElementById('start-screen').style.display = 'none';
}
function showGameOver() {
  document.getElementById('gameover-screen').style.display = 'flex';
  document.getElementById('final-score').textContent = `最终得分：${pacman.score}`;
}
function hideGameOver() {
  document.getElementById('gameover-screen').style.display = 'none';
}
function showModeSelectScreen() {
  document.getElementById('mode-select-screen').style.display = 'flex';
  document.getElementById('start-screen').style.display = 'none';
}
function hideModeSelectScreen() {
  document.getElementById('mode-select-screen').style.display = 'none';
}

window.addEventListener('DOMContentLoaded', () => {
  document.getElementById('start-btn').onclick = () => {
    showModeSelectScreen();
  };
  document.getElementById('mobile-mode-btn').onclick = () => {
    isMobileMode = true;
    hideModeSelectScreen();
    startGameWithMode();
  };
  document.getElementById('desktop-mode-btn').onclick = () => {
    isMobileMode = false;
    hideModeSelectScreen();
    startGameWithMode();
  };
  document.getElementById('restart-btn').onclick = () => {
    resetGame();
    hideGameOver();
  };
});

function startGameWithMode() {
  resetGame();
  if (isMobileMode) {
    document.body.classList.add('mobile-mode');
    createMobileControls();
    resizeCanvas(true);
  } else {
    document.body.classList.remove('mobile-mode');
    removeMobileControls();
    resizeCanvas(false);
  }
}

function drawMap() {
  for (let row = 0; row < map.length; row++) {
    for (let col = 0; col < map[row].length; col++) {
      if (map[row][col] === 1) {
        ctx.fillStyle = 'blue';
        ctx.fillRect(col * window.tileSize, row * window.tileSize, window.tileSize, window.tileSize);
      } else if (map[row][col] === 2) {
        ctx.fillStyle = '#FFD700'; // 更亮的黄色
        ctx.beginPath();
        ctx.arc(col * window.tileSize + window.tileSize / 2, row * window.tileSize + window.tileSize / 2, window.tileSize / 3, 0, Math.PI * 2);
        ctx.fill();
      }
    }
  }
}

function drawPacman() {
  ctx.save();
  ctx.translate(pacman.x * window.tileSize + window.tileSize / 2, pacman.y * window.tileSize + window.tileSize / 2);
  let angle = 0;
  if (pacman.direction === 'up') angle = -0.5 * Math.PI;
  else if (pacman.direction === 'down') angle = 0.5 * Math.PI;
  else if (pacman.direction === 'left') angle = Math.PI;
  ctx.rotate(angle);
  ctx.fillStyle = 'yellow';
  ctx.beginPath();
  ctx.arc(0, 0, window.tileSize / 2.2, 0.2 * Math.PI, 1.8 * Math.PI);
  ctx.lineTo(0, 0);
  ctx.fill();
  ctx.restore();
}

function drawGhost(ghost) {
  ctx.save();
  ctx.translate(ghost.x * window.tileSize + window.tileSize / 2, ghost.y * window.tileSize + window.tileSize / 2);
  ctx.fillStyle = ghost.color;
  ctx.beginPath();
  ctx.arc(0, 0, window.tileSize / 2.2, Math.PI, 2 * Math.PI);
  ctx.lineTo(window.tileSize / 2.2, window.tileSize / 2.2);
  ctx.lineTo(-window.tileSize / 2.2, window.tileSize / 2.2);
  ctx.closePath();
  ctx.fill();
  // 画眼睛
  ctx.fillStyle = '#fff';
  ctx.beginPath();
  ctx.arc(-window.tileSize/6, -window.tileSize/8, window.tileSize/8, 0, 2*Math.PI);
  ctx.arc(window.tileSize/6, -window.tileSize/8, window.tileSize/8, 0, 2*Math.PI);
  ctx.fill();
  ctx.restore();
}

// 冰冻道具相关
let freezeItem = null; // {x, y}
let freezeActive = false;
let freezeEndTime = 0;
const freezeDuration = 3000; // 冻结3秒

function spawnFreezeItem() {
  let emptySpaces = [];
  for (let row = 0; row < map.length; row++) {
    for (let col = 0; col < map[row].length; col++) {
      if (map[row][col] === 0 && !(pacman.x === col && pacman.y === row)) {
        emptySpaces.push({ row, col });
      }
    }
  }
  if (emptySpaces.length > 0) {
    const randomIndex = Math.floor(Math.random() * emptySpaces.length);
    const { row, col } = emptySpaces[randomIndex];
    freezeItem = { x: col, y: row };
  }
}

function drawFreezeItem() {
  if (freezeItem) {
    ctx.save();
    ctx.fillStyle = '#00eaff';
    ctx.beginPath();
    ctx.arc(freezeItem.x * window.tileSize + window.tileSize / 2, freezeItem.y * window.tileSize + window.tileSize / 2, window.tileSize / 3, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }
}

function checkFreezeItem() {
  if (freezeItem && pacman.x === freezeItem.x && pacman.y === freezeItem.y) {
    freezeActive = true;
    freezeEndTime = performance.now() + freezeDuration;
    freezeItem = null;
  }
}

function updateFreezeStatus(timestamp) {
  if (freezeActive && timestamp > freezeEndTime) {
    freezeActive = false;
    spawnFreezeItem();
  }
}

function respawnDot() {
  let emptySpaces = [];
  for (let row = 0; row < map.length; row++) {
    for (let col = 0; col < map[row].length; col++) {
      // 只在轨道（0）且不在吃豆人当前位置刷新
      if (map[row][col] === 0 && !(pacman.x === col && pacman.y === row)) {
        emptySpaces.push({ row, col });
      }
    }
  }
  if (emptySpaces.length > 0) {
    const randomIndex = Math.floor(Math.random() * emptySpaces.length);
    const { row, col } = emptySpaces[randomIndex];
    map[row][col] = 2;
  }
}

// 游戏初始化时确保有豆子
function ensureDotExists() {
  let hasDot = false;
  for (let row = 0; row < map.length; row++) {
    for (let col = 0; col < map[row].length; col++) {
      if (map[row][col] === 2) {
        hasDot = true;
        break;
      }
    }
    if (hasDot) break;
  }
  if (!hasDot) respawnDot();
}

let lastMoveTime = 0;
const moveDelay = 120; // ms，提升移动速度
const ghostMoveDelay = moveDelay * 1.5; // 鬼比玩家慢
let lastGhostMoveTime = 0;

function updateScore() {
  const scoreDiv = document.getElementById('score');
  if (scoreDiv) scoreDiv.textContent = `Score: ${pacman.score}`;
}

function update(timestamp) {
  if (timestamp - lastMoveTime < moveDelay) {
    return;
  }
  lastMoveTime = timestamp;

  let moved = false;
  if (pacman.direction === 'up' && map[pacman.y - 1][pacman.x] !== 1) {
    pacman.y--;
    moved = true;
  } else if (pacman.direction === 'down' && map[pacman.y + 1][pacman.x] !== 1) {
    pacman.y++;
    moved = true;
  } else if (pacman.direction === 'left' && map[pacman.y][pacman.x - 1] !== 1) {
    pacman.x--;
    moved = true;
  } else if (pacman.direction === 'right' && map[pacman.y][pacman.x + 1] !== 1) {
    pacman.x++;
    moved = true;
  }

  if (moved && map[pacman.y][pacman.x] === 2) {
    pacman.score++;
    map[pacman.y][pacman.x] = 0;
    updateScore();
    respawnDot();
  }
  // 保证地图上始终有豆子
  ensureDotExists();
  checkFreezeItem();
  updateFreezeStatus(timestamp);
}

function moveGhost(ghost, timestamp, otherGhost) {
  if (freezeActive) return; // 冻结时不移动
  if (timestamp - ghost.lastMoveTime < ghostMoveDelay) {
    return;
  }
  ghost.lastMoveTime = timestamp;
  // 使用BFS找到鬼到Pac-Man的最短路径，避开另一个鬼
  const queue = [];
  const visited = Array.from({ length: map.length }, () => Array(map[0].length).fill(false));
  const prev = Array.from({ length: map.length }, () => Array(map[0].length).fill(null));
  queue.push({ x: ghost.x, y: ghost.y });
  visited[ghost.y][ghost.x] = true;
  let found = false;
  while (queue.length > 0 && !found) {
    const { x, y } = queue.shift();
    const dirs = [
      { dx: 0, dy: -1 }, // up
      { dx: 0, dy: 1 },  // down
      { dx: -1, dy: 0 }, // left
      { dx: 1, dy: 0 }   // right
    ];
    for (const { dx, dy } of dirs) {
      const nx = x + dx;
      const ny = y + dy;
      if (
        nx >= 0 && nx < map[0].length &&
        ny >= 0 && ny < map.length &&
        map[ny][nx] !== 1 &&
        !visited[ny][nx] &&
        !(otherGhost && otherGhost.x === nx && otherGhost.y === ny) // 避免走到另一个鬼魂的位置
      ) {
        queue.push({ x: nx, y: ny });
        visited[ny][nx] = true;
        prev[ny][nx] = { x, y };
        if (nx === pacman.x && ny === pacman.y) {
          found = true;
          break;
        }
      }
    }
  }
  // 回溯路径，移动一步
  let path = [];
  let cx = pacman.x, cy = pacman.y;
  while (prev[cy][cx] && (cx !== ghost.x || cy !== ghost.y)) {
    path.push({ x: cx, y: cy });
    const p = prev[cy][cx];
    cx = p.x;
    cy = p.y;
  }
  if (path.length > 0) {
    const next = path[path.length - 1];
    // 再次检查目标格是否被另一个鬼占据
    if (!(otherGhost && otherGhost.x === next.x && otherGhost.y === next.y)) {
      ghost.x = next.x;
      ghost.y = next.y;
    }
  }
}

function checkGameOver() {
  if ((pacman.x === ghost1.x && pacman.y === ghost1.y) || (pacman.x === ghost2.x && pacman.y === ghost2.y)) {
    gameRunning = false;
    gameOver = true;
    showGameOver();
  }
}

let lastUpdateTime = 0;
const frameRate = 60;

function gameLoop(timestamp) {
  if (!gameRunning) {
    requestAnimationFrame(gameLoop);
    return;
  }
  if (timestamp - lastUpdateTime < 1000 / frameRate) {
    requestAnimationFrame(gameLoop);
    return;
  }
  lastUpdateTime = timestamp;

  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawMap();
  drawPacman();
  drawGhost(ghost1);
  drawGhost(ghost2);
  drawFreezeItem();
  moveGhost(ghost1, timestamp, ghost2);
  moveGhost(ghost2, timestamp, ghost1);
  update(timestamp);
  checkGameOver();
  requestAnimationFrame(gameLoop);
}

document.addEventListener('keydown', (e) => {
  if (!gameRunning) return;
  if (e.key === 'ArrowUp') pacman.direction = 'up';
  else if (e.key === 'ArrowDown') pacman.direction = 'down';
  else if (e.key === 'ArrowLeft') pacman.direction = 'left';
  else if (e.key === 'ArrowRight') pacman.direction = 'right';
});

// 移动端虚拟按键支持
function createMobileControls() {
  if (document.getElementById('mobile-controls')) return;
  const controls = document.createElement('div');
  controls.id = 'mobile-controls';
  controls.style.position = 'fixed';
  controls.style.left = '0';
  controls.style.right = '0';
  controls.style.bottom = '2vh';
  controls.style.zIndex = '30';
  controls.style.display = 'flex';
  controls.style.flexDirection = 'column';
  controls.style.alignItems = 'center';
  controls.style.justifyContent = 'center';
  controls.innerHTML = `
    <div style="display:flex;justify-content:center;">
      <button data-dir="up" style="width:56px;height:56px;border-radius:50%;font-size:2rem;">↑</button>
    </div>
    <div style="display:flex;justify-content:center;gap:2vw;margin-top:4px;">
      <button data-dir="left" style="width:56px;height:56px;border-radius:50%;font-size:2rem;">←</button>
      <button data-dir="down" style="width:56px;height:56px;border-radius:50%;font-size:2rem;">↓</button>
      <button data-dir="right" style="width:56px;height:56px;border-radius:50%;font-size:2rem;">→</button>
    </div>
  `;
  document.body.appendChild(controls);
  controls.addEventListener('click', e => {
    if (e.target.dataset.dir) {
      pacman.direction = e.target.dataset.dir;
    }
  });
}

function removeMobileControls() {
  const controls = document.getElementById('mobile-controls');
  if (controls) controls.remove();
}

let isMobileMode = false;

// 修改resizeCanvas，mobile模式下canvas高度更大
function resizeCanvas(forceMobile) {
  let mobile = forceMobile !== undefined ? forceMobile : isMobileMode;
  const maxWidth = window.innerWidth * 0.98;
  const maxHeight = mobile ? window.innerHeight * 0.92 : window.innerHeight * 0.7;
  const tileW = Math.floor(maxWidth / map[0].length);
  const tileH = Math.floor(maxHeight / map.length);
  const newTileSize = Math.max(16, Math.min(tileW, tileH));
  canvas.width = map[0].length * newTileSize;
  canvas.height = map.length * newTileSize;
  window.tileSize = newTileSize;
}
window.addEventListener('resize', () => resizeCanvas());

updateScore();
ensureDotExists();
showStartScreen();
requestAnimationFrame(gameLoop);