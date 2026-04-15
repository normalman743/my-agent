// AI玩家 - 自动控制吃豆人生存并获得高分
class PacmanAI {
    constructor() {
        this.lastDecision = null;
        this.decisionCooldown = 0;
        this.survivalMode = false;
        this.targetDot = null;
        this.escapeRoute = null;
        this.priorities = {
            survival: 10,    // 生存优先级最高
            dots: 5,        // 收集豆子
            freezeItem: 8,  // 冰冻道具很重要
            exploration: 1  // 探索
        };
    }

    // 计算两点之间的曼哈顿距离
    manhattanDistance(pos1, pos2) {
        return Math.abs(pos1.x - pos2.x) + Math.abs(pos1.y - pos2.y);
    }

    // 使用BFS寻找最短路径
    findPath(start, end, avoidPositions = []) {
        const queue = [{...start, path: []}];
        const visited = new Set();
        visited.add(`${start.x},${start.y}`);

        while (queue.length > 0) {
            const current = queue.shift();
            
            if (current.x === end.x && current.y === end.y) {
                return current.path;
            }

            const directions = [
                {x: 0, y: -1, dir: 'up'},
                {x: 0, y: 1, dir: 'down'},
                {x: -1, y: 0, dir: 'left'},
                {x: 1, y: 0, dir: 'right'}
            ];

            for (const dir of directions) {
                const newX = current.x + dir.x;
                const newY = current.y + dir.y;
                const key = `${newX},${newY}`;

                // 检查边界和墙壁
                if (newX < 0 || newX >= map[0].length || 
                    newY < 0 || newY >= map.length || 
                    map[newY][newX] === 1 || 
                    visited.has(key)) {
                    continue;
                }

                // 避开危险位置
                const isDangerous = avoidPositions.some(pos => 
                    pos.x === newX && pos.y === newY
                );
                if (isDangerous) continue;

                visited.add(key);
                queue.push({
                    x: newX,
                    y: newY,
                    path: [...current.path, dir.dir]
                });
            }
        }
        return [];
    }

    // 评估位置的安全性
    evaluateSafety(position, ghosts) {
        let safetyScore = 100;
        
        for (const ghost of ghosts) {
            const distance = this.manhattanDistance(position, ghost);
            if (distance <= 2) {
                safetyScore -= (3 - distance) * 30; // 距离越近越危险
            }
        }

        // 检查是否在死胡同
        const exits = this.getValidMoves(position).length;
        if (exits <= 1) {
            safetyScore -= 20; // 死胡同很危险
        }

        return safetyScore;
    }

    // 获取有效移动方向
    getValidMoves(position) {
        const moves = [];
        const directions = [
            {x: 0, y: -1, dir: 'up'},
            {x: 0, y: 1, dir: 'down'},
            {x: -1, y: 0, dir: 'left'},
            {x: 1, y: 0, dir: 'right'}
        ];

        for (const dir of directions) {
            const newX = position.x + dir.x;
            const newY = position.y + dir.y;
            
            if (newX >= 0 && newX < map[0].length && 
                newY >= 0 && newY < map.length && 
                map[newY][newX] !== 1) {
                moves.push(dir);
            }
        }
        return moves;
    }

    // 寻找最近的豆子
    findNearestDot(pacmanPos) {
        let nearest = null;
        let minDistance = Infinity;

        for (let y = 0; y < map.length; y++) {
            for (let x = 0; x < map[y].length; x++) {
                if (map[y][x] === 2) {
                    const distance = this.manhattanDistance(pacmanPos, {x, y});
                    if (distance < minDistance) {
                        minDistance = distance;
                        nearest = {x, y};
                    }
                }
            }
        }
        return nearest;
    }

    // 预测鬼魂下一步位置
    predictGhostMovement(ghost, pacmanPos, otherGhost) {
        // 简化的鬼魂行为预测 - 假设它们会朝玩家移动
        const path = this.findPath(ghost, pacmanPos, otherGhost ? [otherGhost] : []);
        if (path.length > 0) {
            const direction = path[0];
            const nextPos = {...ghost};
            
            switch(direction) {
                case 'up': nextPos.y--; break;
                case 'down': nextPos.y++; break;
                case 'left': nextPos.x--; break;
                case 'right': nextPos.x++; break;
            }
            return nextPos;
        }
        return ghost;
    }

    // 主要AI决策函数
    makeDecision(gameState) {
        const pacmanPos = {x: gameState.pacman.x, y: gameState.pacman.y};
        const ghosts = [gameState.ghost1, gameState.ghost2];
        
        // 如果游戏结束或未开始，不做决策
        if (!gameState.gameRunning) {
            return null;
        }

        // 减少决策频率，避免过于频繁的方向改变
        if (this.decisionCooldown > 0) {
            this.decisionCooldown--;
            return this.lastDecision;
        }

        // 预测鬼魂下一步位置
        const predictedGhosts = ghosts.map((ghost, index) => 
            this.predictGhostMovement(ghost, pacmanPos, ghosts[1-index])
        );

        // 计算与鬼魂的最小距离
        const minGhostDistance = Math.min(...ghosts.map(ghost => 
            this.manhattanDistance(pacmanPos, ghost)
        ));

        // 判断是否进入生存模式
        this.survivalMode = minGhostDistance <= 3 || this.survivalMode && minGhostDistance <= 5;

        let bestMove = null;
        let bestScore = -Infinity;

        const validMoves = this.getValidMoves(pacmanPos);

        for (const move of validMoves) {
            const nextPos = {
                x: pacmanPos.x + (move.dir === 'left' ? -1 : move.dir === 'right' ? 1 : 0),
                y: pacmanPos.y + (move.dir === 'up' ? -1 : move.dir === 'down' ? 1 : 0)
            };

            let score = 0;

            // 安全性评估
            const safety = this.evaluateSafety(nextPos, predictedGhosts);
            score += safety * this.priorities.survival;

            // 如果不安全，大幅降低分数
            if (safety < 50) {
                score -= 1000;
            }

            // 在生存模式下，优先考虑安全
            if (this.survivalMode) {
                score += safety * 2;
                
                // 尝试远离鬼魂
                const avgGhostDistance = ghosts.reduce((sum, ghost) => 
                    sum + this.manhattanDistance(nextPos, ghost), 0) / ghosts.length;
                score += avgGhostDistance * 10;
            } else {
                // 非生存模式下，考虑收集豆子
                if (map[nextPos.y][nextPos.x] === 2) {
                    score += 50 * this.priorities.dots; // 直接吃到豆子
                }

                // 寻找最近的豆子
                const nearestDot = this.findNearestDot(nextPos);
                if (nearestDot) {
                    const dotDistance = this.manhattanDistance(nextPos, nearestDot);
                    score += (20 - dotDistance) * this.priorities.dots;
                }

                // 冰冻道具优先级
                if (gameState.freezeItem) {
                    const freezeDistance = this.manhattanDistance(nextPos, gameState.freezeItem);
                    if (freezeDistance <= 3) {
                        score += (10 - freezeDistance) * this.priorities.freezeItem;
                    }
                }
            }

            // 避免反复移动
            if (this.lastDecision && this.getOppositeDirection(move.dir) === this.lastDecision) {
                score -= 20;
            }

            // 选择最优移动
            if (score > bestScore) {
                bestScore = score;
                bestMove = move.dir;
            }
        }

        this.lastDecision = bestMove;
        this.decisionCooldown = 2; // 设置冷却时间

        return bestMove;
    }

    // 获取相反方向
    getOppositeDirection(direction) {
        const opposites = {
            'up': 'down',
            'down': 'up',
            'left': 'right',
            'right': 'left'
        };
        return opposites[direction];
    }

    // 重置AI状态
    reset() {
        this.lastDecision = null;
        this.decisionCooldown = 0;
        this.survivalMode = false;
        this.targetDot = null;
        this.escapeRoute = null;
    }
}

// 创建AI实例
const pacmanAI = new PacmanAI();

// AI自动控制函数
function enableAI() {
    if (typeof gameRunning === 'undefined') {
        console.log('游戏尚未加载完成，请稍后再试');
        return;
    }

    // 创建AI控制间隔
    const aiInterval = setInterval(() => {
        if (!gameRunning || gameOver) {
            // 如果游戏结束，尝试重新开始
            if (gameOver) {
                console.log('AI检测到游戏结束，准备重新开始...');
                setTimeout(() => {
                    const restartBtn = document.getElementById('restart-btn');
                    if (restartBtn) {
                        restartBtn.click();
                        pacmanAI.reset();
                    }
                }, 1000);
            }
            return;
        }

        // 构建游戏状态
        const gameState = {
            pacman: pacman,
            ghost1: ghost1,
            ghost2: ghost2,
            gameRunning: gameRunning,
            freezeItem: freezeItem,
            freezeActive: freezeActive
        };

        // 获取AI决策
        const decision = pacmanAI.makeDecision(gameState);
        
        // 执行AI决策
        if (decision && decision !== pacman.direction) {
            pacman.direction = decision;
            console.log(`AI决策: ${decision}, 当前分数: ${pacman.score}, 生存模式: ${pacmanAI.survivalMode}`);
        }
    }, 100); // 每100ms做一次决策

    console.log('🤖 AI已启动！吃豆人现在由AI控制');
    console.log('🎯 目标：尽可能长时间存活并获得高分');
    
    return aiInterval;
}

// 手动控制恢复函数
function disableAI(aiInterval) {
    if (aiInterval) {
        clearInterval(aiInterval);
        console.log('🎮 AI已停止，恢复手动控制');
    }
}

// 导出函数供外部使用
window.enableAI = enableAI;
window.disableAI = disableAI;
window.pacmanAI = pacmanAI;
