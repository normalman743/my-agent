// 🎮 正确的大地图改造脚本
// 复制这段代码到游戏页面控制台运行

console.log('🏗️ 开始地图改造...');

(function() {
    // 检查游戏是否已加载
    if (typeof map === 'undefined') {
        console.log('❌ 游戏还未加载，请稍后重试');
        return;
    }
    
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
    
    // 在空地上随机放置豆子（密度约60%）
    let dotCount = 0;
    for (let y = 1; y < newMap.length - 1; y++) {
        for (let x = 1; x < newMap[0].length - 1; x++) {
            if (newMap[y][x] === 0 && Math.random() < 0.6) {
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
    
    // 增强AI代码
    let aiActive = true;
    let lastDirection = 'right';
    
    function getGameObjects() {
        return {
            pacman: window.pacman || (typeof pacman !== 'undefined' ? pacman : null),
            ghost1: window.ghost1 || (typeof ghost1 !== 'undefined' ? ghost1 : null),
            ghost2: window.ghost2 || (typeof ghost2 !== 'undefined' ? ghost2 : null),
            map: window.map || (typeof map !== 'undefined' ? map : null)
        };
    }
    
    function calculateDistance(obj1, obj2) {
        if (!obj1 || !obj2) return 999;
        return Math.abs(obj1.x - obj2.x) + Math.abs(obj1.y - obj2.y);
    }
    
    function isValidPosition(x, y, gameMap) {
        if (!gameMap || x < 0 || y < 0 || y >= gameMap.length || x >= gameMap[0].length) {
            return false;
        }
        return gameMap[y][x] !== 1; // 1是墙壁
    }
    
    function makeSmartMove() {
        if (!aiActive) return;
        
        const game = getGameObjects();
        if (!game.pacman || !game.map) return;
        
        const pac = game.pacman;
        const currentMap = game.map;
        
        // 所有可能的移动方向
        const directions = [
            { name: 'right', x: pac.x + 1, y: pac.y },
            { name: 'left', x: pac.x - 1, y: pac.y },
            { name: 'down', x: pac.x, y: pac.y + 1 },
            { name: 'up', x: pac.x, y: pac.y - 1 }
        ];
        
        // 过滤出有效移动
        const validMoves = directions.filter(dir => 
            isValidPosition(dir.x, dir.y, currentMap)
        );
        
        if (validMoves.length === 0) return;
        
        let bestMove = validMoves[0];
        let bestScore = -Infinity;
        
        for (const move of validMoves) {
            let score = 0;
            
            // 计算与鬼魂的距离
            const dist1 = calculateDistance(move, game.ghost1);
            const dist2 = calculateDistance(move, game.ghost2);
            const minGhostDist = Math.min(dist1, dist2);
            
            // 安全性评分
            if (minGhostDist <= 1) {
                score = -10000; // 避免直接撞到鬼魂
            } else if (minGhostDist <= 3) {
                score = -1000 + minGhostDist * 100; // 距离太近很危险
            } else {
                score = minGhostDist * 50; // 距离越远越安全
                
                // 豆子奖励
                if (currentMap[move.y] && currentMap[move.y][move.x] === 2) {
                    score += 300;
                }
                
                // 倾向于继续当前方向，减少摆动
                if (move.name === lastDirection) {
                    score += 100;
                }
                
                // 避免死胡同（简单检测）
                const nextMoves = directions
                    .map(d => ({ x: move.x + (d.x - pac.x), y: move.y + (d.y - pac.y) }))
                    .filter(pos => isValidPosition(pos.x, pos.y, currentMap));
                
                if (nextMoves.length === 1) {
                    score -= 200; // 可能是死胡同
                }
                
                // 添加随机性避免卡住
                score += Math.random() * 50;
            }
            
            if (score > bestScore) {
                bestScore = score;
                bestMove = move;
            }
        }
        
        // 执行最佳移动
        if (bestMove) {
            pac.direction = bestMove.name;
            lastDirection = bestMove.name;
            console.log(`🤖 AI选择: ${bestMove.name} (评分: ${Math.round(bestScore)})`);
        }
    }
    
    // 自动开始游戏
    function autoStartGame() {
        // 检查游戏状态
        const isRunning = window.gameRunning || (typeof gameRunning !== 'undefined' ? gameRunning : false);
        
        if (!isRunning) {
            // 尝试启动游戏
            if (window.startGame && typeof window.startGame === 'function') {
                console.log('🎮 AI自动开始游戏');
                window.startGame();
            } else if (typeof startGameWithMode === 'function') {
                console.log('🎮 AI使用模式开始游戏');
                startGameWithMode();
            }
        }
        
        // 如果在模式选择界面，选择手机模式
        if (window.selectMode && typeof window.selectMode === 'function') {
            window.selectMode('mobile');
        }
    }
    
    // 削弱鬼魂（降低移动频率）
    if (!window._ghostsWeakened) {
        const originalMoveGhost = window.moveGhost;
        if (originalMoveGhost) {
            window.moveGhost = function(ghost, timestamp, otherGhost) {
                // 只有40%的概率移动鬼魂
                if (Math.random() < 0.4) {
                    return originalMoveGhost.call(this, ghost, timestamp, otherGhost);
                }
            };
            window._ghostsWeakened = true;
            console.log('👻 鬼魂移动频率已降低到40%');
        }
    }
    
    // 启动AI主循环
    console.log('🤖 启动增强AI...');
    const aiInterval = setInterval(() => {
        if (!aiActive) return;
        
        try {
            autoStartGame();
            makeSmartMove();
        } catch (error) {
            console.warn('⚠️ AI遇到错误:', error.message);
        }
    }, 100);
    
    // 全局控制函数
    window.stopBigMapAI = function() {
        aiActive = false;
        clearInterval(aiInterval);
        console.log('⏹️ 大地图AI已停止');
    };
    
    window.startBigMapAI = function() {
        if (!aiActive) {
            aiActive = true;
            setInterval(() => {
                if (!aiActive) return;
                try {
                    autoStartGame();
                    makeSmartMove();
                } catch (error) {
                    console.warn('⚠️ AI遇到错误:', error.message);
                }
            }, 100);
            console.log('▶️ 大地图AI已重启');
            
        }
    };
    
    // 立即重启游戏应用新地图
    setTimeout(() => {
        if (window.resetGame && typeof window.resetGame === 'function') {
            console.log('🔄 重新开始游戏以应用新地图');
            window.resetGame();
        }
    }, 1000);
    
    console.log('🎉 大地图改造完成！');
    console.log(`📏 新地图尺寸: ${newMap[0].length}x${newMap.length}`);
    console.log(`🍪 豆子数量: ${dotCount}`);
    console.log('🤖 增强AI已启动');
    console.log('💡 输入 stopBigMapAI() 停止AI');
    console.log('💡 输入 startBigMapAI() 重启AI');
    stopBigMapAI()
})();
