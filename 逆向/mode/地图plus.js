// 🎮 地图Plus - 融合大地图改造和平衡AI的完整版本
// 复制这段代码到游戏页面控制台运行

console.log('🏗️ 启动地图Plus改造 - 大地图+平衡AI...');

(function() {
    // 检查游戏是否已加载
    if (typeof map === 'undefined') {
        console.log('❌ 游戏还未加载，请稍后重试');
        return;
    }
    
    // === 第一部分：地图改造 ===
    
    // 新的大地图 30x20
    const newMap = [
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,1,1,0,1,1,0,1,1,1,0,1,0,1,0,1,0,1,1,1,0,1,1,0,1,1,0,0,1],
        [1,0,1,0,0,0,1,0,0,0,0,0,1,0,1,0,1,0,1,0,0,0,0,0,1,0,0,0,0,1],
        [1,0,0,0,1,0,0,0,1,1,0,1,1,0,1,0,1,0,1,1,0,1,1,0,0,0,1,0,0,1],
        [1,0,1,1,1,1,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,1,1,1,0,1],
        [1,0,0,0,0,0,0,0,0,0,1,1,0,1,1,0,1,1,0,1,1,0,0,0,0,0,0,0,0,1],
        [1,1,1,0,1,1,1,0,1,0,1,0,0,0,0,0,0,0,0,0,1,0,1,0,1,1,1,0,1,1],
        [1,0,0,0,0,0,0,0,1,0,0,0,1,1,1,0,1,1,1,0,0,0,1,0,0,0,0,0,0,1],
        [1,0,1,1,0,1,1,0,0,0,1,0,1,0,1,0,1,0,1,0,1,0,0,0,1,1,0,1,0,1],
        [1,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,1],
        [1,1,1,0,1,1,1,0,1,0,0,0,1,1,1,0,1,1,1,0,0,0,1,0,1,1,1,0,1,1],
        [1,0,0,0,0,0,0,0,0,0,1,1,0,1,1,0,1,1,0,1,1,0,0,0,0,0,0,0,0,1],
        [1,0,1,1,1,1,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,1,1,1,0,1],
        [1,0,0,0,1,0,0,0,1,1,0,1,1,0,1,0,1,0,1,1,0,1,1,0,0,0,1,0,0,1],
        [1,0,1,0,0,0,1,0,0,0,0,0,1,0,1,0,1,0,1,0,0,0,0,0,1,0,0,0,0,1],
        [1,0,1,1,0,1,1,0,1,1,1,0,1,0,1,0,1,0,1,0,1,1,1,0,1,1,0,1,0,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    ];
    
    console.log('🗺️ 开始替换地图...');
    
    // 直接替换全局地图变量
    if (typeof window !== 'undefined') {
        window.map = newMap;
    }
    // 也替换局部变量（如果存在）
    if (typeof map !== 'undefined') {
        // 清空原地图，重新填充
        map.length = 0;
        newMap.forEach(row => {
            map.push([...row]);
        });
    }
    
    console.log(`✅ 地图已扩展到 ${newMap[0].length}x${newMap.length}`);
    
    // 调整画布大小
    const canvas = document.getElementById('gameCanvas');
    if (canvas) {
        const tileSize = window.tileSize || 32;
        canvas.width = newMap[0].length * tileSize;
        canvas.height = newMap.length * tileSize;
        console.log(`🖼️ 画布调整为 ${canvas.width}x${canvas.height}`);
    }
    
    // 在空地上随机放置豆子（密度约65%）
    let dotCount = 0;
    for (let y = 1; y < newMap.length - 1; y++) {
        for (let x = 1; x < newMap[0].length - 1; x++) {
            if (newMap[y][x] === 0 && Math.random() < 0.65) {
                newMap[y][x] = 2; // 2代表豆子
                if (window.map) window.map[y][x] = 2;
                if (typeof map !== 'undefined') map[y][x] = 2;
                dotCount++;
            }
        }
    }
    console.log(`🍪 已生成 ${dotCount} 个豆子`);
    
    // 重新定位游戏对象
    if (window.pacman || typeof pacman !== 'undefined') {
        const pac = window.pacman || pacman;
        pac.x = 1;
        pac.y = 1;
        console.log('🔵 吃豆人重新定位');
    }
    
    if (window.ghost1 || typeof ghost1 !== 'undefined') {
        const g1 = window.ghost1 || ghost1;
        g1.x = newMap[0].length - 2;
        g1.y = newMap.length - 2;
        console.log('👻 鬼魂1重新定位');
    }
    
    if (window.ghost2 || typeof ghost2 !== 'undefined') {
        const g2 = window.ghost2 || ghost2;
        g2.x = newMap[0].length - 3;
        g2.y = newMap.length - 2;
        console.log('👻 鬼魂2重新定位');
    }
    
    // === 第二部分：平衡AI系统 ===
    
    let aiRunning = false;
    let aiInterval;
    let lastDirection = 'right';
    let collectMode = true; // 收集模式开关
    
    // AI工具函数
    function distance(a, b) {
        return Math.abs(a.x - b.x) + Math.abs(a.y - b.y);
    }
    
    function isValidMove(x, y) {
        const currentMap = window.map || map;
        return x >= 0 && y >= 0 && x < currentMap[0].length && y < currentMap.length && currentMap[y][x] !== 1;
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
        const currentMap = window.map || map;
        
        for (let y = 0; y < currentMap.length; y++) {
            for (let x = 0; x < currentMap[0].length; x++) {
                if (currentMap[y][x] === 2) {
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
    
    function getGameObjects() {
        return {
            pacman: window.pacman || (typeof pacman !== 'undefined' ? pacman : null),
            ghost1: window.ghost1 || (typeof ghost1 !== 'undefined' ? ghost1 : null),
            ghost2: window.ghost2 || (typeof ghost2 !== 'undefined' ? ghost2 : null),
            map: window.map || (typeof map !== 'undefined' ? map : null),
            gameRunning: window.gameRunning || (typeof gameRunning !== 'undefined' ? gameRunning : false),
            gameOver: window.gameOver || (typeof gameOver !== 'undefined' ? gameOver : false)
        };
    }
    
    function findBestMove() {
        const game = getGameObjects();
        if (!game.gameRunning || !game.pacman || !game.ghost1 || !game.ghost2) return null;
        
        const pos = {x: game.pacman.x, y: game.pacman.y};
        const ghosts = [game.ghost1, game.ghost2];
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
            score += minDist * 25; // 距离鬼魂越远越好
            
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
                score -= 200;
            }
            
            // 5. 收集奖励（关键改进！）
            if (collectMode || minDist >= 3) {
                const currentMap = game.map;
                // 直接豆子奖励
                if (currentMap[nextPos.y][nextPos.x] === 2) {
                    score += 250; // 大幅提高豆子奖励
                    console.log(`🍪 ${move.name}: 发现豆子！+250分`);
                }
                
                // 冰冻道具奖励（如果存在）
                if (window.freezeItem && nextPos.x === window.freezeItem.x && nextPos.y === window.freezeItem.y) {
                    score += 400;
                    console.log(`❄️ ${move.name}: 冰冻道具！+400分`);
                }
                
                // 寻找最近豆子的方向奖励
                const nearestDot = findNearestDot(nextPos);
                if (nearestDot) {
                    const currentDotDist = distance(pos, nearestDot);
                    const newDotDist = nearestDot.distance;
                    
                    if (newDotDist < currentDotDist) {
                        score += 60; // 靠近豆子奖励
                        console.log(`➡️ ${move.name}: 靠近豆子 +60分`);
                    }
                }
            }
            
            // 6. 避免摆动
            if (move.name === lastDirection) {
                score += 40;
            }
            
            // 7. 随机性避免卡住
            score += Math.random() * 30;
            
            console.log(`📋 ${move.name}: ${score.toFixed(1)}分 (距离:${minDist}, 豆子:${game.map[nextPos.y][nextPos.x]===2?'✓':'✗'})`);
            
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
    
    // 自动开始游戏
    function autoStartGame() {
        const game = getGameObjects();
        
        if (!game.gameRunning) {
            // 尝试启动游戏
            const startBtn = document.getElementById('start-btn');
            const mobileBtn = document.getElementById('mobile-mode-btn');
            
            if (startBtn && window.getComputedStyle(startBtn).display !== 'none') {
                console.log('🎮 点击开始按钮');
                startBtn.click();
            } else if (mobileBtn && window.getComputedStyle(mobileBtn).display !== 'none') {
                console.log('🎮 选择手机模式');
                mobileBtn.click();
            } else if (window.startGame && typeof window.startGame === 'function') {
                console.log('🎮 AI自动开始游戏');
                window.startGame();
            }
        }
    }
    
    function startPlusAI() {
        if (aiRunning) {
            console.log('Plus AI已在运行');
            return;
        }
        
        aiRunning = true;
        collectMode = true;
        console.log('🍪 Plus AI启动！大地图+平衡AI');
        
        aiInterval = setInterval(() => {
            const game = getGameObjects();
            
            // 自动开始游戏
            if (!game.gameRunning) {
                autoStartGame();
                return;
            }
            
            // 游戏结束处理
            if (game.gameOver) {
                console.log(`💀 游戏结束！最终分数: ${game.pacman ? game.pacman.score : 'N/A'}`);
                setTimeout(() => {
                    const restartBtn = document.getElementById('restart-btn');
                    if (restartBtn && window.getComputedStyle(restartBtn).display !== 'none') {
                        restartBtn.click();
                    }
                }, 1500);
                return;
            }
            
            const bestMove = findBestMove();
            if (bestMove && game.pacman && game.pacman.direction !== bestMove) {
                game.pacman.direction = bestMove;
                console.log(`🎮 移动: ${bestMove} | 分数: ${game.pacman.score} | ${collectMode ? '🍪收集中' : '🚨逃生中'}`);
            }
        }, 120); // 稍微调慢一点，让游戏更稳定
    }
    
    function stopPlusAI() {
        if (aiInterval) {
            clearInterval(aiInterval);
            aiRunning = false;
            console.log('⏹️ Plus AI已停止');
        }
    }
    
    // 削弱鬼魂（降低移动频率）
    if (!window._ghostsWeakenedPlus) {
        const originalMoveGhost = window.moveGhost;
        if (originalMoveGhost) {
            window.moveGhost = function(ghost, timestamp, otherGhost) {
                // 只有45%的概率移动鬼魂（比原版稍微提高一点点难度）
                if (Math.random() < 0.45) {
                    return originalMoveGhost.call(this, ghost, timestamp, otherGhost);
                }
            };
            window._ghostsWeakenedPlus = true;
            console.log('👻 鬼魂移动频率已降低到45%');
        }
    }
    
    // === 全局控制函数 ===
    
    window.startMapPlusAI = startPlusAI;
    window.stopMapPlusAI = stopPlusAI;
    
    window.togglePlusCollectMode = () => {
        collectMode = !collectMode;
        console.log(`🔄 收集模式: ${collectMode ? '开启' : '关闭'}`);
    };
    
    // 状态查看
    window.showMapPlusStatus = () => {
        const game = getGameObjects();
        console.log('🏗️ 地图Plus状态:');
        console.log(`AI运行中: ${aiRunning}`);
        console.log(`收集模式: ${collectMode}`);
        console.log(`游戏运行中: ${game.gameRunning}`);
        console.log(`当前分数: ${game.pacman ? game.pacman.score : 'N/A'}`);
        
        if (game.pacman && game.ghost1 && game.ghost2) {
            const pos = {x: game.pacman.x, y: game.pacman.y};
            const ghosts = [game.ghost1, game.ghost2];
            const minDist = Math.min(...ghosts.map(g => distance(pos, g)));
            console.log(`与鬼魂最近距离: ${minDist}`);
            
            // 计算地图上剩余豆子数量
            let dotsLeft = 0;
            const currentMap = game.map;
            for (let y = 0; y < currentMap.length; y++) {
                for (let x = 0; x < currentMap[0].length; x++) {
                    if (currentMap[y][x] === 2) dotsLeft++;
                }
            }
            console.log(`剩余豆子: ${dotsLeft} 个`);
        }
    };
    
    // 等待游戏加载后自动启动
    function waitAndStart() {
        const game = getGameObjects();
        if (game.pacman && typeof game.gameRunning !== 'undefined') {
            startPlusAI();
        } else {
            console.log('⏳ 等待游戏加载...');
            setTimeout(waitAndStart, 1000);
        }
    }
    
    // 立即重启游戏应用新地图
    setTimeout(() => {
        if (window.resetGame && typeof window.resetGame === 'function') {
            console.log('🔄 重新开始游戏以应用新地图');
            window.resetGame();
        }
        // 延迟启动AI，确保地图加载完成
        setTimeout(waitAndStart, 500);
    }, 1000);
    
    console.log('🎉 地图Plus改造完成！');
    console.log(`📏 新地图尺寸: ${newMap[0].length}x${newMap.length}`);
    console.log(`🍪 豆子数量: ${dotCount}`);
    console.log('🤖 平衡AI已准备就绪');
    console.log('');
    console.log('💡 控制命令:');
    console.log('• stopMapPlusAI() - 停止AI');
    console.log('• startMapPlusAI() - 重启AI');  
    console.log('• togglePlusCollectMode() - 切换收集模式');
    console.log('• showMapPlusStatus() - 查看状态');

})();
