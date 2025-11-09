/**
 * Görsel Oturum Düzenleme Canvas Editörü
 * Drag & drop, sahne konumu, zoom özellikleri ile
 */

class VisualSeatingEditor {
    constructor(containerId, config = {}) {
        this.container = document.getElementById(containerId);
        this.config = {
            width: config.width || 800,
            height: config.height || 600,
            gridSize: config.gridSize || 20,
            stagePosition: config.stagePosition || 'top', // top, bottom, left, right
            ...config
        };
        
        this.canvas = null;
        this.ctx = null;
        this.stage = null;
        this.seatings = [];
        this.selectedSeating = null;
        this.isDragging = false;
        this.dragOffset = { x: 0, y: 0 };
        this.zoom = 1;
        this.pan = { x: 0, y: 0 };
        
        // Undo/Redo system
        this.history = [];
        this.historyIndex = -1;
        this.maxHistorySize = 50;
        this.isRestoring = false;
        
        this.init();
    }
    
    init() {
        this.createCanvas();
        this.createStage();
        this.setupEventListeners();
        this.draw();
    }
    
    createCanvas() {
        // Canvas container
        const canvasContainer = document.createElement('div');
        canvasContainer.className = 'visual-editor-container';
        canvasContainer.style.cssText = `
            position: relative;
            width: ${this.config.width}px;
            height: ${this.config.height}px;
            border: 2px solid #ddd;
            background-color: #f8f9fa;
            overflow: hidden;
        `;
        
        // Canvas element
        this.canvas = document.createElement('canvas');
        this.canvas.width = this.config.width;
        this.canvas.height = this.config.height;
        this.canvas.style.cssText = `
            cursor: crosshair;
            position: absolute;
            top: 0;
            left: 0;
        `;
        
        this.ctx = this.canvas.getContext('2d');
        
        // Grid layer
        this.gridCanvas = document.createElement('canvas');
        this.gridCanvas.width = this.config.width;
        this.gridCanvas.height = this.config.height;
        this.gridCanvas.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            pointer-events: none;
        `;
        
        canvasContainer.appendChild(this.gridCanvas);
        canvasContainer.appendChild(this.canvas);
        this.container.appendChild(canvasContainer);
        
        this.drawGrid();
    }
    
    createStage() {
        // Sahne alanı
        const stageContainer = document.createElement('div');
        stageContainer.className = 'stage-container';
        stageContainer.style.cssText = `
            position: absolute;
            background-color: #2c3e50;
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: bold;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            z-index: 100;
            cursor: move;
        `;
        
        // Sahne metni
        const stageText = document.createElement('div');
        stageText.textContent = '🎭 SAHNE';
        stageText.className = 'stage-text';
        stageContainer.appendChild(stageText);
        
        this.container.querySelector('.visual-editor-container').appendChild(stageContainer);
        this.stage = stageContainer;
        
        this.positionStage();
    }
    
    positionStage() {
        const stageSize = { width: 100, height: 40 };
        let x = 0, y = 0;
        
        switch (this.config.stagePosition) {
            case 'top':
                x = (this.config.width - stageSize.width) / 2;
                y = 10;
                break;
            case 'bottom':
                x = (this.config.width - stageSize.width) / 2;
                y = this.config.height - stageSize.height - 10;
                break;
            case 'left':
                x = 10;
                y = (this.config.height - stageSize.height) / 2;
                break;
            case 'right':
                x = this.config.width - stageSize.width - 10;
                y = (this.config.height - stageSize.height) / 2;
                break;
        }
        
        this.stage.style.left = `${x}px`;
        this.stage.style.top = `${y}px`;
    }
    
    setupEventListeners() {
        // Canvas event listeners
        this.canvas.addEventListener('mousedown', this.onMouseDown.bind(this));
        this.canvas.addEventListener('mousemove', this.onMouseMove.bind(this));
        this.canvas.addEventListener('mouseup', this.onMouseUp.bind(this));
        this.canvas.addEventListener('click', this.onClick.bind(this));
        
        // Sahne drag event listener
        this.stage.addEventListener('mousedown', this.onStageMouseDown.bind(this));
        this.stage.addEventListener('mousemove', this.onStageMouseMove.bind(this));
        this.stage.addEventListener('mouseup', this.onStageMouseUp.bind(this));
        
        // Keyboard shortcuts
        document.addEventListener('keydown', this.onKeyDown.bind(this));
        
        // Zoom controls
        this.setupZoomControls();
    }
    
    setupZoomControls() {
        const zoomControls = document.createElement('div');
        zoomControls.className = 'zoom-controls';
        zoomControls.style.cssText = `
            position: absolute;
            top: 10px;
            right: 10px;
            z-index: 200;
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        `;
        
        // Zoom in button
        const zoomInBtn = document.createElement('button');
        zoomInBtn.innerHTML = '+';
        zoomInBtn.style.cssText = `
            margin: 2px;
            padding: 5px 8px;
            border: 1px solid #ddd;
            background: white;
            cursor: pointer;
            border-radius: 3px;
        `;
        zoomInBtn.addEventListener('click', () => this.zoomIn());
        
        // Zoom out button
        const zoomOutBtn = document.createElement('button');
        zoomOutBtn.innerHTML = '-';
        zoomOutBtn.style.cssText = `
            margin: 2px;
            padding: 5px 8px;
            border: 1px solid #ddd;
            background: white;
            cursor: pointer;
            border-radius: 3px;
        `;
        zoomOutBtn.addEventListener('click', () => this.zoomOut());
        
        // Zoom reset button
        const zoomResetBtn = document.createElement('button');
        zoomResetBtn.innerHTML = '↻';
        zoomResetBtn.style.cssText = `
            margin: 2px;
            padding: 5px 8px;
            border: 1px solid #ddd;
            background: white;
            cursor: pointer;
            border-radius: 3px;
        `;
        zoomResetBtn.addEventListener('click', () => this.zoomReset());
        
        // Zoom level indicator
        this.zoomIndicator = document.createElement('span');
        this.zoomIndicator.textContent = '100%';
        this.zoomIndicator.style.cssText = `
            margin: 2px;
            padding: 5px;
            font-size: 12px;
            color: #666;
        `;
        
        zoomControls.appendChild(zoomInBtn);
        zoomControls.appendChild(zoomResetBtn);
        zoomControls.appendChild(zoomOutBtn);
        zoomControls.appendChild(this.zoomIndicator);
        
        this.container.querySelector('.visual-editor-container').appendChild(zoomControls);
    }
    
    addSeating(type, position, config = {}) {
        const seating = {
            id: Date.now() + Math.random(),
            type: type,
            x: position.x,
            y: position.y,
            width: config.width || 60,
            height: config.height || 40,
            capacity: config.capacity || 4,
            name: config.name || `M${this.seatings.length + 1}`,
            color: config.color || '#3498db',
            icon: config.icon || '🪑',
            reserved: false
        };
        
        this.seatings.push(seating);
        this.saveState();
        this.draw();
        return seating;
    }
    
    removeSeating(id) {
        const seatingToRemove = this.seatings.find(s => s.id === id);
        this.seatings = this.seatings.filter(s => s.id !== id);
        if (this.selectedSeating && this.selectedSeating.id === id) {
            this.selectedSeating = null;
        }
        this.saveState();
        this.draw();
    }
    
    selectSeating(id) {
        this.selectedSeating = this.seatings.find(s => s.id === id) || null;
        this.draw();
    }
    
    getSeatingAt(x, y) {
        return this.seatings.find(s => {
            return x >= s.x && x <= s.x + s.width &&
                   y >= s.y && y <= s.y + s.height;
        });
    }
    
    onMouseDown(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const seating = this.getSeatingAt(x, y);
        if (seating) {
            this.selectedSeating = seating;
            this.isDragging = true;
            this.dragOffset = {
                x: x - seating.x,
                y: y - seating.y
            };
            this.draw();
        }
    }
    
    onMouseMove(e) {
        if (this.isDragging && this.selectedSeating) {
            const rect = this.canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            // Grid snap
            this.selectedSeating.x = Math.round((x - this.dragOffset.x) / this.config.gridSize) * this.config.gridSize;
            this.selectedSeating.y = Math.round((y - this.dragOffset.y) / this.config.gridSize) * this.config.gridSize;
            
            this.draw();
        }
    }
    
    onMouseUp() {
        if (this.isDragging) {
            this.isDragging = false;
            this.saveState(); // Save state after drag operation
        }
    }
    
    // Undo/Redo System Methods
    saveState() {
        if (this.isRestoring) return;
        
        // Remove any future history if we're not at the end
        if (this.historyIndex < this.history.length - 1) {
            this.history = this.history.slice(0, this.historyIndex + 1);
        }
        
        // Add current state
        const state = {
            seatings: JSON.parse(JSON.stringify(this.seatings)),
            stagePosition: this.config.stagePosition,
            canvas: {
                width: this.config.width,
                height: this.config.height,
                gridSize: this.config.gridSize
            }
        };
        
        this.history.push(state);
        this.historyIndex = this.history.length - 1;
        
        // Limit history size
        if (this.history.length > this.maxHistorySize) {
            this.history.shift();
            this.historyIndex--;
        }
    }
    
    undo() {
        if (this.historyIndex > 0) {
            this.isRestoring = true;
            this.historyIndex--;
            this.restoreState(this.history[this.historyIndex]);
            this.isRestoring = false;
            this.draw();
            return true;
        }
        return false;
    }
    
    redo() {
        if (this.historyIndex < this.history.length - 1) {
            this.isRestoring = true;
            this.historyIndex++;
            this.restoreState(this.history[this.historyIndex]);
            this.isRestoring = false;
            this.draw();
            return true;
        }
        return false;
    }
    
    restoreState(state) {
        this.seatings = JSON.parse(JSON.stringify(state.seatings));
        this.config.stagePosition = state.stagePosition;
        this.config.width = state.canvas.width;
        this.config.height = state.canvas.height;
        this.config.gridSize = state.canvas.gridSize;
        this.positionStage();
    }
    
    canUndo() {
        return this.historyIndex > 0;
    }
    
    canRedo() {
        return this.historyIndex < this.history.length - 1;
    }
    
    clearHistory() {
        this.history = [];
        this.historyIndex = -1;
        this.saveState(); // Save current state as initial state
    }
    
    // Collision detection and resolution
    checkCollisions(newSeating) {
        return this.seatings.filter(seating => {
            if (seating.id === newSeating.id) return false;
            
            return !(newSeating.x + newSeating.width <= seating.x ||
                    seating.x + seating.width <= newSeating.x ||
                    newSeating.y + newSeating.height <= seating.y ||
                    seating.y + seating.height <= newSeating.y);
        });
    }
    
    resolveCollisions(seating) {
        const collisions = this.checkCollisions(seating);
        if (collisions.length === 0) return true;
        
        // Try to find a non-colliding position nearby
        const directions = [
            {x: 0, y: -this.config.gridSize}, // up
            {x: 0, y: this.config.gridSize},  // down
            {x: -this.config.gridSize, y: 0}, // left
            {x: this.config.gridSize, y: 0},  // right
            {x: -this.config.gridSize, y: -this.config.gridSize}, // up-left
            {x: this.config.gridSize, y: -this.config.gridSize},  // up-right
            {x: -this.config.gridSize, y: this.config.gridSize},  // down-left
            {x: this.config.gridSize, y: this.config.gridSize}   // down-right
        ];
        
        for (let offset of directions) {
            const testX = seating.x + offset.x;
            const testY = seating.y + offset.y;
            
            // Ensure new position is within canvas bounds
            if (testX < 0 || testY < 0 || 
                testX + seating.width > this.config.width || 
                testY + seating.height > this.config.height) {
                continue;
            }
            
            const testSeating = {...seating, x: testX, y: testY};
            const testCollisions = this.checkCollisions(testSeating);
            
            if (testCollisions.length === 0) {
                seating.x = testX;
                seating.y = testY;
                return true;
            }
        }
        
        return false;
    }
    
    autoArrange() {
        // Simple auto-arrange algorithm - arrange seatings in a grid
        const sortedSeatings = [...this.seatings].sort((a, b) => {
            // Sort by type first, then by creation order
            if (a.type !== b.type) {
                return a.type.localeCompare(b.type);
            }
            return a.name.localeCompare(b.name);
        });
        
        const cols = Math.floor(this.config.width / 100); // 100px per column
        const startX = 50;
        const startY = 80; // Leave space for stage
        const spacingX = 100;
        const spacingY = 80;
        
        sortedSeatings.forEach((seating, index) => {
            const col = index % cols;
            const row = Math.floor(index / cols);
            
            const newX = startX + col * spacingX;
            const newY = startY + row * spacingY;
            
            // Check if new position would cause collision
            const testSeating = {...seating, x: newX, y: newY};
            const collisions = this.checkCollisions(testSeating);
            
            if (collisions.length === 0) {
                seating.x = newX;
                seating.y = newY;
            }
        });
        
        this.saveState();
        this.draw();
    }
    
    onClick(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const seating = this.getSeatingAt(x, y);
        if (!seating) {
            this.selectedSeating = null;
            this.draw();
        }
    }
    
    onStageMouseDown(e) {
        this.stageDragging = true;
        this.stageDragOffset = {
            x: e.clientX - this.stage.offsetLeft,
            y: e.clientY - this.stage.offsetTop
        };
        e.preventDefault();
    }
    
    onStageMouseMove(e) {
        if (this.stageDragging) {
            const rect = this.container.querySelector('.visual-editor-container').getBoundingClientRect();
            const newX = e.clientX - this.stageDragOffset.x - rect.left;
            const newY = e.clientY - this.stageDragOffset.y - rect.top;
            
            this.stage.style.left = `${Math.max(0, Math.min(newX, rect.width - this.stage.offsetWidth))}px`;
            this.stage.style.top = `${Math.max(0, Math.min(newY, rect.height - this.stage.offsetHeight))}px`;
            
            // Update stage position
            this.updateStagePosition();
        }
    }
    
    onStageMouseUp() {
        this.stageDragging = false;
    }
    
    updateStagePosition() {
        const rect = this.container.querySelector('.visual-editor-container').getBoundingClientRect();
        const stageRect = this.stage.getBoundingClientRect();
        const stageCenterX = stageRect.left - rect.left + stageRect.width / 2;
        const stageCenterY = stageRect.top - rect.top + stageRect.height / 2;
        
        if (stageCenterX < rect.width / 3) {
            this.config.stagePosition = 'left';
        } else if (stageCenterX > rect.width * 2 / 3) {
            this.config.stagePosition = 'right';
        } else if (stageCenterY < rect.height / 3) {
            this.config.stagePosition = 'top';
        } else {
            this.config.stagePosition = 'bottom';
        }
    }
    
    onKeyDown(e) {
        if (this.selectedSeating) {
            const step = this.config.gridSize;
            
            switch (e.key) {
                case 'Delete':
                case 'Backspace':
                    this.removeSeating(this.selectedSeating.id);
                    break;
                case 'ArrowUp':
                    this.selectedSeating.y -= step;
                    this.draw();
                    e.preventDefault();
                    break;
                case 'ArrowDown':
                    this.selectedSeating.y += step;
                    this.draw();
                    e.preventDefault();
                    break;
                case 'ArrowLeft':
                    this.selectedSeating.x -= step;
                    this.draw();
                    e.preventDefault();
                    break;
                case 'ArrowRight':
                    this.selectedSeating.x += step;
                    this.draw();
                    e.preventDefault();
                    break;
            }
        }
        
        // Global shortcuts
        if (e.ctrlKey || e.metaKey) {
            switch (e.key) {
                case '=':
                case '+':
                    this.zoomIn();
                    e.preventDefault();
                    break;
                case '-':
                    this.zoomOut();
                    e.preventDefault();
                    break;
                case '0':
                    this.zoomReset();
                    e.preventDefault();
                    break;
            }
        }
    }
    
    zoomIn() {
        this.zoom = Math.min(this.zoom * 1.2, 3);
        this.updateZoom();
    }
    
    zoomOut() {
        this.zoom = Math.max(this.zoom / 1.2, 0.3);
        this.updateZoom();
    }
    
    zoomReset() {
        this.zoom = 1;
        this.updateZoom();
    }
    
    updateZoom() {
        this.zoomIndicator.textContent = `${Math.round(this.zoom * 100)}%`;
        this.canvas.style.transform = `scale(${this.zoom})`;
        this.canvas.style.transformOrigin = 'top left';
    }
    
    drawGrid() {
        const ctx = this.gridCanvas.getContext('2d');
        ctx.clearRect(0, 0, this.config.width, this.config.height);
        
        ctx.strokeStyle = '#e0e0e0';
        ctx.lineWidth = 0.5;
        
        // Vertical lines
        for (let x = 0; x <= this.config.width; x += this.config.gridSize) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, this.config.height);
            ctx.stroke();
        }
        
        // Horizontal lines
        for (let y = 0; y <= this.config.height; y += this.config.gridSize) {
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(this.config.width, y);
            ctx.stroke();
        }
    }
    
    draw() {
        this.ctx.clearRect(0, 0, this.config.width, this.config.height);
        
        // Draw seatings
        this.seatings.forEach(seating => {
            this.drawSeating(seating);
        });
        
        // Draw selection highlight
        if (this.selectedSeating) {
            this.drawSelection(this.selectedSeating);
        }
    }
    
    drawSeating(seating) {
        this.ctx.fillStyle = seating.color;
        this.ctx.strokeStyle = '#2c3e50';
        this.ctx.lineWidth = 2;
        
        // Seating rectangle
        this.ctx.fillRect(seating.x, seating.y, seating.width, seating.height);
        this.ctx.strokeRect(seating.x, seating.y, seating.width, seating.height);
        
        // Seating number
        this.ctx.fillStyle = 'white';
        this.ctx.font = 'bold 12px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        
        // Icon
        this.ctx.font = '16px Arial';
        this.ctx.fillText(
            seating.icon, 
            seating.x + seating.width / 2, 
            seating.y + seating.height / 2 - 8
        );
        
        // Number
        this.ctx.font = 'bold 10px Arial';
        this.ctx.fillText(
            seating.name, 
            seating.x + seating.width / 2, 
            seating.y + seating.height / 2 + 8
        );
        
        // Capacity indicator
        this.ctx.font = '8px Arial';
        this.ctx.fillText(
            `${seating.capacity} kişi`, 
            seating.x + seating.width / 2, 
            seating.y + seating.height - 4
        );
    }
    
    drawSelection(seating) {
        // Selection border
        this.ctx.strokeStyle = '#f39c12';
        this.ctx.lineWidth = 3;
        this.ctx.strokeRect(seating.x - 2, seating.y - 2, seating.width + 4, seating.height + 4);
        
        // Handle points
        const handles = this.getSelectionHandles(seating);
        this.ctx.fillStyle = '#f39c12';
        
        handles.forEach(handle => {
            this.ctx.fillRect(handle.x - 3, handle.y - 3, 6, 6);
        });
    }
    
    getSelectionHandles(seating) {
        const x = seating.x, y = seating.y, w = seating.width, h = seating.height;
        return [
            { x: x, y: y, cursor: 'nw-resize' },
            { x: x + w, y: y, cursor: 'ne-resize' },
            { x: x, y: y + h, cursor: 'sw-resize' },
            { x: x + w, y: y + h, cursor: 'se-resize' }
        ];
    }
    
    // Public methods for external access
    addMasa(kisiSayisi, position) {
        const config = {
            name: `M${this.seatings.length + 1}`,
            width: 60,
            height: 40,
            capacity: kisiSayisi,
            color: this.getColorForCapacity(kisiSayisi),
            icon: '🪑',
            type: 'masa'
        };
        return this.addSeating('masa', position, config);
    }
    
    addKoltuk(position) {
        const config = {
            name: `K${this.seatings.length + 1}`,
            width: 30,
            height: 30,
            capacity: 1,
            color: '#e74c3c',
            icon: '💺',
            type: 'koltuk'
        };
        return this.addSeating('koltuk', position, config);
    }
    
    addVipLoca(position) {
        const config = {
            name: `VIP${this.seatings.length + 1}`,
            width: 80,
            height: 60,
            capacity: 8,
            color: '#f1c40f',
            icon: '👑',
            type: 'vip'
        };
        return this.addSeating('vip', position, config);
    }
    
    getColorForCapacity(capacity) {
        const colors = {
            1: '#e74c3c',
            2: '#3498db',
            4: '#2ecc71',
            6: '#f39c12',
            8: '#9b59b6',
            10: '#34495e',
            12: '#1abc9c'
        };
        return colors[capacity] || '#95a5a6';
    }
    
    getSeatingsData() {
        return this.seatings.map(seating => ({
            id: seating.id,
            name: seating.name,
            type: seating.type,
            x: seating.x,
            y: seating.y,
            width: seating.width,
            height: seating.height,
            capacity: seating.capacity,
            color: seating.color,
            icon: seating.icon
        }));
    }
    
    loadSeatingsData(seatingsData) {
        this.seatings = [];
        seatingsData.forEach(data => {
            this.addSeating(data.type, { x: data.x, y: data.y }, data);
        });
    }
    
    getConfiguration() {
        return {
            stagePosition: this.config.stagePosition,
            seatings: this.getSeatingsData(),
            gridSize: this.config.gridSize
        };
    }
    
    loadConfiguration(config) {
        if (config.stagePosition) {
            this.config.stagePosition = config.stagePosition;
            this.positionStage();
        }
        
        if (config.seatings) {
            this.loadSeatingsData(config.seatings);
        }
        
        if (config.gridSize) {
            this.config.gridSize = config.gridSize;
            this.drawGrid();
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VisualSeatingEditor;
}
