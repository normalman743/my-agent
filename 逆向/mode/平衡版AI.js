// 🍪 平衡版AI - 既安全又会吃豆子
console.log('🍪 启动平衡版AI - 会吃豆子的智能AI...');

(function() {
    let aiRunning = false;
    let aiInterval;
    let lastDirection = 'right';
    let collectMode = true; // 收集模式开关
    
    function distance(a, b) {
        return Math.abs(a.x - b.x) + Math.abs(a.y - b.y);
    }
    
    function isValidMove(x, y) {
        return x >= 0 && y >= 0 && x < map[0].length && y < map.length && map[y][x] !== 1;
    }
    
    function getValidMoves(pos) {
        const moves = [];
        const dirs = [
            {x: 0, y: -1, name: 'up'},
            {x: 0, y: 1, name: 'down'},
            {x: -1, y: 0, name: 'left'},
            {x: 1, y: 0, name: 'right'}
        ];
        
        for (let dir of dirs) {
            if (isValidMove(pos.x + dir.x, pos.y + dir.y)) {
                moves.push({...dir, newX: pos.x + dir.x, newY: pos.y + dir.y});
            }
        }
        return moves;
    }
    
    // 简化的死胡同检测
    function isDeadEnd(pos, depth = 3) {
        const queue = [{pos, depth: 0}];
        const visited = new Set();
        let exitCount = 0;
        
        while (queue.length > 0) {
            const {pos: currentPos, depth: currentDepth} = queue.shift();
            const key = `${currentPos.x},${currentPos.y}`;
            
            if (visited.has(key) || currentDepth > depth) continue;
            visited.add(key);
            
            const moves = getValidMoves(currentPos);
            if (moves.length > 2) exitCount++;
            
            for (let move of moves) {
                queue.push({
                    pos: {x: move.newX, y: move.newY},
                    depth: currentDepth + 1
                });
            }
        }
        
        return exitCount < 2; // 如果出口太少就是死胡同
    }
    
    // 包夹检测（简化版）
    function isPincerAttack(pos, ghosts) {
        if (ghosts.length < 2) return false;
        
        const [g1, g2] = ghosts;
        const d1 = distance(pos, g1);
        const d2 = distance(pos, g2);
        
        // 只有鬼魂都很近时才考虑包夹
        if (d1 > 4 || d2 > 4) return false;
        
        const angle1 = Math.atan2(g1.y - pos.y, g1.x - pos.x);
        const angle2 = Math.atan2(g2.y - pos.y, g2.x - pos.x);
        let angleDiff = Math.abs(angle1 - angle2);
        
        if (angleDiff > Math.PI) {
            angleDiff = 2 * Math.PI - angleDiff;
        }
        
        return angleDiff > Math.PI * 0.5 && angleDiff < Math.PI * 1.5;
    }
    
    // 寻找最近的豆子
    function findNearestDot(pos) {
        let nearestDot = null;
        let minDistance = Infinity;
        
        for (let y = 0; y < map.length; y++) {
            for (let x = 0; x < map[0].length; x++) {
                if (map[y][x] === 2) {
                    const dist = distance(pos, {x, y});
                    if (dist < minDistance) {
                        minDistance = dist;
                        nearestDot = {x, y, distance: dist};
                    }
                }
            }
        }
        
        return nearestDot;
    }
    
    function findBestMove() {
        if (!gameRunning || !pacman || !ghost1 || !ghost2) return null;
        
        const pos = {x: pacman.x, y: pacman.y};
        const ghosts = [ghost1, ghost2];
        const moves = getValidMoves(pos);
        
        if (moves.length === 0) return null;
        
        const minGhostDist = Math.min(...ghosts.map(g => distance(pos, g)));
        const isInDanger = minGhostDist <= 2;
        const isPincer = isPincerAttack(pos, ghosts);
        
        // 动态切换模式
        if (isInDanger || isPincer) {
            collectMode = false;
            console.log('🚨 切换到逃生模式');
        } else if (minGhostDist >= 4) {
            collectMode = true;
            console.log('🍪 切换到收集模式');
        }
        
        let bestMove = null;
        let bestScore = -Infinity;
        
        console.log(`📊 分析 ${moves.length} 个移动选项 | 模式: ${collectMode ? '收集' : '逃生'}`);
        
        for (let move of moves) {
            const nextPos = {x: move.newX, y: move.newY};
            let score = 0;
            
            // 1. 基础安全检查
            const ghostDistances = ghosts.map(g => distance(nextPos, g));
            const minDist = Math.min(...ghostDistances);
            
            if (minDist <= 1) {
                console.log(`❌ ${move.name}: 会撞鬼`);
                continue; // 直接跳过会撞鬼的移动
            }
            
            // 2. 安全性评分
            score += minDist * 100; // 距离鬼魂越远越好
            
            // 3. 死胡同惩罚（但不是致命的）
            if (isDeadEnd(nextPos)) {
                if (collectMode && minDist >= 3) {
                    score -= 100; // 收集模式下轻微惩罚
                } else {
                    score -= 300; // 逃生模式下重度惩罚
                }
            }
            
            // 4. 包夹惩罚
            if (isPincerAttack(nextPos, ghosts)) {
                score -= 1000;
            }
            
            // 5. 收集奖励（关键改进！）
            if (collectMode || minDist >= 3) {
                // 直接豆子奖励
                if (map[nextPos.y][nextPos.x] === 2) {
                    score += 400; // 大幅提高豆子奖励
                    console.log(`🍪 ${move.name}: 发现豆子！+200分`);
                }
                
                // 冰冻道具奖励
                if (freezeItem && nextPos.x === freezeItem.x && nextPos.y === freezeItem.y) {
                    score += 400;
                    console.log(`❄️ ${move.name}: 冰冻道具！+400分`);
                }
                
                // 寻找最近豆子的方向奖励
                const nearestDot = findNearestDot(nextPos);
                if (nearestDot) {
                    const currentDotDist = distance(pos, nearestDot);
                    const newDotDist = nearestDot.distance;
                    
                    if (newDotDist < currentDotDist) {
                        score += 70; // 靠近豆子奖励
                        console.log(`➡️ ${move.name}: 靠近豆子 +50分`);
                    }
                }
            }
            
            // 6. 避免摆动
            if (move.name === lastDirection) {
                score += 30;
            }
            
            // 7. 随机性避免卡住
            score += Math.random() * 20;
            
            console.log(`📋 ${move.name}: ${score.toFixed(1)}分 (距离:${minDist}, 豆子:${map[nextPos.y][nextPos.x]===2?'✓':'✗'})`);
            
            if (score > bestScore) {
                bestScore = score;
                bestMove = move;
            }
        }
        
        if (bestMove) {
            lastDirection = bestMove.name;
            console.log(`✅ 选择: ${bestMove.name} | 得分: ${bestScore.toFixed(1)} | 模式: ${collectMode ? '🍪收集' : '🚨逃生'}`);
        }
        
        return bestMove ? bestMove.name : moves[0].name;
    }
    
    function startAI() {
        if (aiRunning) {
            console.log('平衡AI已在运行');
            return;
        }
        
        aiRunning = true;
        collectMode = true;
        console.log('🍪 平衡版AI启动！既安全又会吃豆子');
        
        aiInterval = setInterval(() => {
            // 自动开始游戏
            if (!gameRunning) {
                const startBtn = document.getElementById('start-btn');
                const mobileBtn = document.getElementById('mobile-mode-btn');
                
                if (startBtn && window.getComputedStyle(startBtn).display !== 'none') {
                    startBtn.click();
                } else if (mobileBtn && window.getComputedStyle(mobileBtn).display !== 'none') {
                    mobileBtn.click();
                }
                return;
            }
            
            // 游戏结束处理
            if (gameOver) {
                console.log(`💀 游戏结束！最终分数: ${pacman.score}`);
                setTimeout(() => {
                    const restartBtn = document.getElementById('restart-btn');
                    if (restartBtn && window.getComputedStyle(restartBtn).display !== 'none') {
                        restartBtn.click();
                    }
                }, 1500);
                return;
            }
            
            const bestMove = findBestMove();
            if (bestMove && pacman.direction !== bestMove) {
                pacman.direction = bestMove;
                console.log(`🎮 移动: ${bestMove} | 分数: ${pacman.score} | ${collectMode ? '🍪收集中' : '🚨逃生中'}`);
            }
        }, 100); // 快速反应
    }
    
    function stopAI() {
        if (aiInterval) {
            clearInterval(aiInterval);
            aiRunning = false;
            console.log('⏹️ 平衡AI已停止');
        }
    }
    
    // 全局控制函数
    window.startBalancedAI = startAI;
    window.stopBalancedAI = stopAI;
    window.toggleCollectMode = () => {
        collectMode = !collectMode;
        console.log(`🔄 收集模式: ${collectMode ? '开启' : '关闭'}`);
    };
    
    // 状态查看
    window.showBalancedAIStatus = () => {
        console.log('🍪 平衡AI状态:');
        console.log(`运行中: ${aiRunning}`);
        console.log(`收集模式: ${collectMode}`);
        console.log(`当前分数: ${pacman ? pacman.score : 'N/A'}`);
        
        if (pacman && ghost1 && ghost2) {
            const pos = {x: pacman.x, y: pacman.y};
            const ghosts = [ghost1, ghost2];
            const minDist = Math.min(...ghosts.map(g => distance(pos, g)));
            console.log(`与鬼魂最近距离: ${minDist}`);
            
            // 计算地图上剩余豆子数量
            let dotsLeft = 0;
            for (let y = 0; y < map.length; y++) {
                for (let x = 0; x < map[0].length; x++) {
                    if (map[y][x] === 2) dotsLeft++;
                }
            }
            console.log(`剩余豆子: ${dotsLeft} 个`);
        }
    };
    
    function waitAndStart() {
        if (typeof gameRunning !== 'undefined' && typeof pacman !== 'undefined') {
            startAI();
        } else {
            console.log('⏳ 等待游戏加载...');
            setTimeout(waitAndStart, 1000);
        }
    }
    
    waitAndStart();
})();

console.log('✅ 平衡版AI加载完成！');
console.log('🍪 特点: 既会逃生又会积极吃豆子');
console.log('💡 控制命令:');
console.log('• stopBalancedAI() - 停止AI');
console.log('• startBalancedAI() - 重启AI');  
console.log('• toggleCollectMode() - 切换收集模式');
console.log('• showBalancedAIStatus() - 查看状态');
