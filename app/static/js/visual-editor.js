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
        this.gridVisible = true; // Grid visibility toggle
        this.showCollisionWarning = false; // Collision warning flag
        
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
        this.setupKeyboardNavigation();
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
        // Canvas mouse event listeners
        this.canvas.addEventListener('mousedown', this.onMouseDown.bind(this));
        this.canvas.addEventListener('mousemove', this.onMouseMove.bind(this));
        this.canvas.addEventListener('mouseup', this.onMouseUp.bind(this));
        this.canvas.addEventListener('click', this.onClick.bind(this));
        
        // Canvas touch event listeners
        this.canvas.addEventListener('touchstart', this.onTouchStart.bind(this), { passive: false });
        this.canvas.addEventListener('touchmove', this.onTouchMove.bind(this), { passive: false });
        this.canvas.addEventListener('touchend', this.onTouchEnd.bind(this), { passive: false });
        
        // Sahne drag event listener - Global listeners for better drag experience
        this.stage.addEventListener('mousedown', this.onStageMouseDown.bind(this));
        document.addEventListener('mousemove', this.onStageMouseMove.bind(this));
        document.addEventListener('mouseup', this.onStageMouseUp.bind(this));
        
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
        
        // Boundary check
        seating.x = Math.max(0, Math.min(seating.x, this.config.width - seating.width));
        seating.y = Math.max(0, Math.min(seating.y, this.config.height - seating.height));
        
        // Grid snap
        seating.x = Math.round(seating.x / this.config.gridSize) * this.config.gridSize;
        seating.y = Math.round(seating.y / this.config.gridSize) * this.config.gridSize;
        
        console.log('➕ Seating ekleniyor:', seating);
        
        // Temporarily add to check collisions
        this.seatings.push(seating);
        
        // Check for collisions
        const collisions = this.checkCollisions(seating);
        if (collisions.length > 0) {
            console.log('⚠️ Çakışma tespit edildi, pozisyon ayarlanıyor...');
            // Try to resolve collision
            const resolved = this.resolveCollisions(seating);
            if (!resolved) {
                console.warn('❌ Çakışma çözülemedi, oturum eklenemedi');
                this.seatings.pop(); // Remove the seating
                return null;
            }
        }
        
        console.log('📊 Toplam seating:', this.seatings.length);
        
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
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        // Update cursor based on position
        if (!this.isDragging) {
            this.updateCursor(x, y);
        }
        
        if (this.isDragging && this.selectedSeating) {
            // Calculate new position
            let newX = x - this.dragOffset.x;
            let newY = y - this.dragOffset.y;
            
            // Grid snap
            newX = Math.round(newX / this.config.gridSize) * this.config.gridSize;
            newY = Math.round(newY / this.config.gridSize) * this.config.gridSize;
            
            // Boundary check - keep within canvas
            newX = Math.max(0, Math.min(newX, this.config.width - this.selectedSeating.width));
            newY = Math.max(0, Math.min(newY, this.config.height - this.selectedSeating.height));
            
            // Store old position for collision check
            const oldX = this.selectedSeating.x;
            const oldY = this.selectedSeating.y;
            
            // Try new position
            this.selectedSeating.x = newX;
            this.selectedSeating.y = newY;
            
            // Check for collisions
            const collisions = this.checkCollisions(this.selectedSeating);
            if (collisions.length > 0) {
                // Revert to old position if collision detected
                this.selectedSeating.x = oldX;
                this.selectedSeating.y = oldY;
                
                // Visual feedback - flash red border
                this.showCollisionWarning = true;
                setTimeout(() => {
                    this.showCollisionWarning = false;
                    this.draw();
                }, 200);
            }
            
            this.draw();
        }
    }
    
    onMouseUp() {
        if (this.isDragging) {
            this.isDragging = false;
            this.saveState(); // Save state after drag operation
        }
    }
    
    // Touch event handlers
    onTouchStart(e) {
        e.preventDefault();
        const touch = e.touches[0];
        const rect = this.canvas.getBoundingClientRect();
        const x = touch.clientX - rect.left;
        const y = touch.clientY - rect.top;
        
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
    
    onTouchMove(e) {
        e.preventDefault();
        if (this.isDragging && this.selectedSeating) {
            const touch = e.touches[0];
            const rect = this.canvas.getBoundingClientRect();
            const x = touch.clientX - rect.left;
            const y = touch.clientY - rect.top;
            
            // Calculate new position
            let newX = x - this.dragOffset.x;
            let newY = y - this.dragOffset.y;
            
            // Grid snap
            newX = Math.round(newX / this.config.gridSize) * this.config.gridSize;
            newY = Math.round(newY / this.config.gridSize) * this.config.gridSize;
            
            // Boundary check
            newX = Math.max(0, Math.min(newX, this.config.width - this.selectedSeating.width));
            newY = Math.max(0, Math.min(newY, this.config.height - this.selectedSeating.height));
            
            // Store old position for collision check
            const oldX = this.selectedSeating.x;
            const oldY = this.selectedSeating.y;
            
            // Try new position
            this.selectedSeating.x = newX;
            this.selectedSeating.y = newY;
            
            // Check for collisions
            const collisions = this.checkCollisions(this.selectedSeating);
            if (collisions.length > 0) {
                // Revert to old position if collision detected
                this.selectedSeating.x = oldX;
                this.selectedSeating.y = oldY;
                
                // Visual feedback
                this.showCollisionWarning = true;
                setTimeout(() => {
                    this.showCollisionWarning = false;
                    this.draw();
                }, 200);
            }
            
            this.draw();
        }
    }
    
    onTouchEnd(e) {
        e.preventDefault();
        if (this.isDragging) {
            this.isDragging = false;
            this.saveState();
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
            let newX = e.clientX - this.stageDragOffset.x - rect.left;
            let newY = e.clientY - this.stageDragOffset.y - rect.top;
            
            // Boundary check - keep stage within canvas
            newX = Math.max(0, Math.min(newX, this.config.width - this.stage.offsetWidth));
            newY = Math.max(0, Math.min(newY, this.config.height - this.stage.offsetHeight));
            
            this.stage.style.left = `${newX}px`;
            this.stage.style.top = `${newY}px`;
            
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
        // Selection border - red if collision warning, orange otherwise
        this.ctx.strokeStyle = this.showCollisionWarning ? '#e74c3c' : '#f39c12';
        this.ctx.lineWidth = this.showCollisionWarning ? 4 : 3;
        this.ctx.strokeRect(seating.x - 2, seating.y - 2, seating.width + 4, seating.height + 4);
        
        // Handle points
        const handles = this.getSelectionHandles(seating);
        this.ctx.fillStyle = this.showCollisionWarning ? '#e74c3c' : '#f39c12';
        
        handles.forEach(handle => {
            this.ctx.fillRect(handle.x - 3, handle.y - 3, 6, 6);
        });
        
        // Show collision warning text
        if (this.showCollisionWarning) {
            this.ctx.fillStyle = '#e74c3c';
            this.ctx.font = 'bold 12px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.fillText('⚠️ Çakışma!', seating.x + seating.width / 2, seating.y - 10);
        }
    }
    
    getSelectionHandles(seating) {
        const x = seating.x, y = seating.y, w = seating.width, h = seating.height;
        return [
            { x: x, y: y, cursor: 'nw-resize', type: 'nw' },
            { x: x + w, y: y, cursor: 'ne-resize', type: 'ne' },
            { x: x, y: y + h, cursor: 'sw-resize', type: 'sw' },
            { x: x + w, y: y + h, cursor: 'se-resize', type: 'se' },
            { x: x + w/2, y: y, cursor: 'n-resize', type: 'n' },
            { x: x + w/2, y: y + h, cursor: 's-resize', type: 's' },
            { x: x, y: y + h/2, cursor: 'w-resize', type: 'w' },
            { x: x + w, y: y + h/2, cursor: 'e-resize', type: 'e' }
        ];
    }
    
    // Check if mouse is over a resize handle
    getHandleAt(x, y) {
        if (!this.selectedSeating) return null;
        
        const handles = this.getSelectionHandles(this.selectedSeating);
        const handleSize = 6;
        
        for (let handle of handles) {
            if (x >= handle.x - handleSize && x <= handle.x + handleSize &&
                y >= handle.y - handleSize && y <= handle.y + handleSize) {
                return handle;
            }
        }
        
        return null;
    }
    
    // Update cursor based on handle
    updateCursor(x, y) {
        const handle = this.getHandleAt(x, y);
        if (handle) {
            this.canvas.style.cursor = handle.cursor;
        } else if (this.getSeatingAt(x, y)) {
            this.canvas.style.cursor = 'move';
        } else {
            this.canvas.style.cursor = 'crosshair';
        }
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
        console.log('📥 Loading seatings data:', seatingsData.length, 'items');
        this.seatings = [];
        
        // Disable collision check temporarily for bulk loading
        const tempCollisionCheck = this.checkCollisions;
        this.checkCollisions = () => [];
        
        seatingsData.forEach((data, index) => {
            console.log(`  ${index + 1}. Loading: ${data.name || data.seat_number}`);
            const seating = this.addSeating(data.type, { x: data.x, y: data.y }, data);
            if (!seating) {
                console.warn(`  ⚠️ Failed to load seating ${index + 1}`);
            }
        });
        
        // Re-enable collision check
        this.checkCollisions = tempCollisionCheck;
        
        console.log('✅ Loaded', this.seatings.length, 'seatings');
        this.draw();
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
    
    // Snap seating to grid
    snapToGrid(seating) {
        if (!seating) return;
        
        seating.x = Math.round(seating.x / this.config.gridSize) * this.config.gridSize;
        seating.y = Math.round(seating.y / this.config.gridSize) * this.config.gridSize;
        
        // Boundary check
        seating.x = Math.max(0, Math.min(seating.x, this.config.width - seating.width));
        seating.y = Math.max(0, Math.min(seating.y, this.config.height - seating.height));
    }
    
    // Keyboard navigation
    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            if (!this.selectedSeating) return;
            
            const step = e.shiftKey ? this.config.gridSize : 1;
            let moved = false;
            
            // Store old position for collision check
            const oldX = this.selectedSeating.x;
            const oldY = this.selectedSeating.y;
            
            switch(e.key) {
                case 'ArrowUp':
                    this.selectedSeating.y -= step;
                    moved = true;
                    break;
                case 'ArrowDown':
                    this.selectedSeating.y += step;
                    moved = true;
                    break;
                case 'ArrowLeft':
                    this.selectedSeating.x -= step;
                    moved = true;
                    break;
                case 'ArrowRight':
                    this.selectedSeating.x += step;
                    moved = true;
                    break;
                case 'Delete':
                case 'Backspace':
                    e.preventDefault();
                    this.deleteSeating(this.selectedSeating);
                    return;
                case 'Escape':
                    this.selectedSeating = null;
                    this.draw();
                    return;
                case 'd':
                case 'D':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.duplicateSeating(this.selectedSeating);
                        return;
                    }
                    break;
            }
            
            if (moved) {
                e.preventDefault();
                this.snapToGrid(this.selectedSeating);
                
                // Check for collisions after move
                const collisions = this.checkCollisions(this.selectedSeating);
                if (collisions.length > 0) {
                    // Revert to old position
                    this.selectedSeating.x = oldX;
                    this.selectedSeating.y = oldY;
                } else {
                    this.saveState();
                }
                
                this.draw();
            }
        });
    }
    
    duplicateSeating(seating) {
        if (!seating) return null;
        
        const newSeating = {
            ...seating,
            id: Date.now(),
            x: seating.x + this.config.gridSize * 2,
            y: seating.y + this.config.gridSize * 2,
            name: `${seating.name} (Kopya)`
        };
        
        // Boundary check
        newSeating.x = Math.max(0, Math.min(newSeating.x, this.config.width - newSeating.width));
        newSeating.y = Math.max(0, Math.min(newSeating.y, this.config.height - newSeating.height));
        
        // Temporarily add to check collisions
        this.seatings.push(newSeating);
        
        // Check for collisions and resolve
        const collisions = this.checkCollisions(newSeating);
        if (collisions.length > 0) {
            const resolved = this.resolveCollisions(newSeating);
            if (!resolved) {
                // If can't resolve, try different offsets
                const offsets = [
                    {x: -this.config.gridSize * 2, y: 0},
                    {x: 0, y: -this.config.gridSize * 2},
                    {x: this.config.gridSize * 4, y: 0},
                    {x: 0, y: this.config.gridSize * 4}
                ];
                
                let placed = false;
                for (let offset of offsets) {
                    newSeating.x = seating.x + offset.x;
                    newSeating.y = seating.y + offset.y;
                    
                    // Boundary check
                    if (newSeating.x < 0 || newSeating.y < 0 ||
                        newSeating.x + newSeating.width > this.config.width ||
                        newSeating.y + newSeating.height > this.config.height) {
                        continue;
                    }
                    
                    const testCollisions = this.checkCollisions(newSeating);
                    if (testCollisions.length === 0) {
                        placed = true;
                        break;
                    }
                }
                
                if (!placed) {
                    console.warn('❌ Çoğaltma için uygun pozisyon bulunamadı');
                    this.seatings.pop();
                    return null;
                }
            }
        }
        
        this.selectedSeating = newSeating;
        this.saveState();
        this.draw();
        return newSeating;
    }
    
    deleteSeating(seating) {
        if (!seating) return;
        
        const index = this.seatings.indexOf(seating);
        if (index > -1) {
            this.seatings.splice(index, 1);
            this.selectedSeating = null;
            this.saveState();
            this.draw();
        }
    }
    
    // Alignment helpers
    alignLeft() {
        if (this.seatings.length === 0) return;
        const minX = Math.min(...this.seatings.map(s => s.x));
        this.seatings.forEach(s => s.x = minX);
        this.saveState();
        this.draw();
    }
    
    alignRight() {
        if (this.seatings.length === 0) return;
        const maxX = Math.max(...this.seatings.map(s => s.x + s.width));
        this.seatings.forEach(s => s.x = maxX - s.width);
        this.saveState();
        this.draw();
    }
    
    alignTop() {
        if (this.seatings.length === 0) return;
        const minY = Math.min(...this.seatings.map(s => s.y));
        this.seatings.forEach(s => s.y = minY);
        this.saveState();
        this.draw();
    }
    
    alignBottom() {
        if (this.seatings.length === 0) return;
        const maxY = Math.max(...this.seatings.map(s => s.y + s.height));
        this.seatings.forEach(s => s.y = maxY - s.height);
        this.saveState();
        this.draw();
    }
    
    alignCenter() {
        if (this.seatings.length === 0) return;
        const centerX = this.config.width / 2;
        const avgWidth = this.seatings.reduce((sum, s) => sum + s.width, 0) / this.seatings.length;
        this.seatings.forEach(s => s.x = centerX - avgWidth / 2);
        this.saveState();
        this.draw();
    }
    
    alignMiddle() {
        if (this.seatings.length === 0) return;
        const centerY = this.config.height / 2;
        const avgHeight = this.seatings.reduce((sum, s) => sum + s.height, 0) / this.seatings.length;
        this.seatings.forEach(s => s.y = centerY - avgHeight / 2);
        this.saveState();
        this.draw();
    }
    
    // Distribute helpers
    distributeHorizontally() {
        if (this.seatings.length < 3) return;
        
        const sorted = [...this.seatings].sort((a, b) => a.x - b.x);
        const first = sorted[0];
        const last = sorted[sorted.length - 1];
        const totalSpace = (last.x + last.width) - first.x;
        const spacing = totalSpace / (sorted.length - 1);
        
        sorted.forEach((seating, i) => {
            if (i > 0 && i < sorted.length - 1) {
                seating.x = first.x + (spacing * i);
            }
        });
        
        this.saveState();
        this.draw();
    }
    
    distributeVertically() {
        if (this.seatings.length < 3) return;
        
        const sorted = [...this.seatings].sort((a, b) => a.y - b.y);
        const first = sorted[0];
        const last = sorted[sorted.length - 1];
        const totalSpace = (last.y + last.height) - first.y;
        const spacing = totalSpace / (sorted.length - 1);
        
        sorted.forEach((seating, i) => {
            if (i > 0 && i < sorted.length - 1) {
                seating.y = first.y + (spacing * i);
            }
        });
        
        this.saveState();
        this.draw();
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VisualSeatingEditor;
}
