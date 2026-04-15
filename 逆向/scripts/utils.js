function getRandomInt(min, max) {
    return Math.floor(Math.random() * (max - min)) + min;
}

function initializeGame(map) {
    // Initialize game state based on the provided map
    const gameState = {
        score: 0,
        pacmanPosition: { x: 1, y: 1 },
        ghosts: [],
        dots: [],
        isGameOver: false,
    };

    // Populate dots and ghosts based on the map
    for (let y = 0; y < map.length; y++) {
        for (let x = 0; x < map[y].length; x++) {
            if (map[y][x] === 2) {
                gameState.dots.push({ x, y });
            }
        }
    }

    return gameState;
}

function renderGame(gameState, context) {
    // Clear the canvas
    context.clearRect(0, 0, context.canvas.width, context.canvas.height);

    // Render Pac-Man
    context.fillStyle = 'yellow';
    context.beginPath();
    context.arc(gameState.pacmanPosition.x * 20 + 10, gameState.pacmanPosition.y * 20 + 10, 10, 0.2 * Math.PI, 1.8 * Math.PI);
    context.lineTo(gameState.pacmanPosition.x * 20 + 10, gameState.pacmanPosition.y * 20 + 10);
    context.fill();

    // Render dots
    context.fillStyle = 'white';
    gameState.dots.forEach(dot => {
        context.beginPath();
        context.arc(dot.x * 20 + 10, dot.y * 20 + 10, 5, 0, 2 * Math.PI);
        context.fill();
    });

    // Render ghosts (placeholder)
    context.fillStyle = 'red';
    gameState.ghosts.forEach(ghost => {
        context.fillRect(ghost.x * 20, ghost.y * 20, 20, 20);
    });
}