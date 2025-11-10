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
        this.selectedSeatings = []; // Multi-select support
        this.isDragging = false;
        this.dragOffset = { x: 0, y: 0 };
        this.zoom = 1;
        this.pan = { x: 0, y: 0 };
        this.gridVisible = true; // Grid visibility toggle
        this.showCollisionWarning = false; // Collision warning flag
        
        // Resize
        this.isResizing = false;
        this.resizeHandle = null;
        this.resizeStart = null;
        this.resizeOriginal = null;
        
        // Lasso selection
        this.isLassoSelecting = false;
        this.lassoStart = null;
        this.lassoEnd = null;
        
        // Alignment guides
        this.showAlignmentGuides = true;
        this.alignmentGuides = [];
        
        // Snap settings
        this.snapToGrid = true;
        this.snapToObjects = true;
        this.snapDistance = 10;
        
        // Clipboard
        this.clipboard = [];
        
        // Auto-save
        this.autoSaveEnabled = true;
        this.autoSaveInterval = 30000; // 30 seconds
        this.lastSaveTime = Date.now();
        this.hasUnsavedChanges = false;
        
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
        this.setupAutoSave();
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
        
        // Check if clicking on resize handle
        const handle = this.getHandleAt(x, y);
        if (handle && this.selectedSeating) {
            this.isResizing = true;
            this.resizeHandle = handle;
            this.resizeStart = { x, y };
            this.resizeOriginal = {
                x: this.selectedSeating.x,
                y: this.selectedSeating.y,
                width: this.selectedSeating.width,
                height: this.selectedSeating.height
            };
            return;
        }
        
        const seating = this.getSeatingAt(x, y);
        
        // Shift key for multi-select
        if (e.shiftKey && seating) {
            if (this.selectedSeatings.includes(seating)) {
                // Remove from selection
                this.selectedSeatings = this.selectedSeatings.filter(s => s !== seating);
            } else {
                // Add to selection
                this.selectedSeatings.push(seating);
            }
            this.selectedSeating = seating;
            this.draw();
            return;
        }
        
        // Ctrl/Cmd key for lasso selection
        if ((e.ctrlKey || e.metaKey) && !seating) {
            this.isLassoSelecting = true;
            this.lassoStart = { x, y };
            this.lassoEnd = { x, y };
            this.draw();
            return;
        }
        
        if (seating) {
            // If clicking on already selected seating in multi-select, start dragging all
            if (this.selectedSeatings.includes(seating)) {
                this.selectedSeating = seating;
                this.isDragging = true;
                this.dragOffset = {
                    x: x - seating.x,
                    y: y - seating.y
                };
            } else {
                // Single select
                this.selectedSeating = seating;
                this.selectedSeatings = [seating];
                this.isDragging = true;
                this.dragOffset = {
                    x: x - seating.x,
                    y: y - seating.y
                };
            }
            this.draw();
        } else {
            // Click on empty space - clear selection (lasso only with Ctrl/Cmd)
            this.selectedSeating = null;
            this.selectedSeatings = [];
            this.draw();
        }
    }
    
    onMouseMove(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        // Resize handling
        if (this.isResizing && this.selectedSeating) {
            const deltaX = x - this.resizeStart.x;
            const deltaY = y - this.resizeStart.y;
            
            const minSize = 20;
            
            switch (this.resizeHandle.type) {
                case 'se': // Southeast - bottom right
                    this.selectedSeating.width = Math.max(minSize, this.resizeOriginal.width + deltaX);
                    this.selectedSeating.height = Math.max(minSize, this.resizeOriginal.height + deltaY);
                    break;
                case 'sw': // Southwest - bottom left
                    const newWidth = Math.max(minSize, this.resizeOriginal.width - deltaX);
                    this.selectedSeating.x = this.resizeOriginal.x + (this.resizeOriginal.width - newWidth);
                    this.selectedSeating.width = newWidth;
                    this.selectedSeating.height = Math.max(minSize, this.resizeOriginal.height + deltaY);
                    break;
                case 'ne': // Northeast - top right
                    const newHeight = Math.max(minSize, this.resizeOriginal.height - deltaY);
                    this.selectedSeating.y = this.resizeOriginal.y + (this.resizeOriginal.height - newHeight);
                    this.selectedSeating.width = Math.max(minSize, this.resizeOriginal.width + deltaX);
                    this.selectedSeating.height = newHeight;
                    break;
                case 'nw': // Northwest - top left
                    const newW = Math.max(minSize, this.resizeOriginal.width - deltaX);
                    const newH = Math.max(minSize, this.resizeOriginal.height - deltaY);
                    this.selectedSeating.x = this.resizeOriginal.x + (this.resizeOriginal.width - newW);
                    this.selectedSeating.y = this.resizeOriginal.y + (this.resizeOriginal.height - newH);
                    this.selectedSeating.width = newW;
                    this.selectedSeating.height = newH;
                    break;
                case 'e': // East - right
                    this.selectedSeating.width = Math.max(minSize, this.resizeOriginal.width + deltaX);
                    break;
                case 'w': // West - left
                    const w = Math.max(minSize, this.resizeOriginal.width - deltaX);
                    this.selectedSeating.x = this.resizeOriginal.x + (this.resizeOriginal.width - w);
                    this.selectedSeating.width = w;
                    break;
                case 's': // South - bottom
                    this.selectedSeating.height = Math.max(minSize, this.resizeOriginal.height + deltaY);
                    break;
                case 'n': // North - top
                    const h = Math.max(minSize, this.resizeOriginal.height - deltaY);
                    this.selectedSeating.y = this.resizeOriginal.y + (this.resizeOriginal.height - h);
                    this.selectedSeating.height = h;
                    break;
            }
            
            this.draw();
            return;
        }
        
        // Lasso selection
        if (this.isLassoSelecting) {
            this.lassoEnd = { x, y };
            this.updateLassoSelection();
            this.draw();
            return;
        }
        
        // Update cursor based on position
        if (!this.isDragging && !this.isResizing) {
            this.updateCursor(x, y);
        }
        
        if (this.isDragging && this.selectedSeating) {
            // Calculate new position
            let newX = x - this.dragOffset.x;
            let newY = y - this.dragOffset.y;
            
            // Calculate delta for multi-select
            const deltaX = newX - this.selectedSeating.x;
            const deltaY = newY - this.selectedSeating.y;
            
            // Grid snap
            if (this.snapToGrid) {
                newX = Math.round(newX / this.config.gridSize) * this.config.gridSize;
                newY = Math.round(newY / this.config.gridSize) * this.config.gridSize;
            }
            
            // Object snap - check alignment with other objects
            if (this.snapToObjects && this.selectedSeatings.length === 1) {
                const snapResult = this.getSnapPosition(this.selectedSeating, newX, newY);
                newX = snapResult.x;
                newY = snapResult.y;
                this.alignmentGuides = snapResult.guides;
            } else {
                this.alignmentGuides = [];
            }
            
            // Boundary check - keep within canvas
            newX = Math.max(0, Math.min(newX, this.config.width - this.selectedSeating.width));
            newY = Math.max(0, Math.min(newY, this.config.height - this.selectedSeating.height));
            
            // Store old positions for collision check
            const oldPositions = this.selectedSeatings.map(s => ({ seating: s, x: s.x, y: s.y }));
            
            // Move all selected seatings
            if (this.selectedSeatings.length > 1) {
                const actualDeltaX = newX - this.selectedSeating.x;
                const actualDeltaY = newY - this.selectedSeating.y;
                
                this.selectedSeatings.forEach(seating => {
                    seating.x += actualDeltaX;
                    seating.y += actualDeltaY;
                });
            } else {
                this.selectedSeating.x = newX;
                this.selectedSeating.y = newY;
            }
            
            // Check for collisions
            let hasCollision = false;
            for (let seating of this.selectedSeatings) {
                const collisions = this.checkCollisions(seating);
                if (collisions.length > 0) {
                    hasCollision = true;
                    break;
                }
            }
            
            if (hasCollision) {
                // Revert all positions
                oldPositions.forEach(({ seating, x, y }) => {
                    seating.x = x;
                    seating.y = y;
                });
                
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
    
    onMouseUp() {
        if (this.isDragging) {
            this.isDragging = false;
            this.alignmentGuides = [];
            this.hasUnsavedChanges = true;
            this.saveState(); // Save state after drag operation
        }
        
        if (this.isResizing) {
            this.isResizing = false;
            this.resizeHandle = null;
            this.resizeStart = null;
            this.resizeOriginal = null;
            this.hasUnsavedChanges = true;
            this.saveState();
            this.draw();
        }
        
        if (this.isLassoSelecting) {
            this.isLassoSelecting = false;
            this.lassoStart = null;
            this.lassoEnd = null;
            this.draw();
        }
    }
    
    // Touch event handlers
    onTouchStart(e) {
        e.preventDefault();
        const touch = e.touches[0];
        const rect = this.canvas.getBoundingClientRect();
        const x = touch.clientX - rect.left;
        const y = touch.clientY - rect.top;
        
        // Check resize handle first
        const handle = this.getHandleAt(x, y);
        if (handle && this.selectedSeating) {
            this.isResizing = true;
            this.resizeHandle = handle;
            this.resizeStart = { x, y };
            this.resizeOriginal = {
                x: this.selectedSeating.x,
                y: this.selectedSeating.y,
                width: this.selectedSeating.width,
                height: this.selectedSeating.height
            };
            return;
        }
        
        const seating = this.getSeatingAt(x, y);
        if (seating) {
            this.selectedSeating = seating;
            this.selectedSeatings = [seating];
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
        const touch = e.touches[0];
        const rect = this.canvas.getBoundingClientRect();
        const x = touch.clientX - rect.left;
        const y = touch.clientY - rect.top;
        
        // Handle resize
        if (this.isResizing && this.selectedSeating) {
            const deltaX = x - this.resizeStart.x;
            const deltaY = y - this.resizeStart.y;
            const minSize = 20;
            
            switch (this.resizeHandle.type) {
                case 'se':
                    this.selectedSeating.width = Math.max(minSize, this.resizeOriginal.width + deltaX);
                    this.selectedSeating.height = Math.max(minSize, this.resizeOriginal.height + deltaY);
                    break;
                case 'sw':
                    const newWidth = Math.max(minSize, this.resizeOriginal.width - deltaX);
                    this.selectedSeating.x = this.resizeOriginal.x + (this.resizeOriginal.width - newWidth);
                    this.selectedSeating.width = newWidth;
                    this.selectedSeating.height = Math.max(minSize, this.resizeOriginal.height + deltaY);
                    break;
                case 'ne':
                    const newHeight = Math.max(minSize, this.resizeOriginal.height - deltaY);
                    this.selectedSeating.y = this.resizeOriginal.y + (this.resizeOriginal.height - newHeight);
                    this.selectedSeating.width = Math.max(minSize, this.resizeOriginal.width + deltaX);
                    this.selectedSeating.height = newHeight;
                    break;
                case 'nw':
                    const newW = Math.max(minSize, this.resizeOriginal.width - deltaX);
                    const newH = Math.max(minSize, this.resizeOriginal.height - deltaY);
                    this.selectedSeating.x = this.resizeOriginal.x + (this.resizeOriginal.width - newW);
                    this.selectedSeating.y = this.resizeOriginal.y + (this.resizeOriginal.height - newH);
                    this.selectedSeating.width = newW;
                    this.selectedSeating.height = newH;
                    break;
            }
            this.draw();
            return;
        }
        
        if (this.isDragging && this.selectedSeating) {
            
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
            this.hasUnsavedChanges = true;
            this.saveState();
        }
        if (this.isResizing) {
            this.isResizing = false;
            this.resizeHandle = null;
            this.resizeStart = null;
            this.resizeOriginal = null;
            this.hasUnsavedChanges = true;
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
        
        // Draw alignment guides
        if (this.showAlignmentGuides && this.alignmentGuides.length > 0) {
            this.drawAlignmentGuides();
        }
        
        // Draw lasso selection
        if (this.isLassoSelecting && this.lassoStart && this.lassoEnd) {
            this.drawLasso();
        }
        
        // Draw seatings
        this.seatings.forEach(seating => {
            const isSelected = this.selectedSeatings.includes(seating);
            this.drawSeating(seating, isSelected);
        });
        
        // Draw multi-selection highlight
        if (this.selectedSeatings.length > 1) {
            this.drawMultiSelection();
        } else if (this.selectedSeating) {
            // Draw single selection highlight
            this.drawSelection(this.selectedSeating);
        }
    }
    
    // Draw alignment guides
    drawAlignmentGuides() {
        this.ctx.strokeStyle = '#e74c3c';
        this.ctx.lineWidth = 1;
        this.ctx.setLineDash([5, 5]);
        
        this.alignmentGuides.forEach(guide => {
            this.ctx.beginPath();
            if (guide.type === 'vertical') {
                this.ctx.moveTo(guide.x, guide.y1);
                this.ctx.lineTo(guide.x, guide.y2);
            } else {
                this.ctx.moveTo(guide.x1, guide.y);
                this.ctx.lineTo(guide.x2, guide.y);
            }
            this.ctx.stroke();
        });
        
        this.ctx.setLineDash([]);
    }
    
    // Draw lasso selection
    drawLasso() {
        const minX = Math.min(this.lassoStart.x, this.lassoEnd.x);
        const maxX = Math.max(this.lassoStart.x, this.lassoEnd.x);
        const minY = Math.min(this.lassoStart.y, this.lassoEnd.y);
        const maxY = Math.max(this.lassoStart.y, this.lassoEnd.y);
        
        this.ctx.strokeStyle = '#3498db';
        this.ctx.fillStyle = 'rgba(52, 152, 219, 0.1)';
        this.ctx.lineWidth = 2;
        this.ctx.setLineDash([5, 5]);
        
        this.ctx.fillRect(minX, minY, maxX - minX, maxY - minY);
        this.ctx.strokeRect(minX, minY, maxX - minX, maxY - minY);
        
        this.ctx.setLineDash([]);
    }
    
    // Draw multi-selection highlight
    drawMultiSelection() {
        // Calculate bounding box
        let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
        
        this.selectedSeatings.forEach(seating => {
            minX = Math.min(minX, seating.x);
            minY = Math.min(minY, seating.y);
            maxX = Math.max(maxX, seating.x + seating.width);
            maxY = Math.max(maxY, seating.y + seating.height);
        });
        
        // Draw bounding box
        this.ctx.strokeStyle = '#3498db';
        this.ctx.lineWidth = 2;
        this.ctx.setLineDash([5, 5]);
        this.ctx.strokeRect(minX - 5, minY - 5, maxX - minX + 10, maxY - minY + 10);
        this.ctx.setLineDash([]);
        
        // Draw count badge
        this.ctx.fillStyle = '#3498db';
        this.ctx.fillRect(maxX - 30, minY - 25, 35, 20);
        this.ctx.fillStyle = 'white';
        this.ctx.font = 'bold 12px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText(`${this.selectedSeatings.length}×`, maxX - 12, minY - 15);
    }
    
    drawSeating(seating, isSelected = false) {
        this.ctx.fillStyle = seating.color;
        this.ctx.strokeStyle = isSelected ? '#3498db' : '#2c3e50';
        this.ctx.lineWidth = isSelected ? 3 : 2;
        
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
        // Selection border - red if collision warning, blue otherwise
        this.ctx.strokeStyle = this.showCollisionWarning ? '#e74c3c' : '#3498db';
        this.ctx.lineWidth = this.showCollisionWarning ? 4 : 2;
        this.ctx.strokeRect(seating.x - 2, seating.y - 2, seating.width + 4, seating.height + 4);
        
        // Handle points - larger and more visible
        const handles = this.getSelectionHandles(seating);
        const handleSize = 8;
        
        handles.forEach(handle => {
            // White background
            this.ctx.fillStyle = 'white';
            this.ctx.fillRect(handle.x - handleSize/2, handle.y - handleSize/2, handleSize, handleSize);
            
            // Blue border
            this.ctx.strokeStyle = '#3498db';
            this.ctx.lineWidth = 2;
            this.ctx.strokeRect(handle.x - handleSize/2, handle.y - handleSize/2, handleSize, handleSize);
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
        const handleSize = 8; // Larger hit area
        
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
    
    // Get snap position with alignment guides
    getSnapPosition(seating, newX, newY) {
        const guides = [];
        let snapX = newX;
        let snapY = newY;
        
        // Check alignment with other seatings
        for (let other of this.seatings) {
            if (other === seating) continue;
            
            // Left edge alignment
            if (Math.abs(newX - other.x) < this.snapDistance) {
                snapX = other.x;
                guides.push({ type: 'vertical', x: other.x, y1: Math.min(newY, other.y), y2: Math.max(newY + seating.height, other.y + other.height) });
            }
            
            // Right edge alignment
            if (Math.abs((newX + seating.width) - (other.x + other.width)) < this.snapDistance) {
                snapX = other.x + other.width - seating.width;
                guides.push({ type: 'vertical', x: other.x + other.width, y1: Math.min(newY, other.y), y2: Math.max(newY + seating.height, other.y + other.height) });
            }
            
            // Center horizontal alignment
            const centerX = newX + seating.width / 2;
            const otherCenterX = other.x + other.width / 2;
            if (Math.abs(centerX - otherCenterX) < this.snapDistance) {
                snapX = otherCenterX - seating.width / 2;
                guides.push({ type: 'vertical', x: otherCenterX, y1: Math.min(newY, other.y), y2: Math.max(newY + seating.height, other.y + other.height) });
            }
            
            // Top edge alignment
            if (Math.abs(newY - other.y) < this.snapDistance) {
                snapY = other.y;
                guides.push({ type: 'horizontal', y: other.y, x1: Math.min(newX, other.x), x2: Math.max(newX + seating.width, other.x + other.width) });
            }
            
            // Bottom edge alignment
            if (Math.abs((newY + seating.height) - (other.y + other.height)) < this.snapDistance) {
                snapY = other.y + other.height - seating.height;
                guides.push({ type: 'horizontal', y: other.y + other.height, x1: Math.min(newX, other.x), x2: Math.max(newX + seating.width, other.x + other.width) });
            }
            
            // Center vertical alignment
            const centerY = newY + seating.height / 2;
            const otherCenterY = other.y + other.height / 2;
            if (Math.abs(centerY - otherCenterY) < this.snapDistance) {
                snapY = otherCenterY - seating.height / 2;
                guides.push({ type: 'horizontal', y: otherCenterY, x1: Math.min(newX, other.x), x2: Math.max(newX + seating.width, other.x + other.width) });
            }
        }
        
        return { x: snapX, y: snapY, guides };
    }
    
    // Update lasso selection
    updateLassoSelection() {
        if (!this.lassoStart || !this.lassoEnd) return;
        
        const minX = Math.min(this.lassoStart.x, this.lassoEnd.x);
        const maxX = Math.max(this.lassoStart.x, this.lassoEnd.x);
        const minY = Math.min(this.lassoStart.y, this.lassoEnd.y);
        const maxY = Math.max(this.lassoStart.y, this.lassoEnd.y);
        
        this.selectedSeatings = this.seatings.filter(seating => {
            return seating.x + seating.width > minX &&
                   seating.x < maxX &&
                   seating.y + seating.height > minY &&
                   seating.y < maxY;
        });
        
        if (this.selectedSeatings.length > 0) {
            this.selectedSeating = this.selectedSeatings[0];
        }
    }
    
    // Copy selected seatings
    copySelection() {
        if (this.selectedSeatings.length === 0) return;
        
        this.clipboard = this.selectedSeatings.map(s => ({
            type: s.type,
            width: s.width,
            height: s.height,
            capacity: s.capacity,
            name: s.name,
            color: s.color,
            icon: s.icon
        }));
        
        console.log('📋 Copied', this.clipboard.length, 'seatings');
    }
    
    // Paste seatings from clipboard
    pasteSelection() {
        if (this.clipboard.length === 0) return;
        
        console.log('📋 Pasting', this.clipboard.length, 'seatings');
        
        const offset = 20;
        const newSeatings = [];
        
        this.clipboard.forEach(data => {
            const position = {
                x: (this.selectedSeating?.x || 100) + offset,
                y: (this.selectedSeating?.y || 100) + offset
            };
            
            const seating = this.addSeating(data.type, position, {
                ...data,
                name: `${data.name} (Kopya)`
            });
            
            if (seating) {
                newSeatings.push(seating);
            }
        });
        
        // Select pasted seatings
        this.selectedSeatings = newSeatings;
        this.selectedSeating = newSeatings[0];
        this.draw();
    }
    
    // Auto-save setup
    setupAutoSave() {
        if (!this.autoSaveEnabled) return;
        
        setInterval(() => {
            if (this.hasUnsavedChanges && Date.now() - this.lastSaveTime > this.autoSaveInterval) {
                console.log('💾 Auto-saving...');
                this.triggerAutoSave();
            }
        }, 5000); // Check every 5 seconds
    }
    
    // Trigger auto-save event
    triggerAutoSave() {
        const event = new CustomEvent('visualeditor:autosave', {
            detail: { configuration: this.getConfiguration() }
        });
        document.dispatchEvent(event);
        this.hasUnsavedChanges = false;
        this.lastSaveTime = Date.now();
    }
    
    // Keyboard navigation
    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            // Global shortcuts (work without selection)
            if (e.ctrlKey || e.metaKey) {
                switch(e.key.toLowerCase()) {
                    case 'a':
                        e.preventDefault();
                        this.selectAll();
                        return;
                    case 'c':
                        e.preventDefault();
                        this.copySelection();
                        return;
                    case 'v':
                        e.preventDefault();
                        this.pasteSelection();
                        return;
                    case 'x':
                        e.preventDefault();
                        this.cutSelection();
                        return;
                    case 'g':
                        e.preventDefault();
                        this.groupSelection();
                        return;
                }
            }
            
            if (!this.selectedSeating && this.selectedSeatings.length === 0) return;
            
            const step = e.shiftKey ? this.config.gridSize : 1;
            let moved = false;
            
            // Store old positions for collision check
            const oldPositions = this.selectedSeatings.map(s => ({ seating: s, x: s.x, y: s.y }));
            
            switch(e.key) {
                case 'ArrowUp':
                    this.selectedSeatings.forEach(s => s.y -= step);
                    moved = true;
                    break;
                case 'ArrowDown':
                    this.selectedSeatings.forEach(s => s.y += step);
                    moved = true;
                    break;
                case 'ArrowLeft':
                    this.selectedSeatings.forEach(s => s.x -= step);
                    moved = true;
                    break;
                case 'ArrowRight':
                    this.selectedSeatings.forEach(s => s.x += step);
                    moved = true;
                    break;
                case 'Delete':
                case 'Backspace':
                    e.preventDefault();
                    this.deleteSelection();
                    return;
                case 'Escape':
                    this.selectedSeating = null;
                    this.selectedSeatings = [];
                    this.draw();
                    return;
                case 'd':
                case 'D':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.duplicateSelection();
                        return;
                    }
                    break;
            }
            
            if (moved) {
                e.preventDefault();
                
                // Snap all to grid
                this.selectedSeatings.forEach(s => this.snapToGrid(s));
                
                // Check for collisions after move
                let hasCollision = false;
                for (let seating of this.selectedSeatings) {
                    const collisions = this.checkCollisions(seating);
                    if (collisions.length > 0) {
                        hasCollision = true;
                        break;
                    }
                }
                
                if (hasCollision) {
                    // Revert all positions
                    oldPositions.forEach(({ seating, x, y }) => {
                        seating.x = x;
                        seating.y = y;
                    });
                } else {
                    this.hasUnsavedChanges = true;
                    this.saveState();
                }
                
                this.draw();
            }
        });
    }
    
    // Select all seatings
    selectAll() {
        this.selectedSeatings = [...this.seatings];
        this.selectedSeating = this.seatings[0];
        this.draw();
        console.log('✅ Selected all', this.selectedSeatings.length, 'seatings');
    }
    
    // Delete selected seatings
    deleteSelection() {
        if (this.selectedSeatings.length === 0) return;
        
        const count = this.selectedSeatings.length;
        this.selectedSeatings.forEach(seating => {
            const index = this.seatings.indexOf(seating);
            if (index > -1) {
                this.seatings.splice(index, 1);
            }
        });
        
        this.selectedSeating = null;
        this.selectedSeatings = [];
        this.hasUnsavedChanges = true;
        this.saveState();
        this.draw();
        
        console.log('🗑️ Deleted', count, 'seatings');
    }
    
    // Duplicate selected seatings
    duplicateSelection() {
        if (this.selectedSeatings.length === 0) return;
        
        const newSeatings = [];
        this.selectedSeatings.forEach(seating => {
            const duplicated = this.duplicateSeating(seating);
            if (duplicated) {
                newSeatings.push(duplicated);
            }
        });
        
        this.selectedSeatings = newSeatings;
        this.selectedSeating = newSeatings[0];
        this.draw();
    }
    
    // Cut selection
    cutSelection() {
        this.copySelection();
        this.deleteSelection();
    }
    
    // Group selection (placeholder for future feature)
    groupSelection() {
        if (this.selectedSeatings.length < 2) {
            console.log('⚠️ En az 2 oturum seçmelisiniz');
            return;
        }
        
        console.log('📦 Gruplama özelliği yakında eklenecek');
        // TODO: Implement grouping
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
