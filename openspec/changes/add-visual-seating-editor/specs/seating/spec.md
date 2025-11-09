# Visual Seating Editor Specification

## ADDED Requirements

### Requirement: Drag-and-Drop Seating Layout
The system SHALL provide a visual drag-and-drop editor for creating and managing event seating layouts.

**Core Features:**
- Drag seats to position them on canvas
- Snap-to-grid for alignment
- Real-time position updates
- Visual feedback during drag
- Touch support for tablets

#### Scenario: Add new seat to layout
- **GIVEN** admin is in seating editor
- **WHEN** admin clicks "Add Seat" and selects type "Table-4"
- **THEN** new seat appears on canvas
- **AND** seat can be dragged to desired position
- **AND** position is saved to database

#### Scenario: Drag seat to new position
- **GIVEN** seat exists on canvas at position (100, 100)
- **WHEN** admin drags seat to position (200, 250)
- **THEN** seat moves smoothly to new position
- **AND** seat snaps to nearest grid point (200, 250)
- **AND** new position is saved to database

#### Scenario: Prevent seat overlap
- **GIVEN** seat A is at position (100, 100)
- **WHEN** admin tries to drag seat B to overlap seat A
- **THEN** seat B is prevented from overlapping
- **AND** visual warning is shown
- **AND** seat B snaps to nearest non-overlapping position

#### Scenario: Delete seat
- **GIVEN** seat is selected on canvas
- **WHEN** admin presses Delete key or clicks delete button
- **THEN** seat is removed from canvas
- **AND** seat is deleted from database
- **AND** confirmation is requested if seat has reservations

### Requirement: Grid System
The system SHALL provide a grid-based layout system for precise seat alignment.

**Grid Properties:**
- Configurable grid size (default 50px)
- Visible grid lines (toggle on/off)
- Snap-to-grid during drag
- Coordinate display

#### Scenario: Enable grid lines
- **GIVEN** editor is open with grid lines hidden
- **WHEN** admin toggles "Show Grid" option
- **THEN** grid lines appear on canvas
- **AND** grid spacing matches configured size

#### Scenario: Snap seat to grid
- **GIVEN** grid size is 50px
- **WHEN** admin drags seat to position (123, 187)
- **THEN** seat automatically snaps to (100, 200)
- **AND** final position aligns with grid

### Requirement: Zoom and Pan Controls
The system SHALL provide zoom and pan capabilities for working with large layouts.

**Zoom Levels**: 25%, 50%, 75%, 100%, 125%, 150%, 200%
**Pan**: Space + drag or two-finger drag (touch)

#### Scenario: Zoom in with button
- **GIVEN** canvas is at 100% zoom
- **WHEN** admin clicks zoom in (+) button
- **THEN** canvas zooms to 125%
- **AND** content remains centered

#### Scenario: Zoom with mouse wheel
- **GIVEN** cursor is over canvas
- **WHEN** admin scrolls mouse wheel up
- **THEN** canvas zooms in at cursor position
- **AND** zoom level increases by 25%

#### Scenario: Pan canvas
- **GIVEN** canvas is zoomed in
- **WHEN** admin holds Space key and drags mouse
- **THEN** canvas pans in drag direction
- **AND** content scrolls smoothly

#### Scenario: Reset view
- **GIVEN** canvas is zoomed and panned
- **WHEN** admin clicks "Reset View" button
- **THEN** canvas returns to 100% zoom
- **AND** canvas is centered

### Requirement: Undo/Redo Functionality
The system SHALL provide undo/redo functionality for editor actions.

**Tracked Actions:**
- Add seat
- Delete seat
- Move seat
- Edit seat properties
- Bulk operations

**History Limit**: 20 actions

#### Scenario: Undo seat move
- **GIVEN** seat was moved from (100, 100) to (200, 200)
- **WHEN** admin clicks Undo or presses Ctrl+Z
- **THEN** seat returns to position (100, 100)
- **AND** database is updated

#### Scenario: Redo seat move
- **GIVEN** seat move was undone
- **WHEN** admin clicks Redo or presses Ctrl+Y
- **THEN** seat moves back to (200, 200)
- **AND** database is updated

#### Scenario: History limit
- **GIVEN** 25 actions have been performed
- **WHEN** admin tries to undo beyond 20 actions
- **THEN** only last 20 actions can be undone
- **AND** older actions are discarded

### Requirement: Auto-Numbering
The system SHALL provide automatic seat numbering based on layout position.

**Numbering Patterns:**
- Left-to-right, top-to-bottom
- Configurable prefix (M, T, VIP)
- Sequential numbers (M1, M2, M3...)

#### Scenario: Auto-number seats
- **GIVEN** 10 seats are on canvas without numbers
- **WHEN** admin clicks "Auto-Number" with prefix "M"
- **THEN** seats are numbered M1 through M10
- **AND** numbering follows left-to-right, top-to-bottom
- **AND** numbers are saved to database

#### Scenario: Preview before applying
- **GIVEN** auto-number is initiated
- **WHEN** numbering algorithm runs
- **THEN** preview shows proposed numbers on canvas
- **AND** admin can confirm or cancel
- **AND** numbers only save on confirmation

### Requirement: Stage Position Configuration
The system SHALL allow configuration of stage position in relation to seating.

**Positions**: Top, Bottom, Left, Right

#### Scenario: Set stage position
- **GIVEN** editor is open
- **WHEN** admin selects "Stage Position: Top"
- **THEN** stage visual appears at top of canvas
- **AND** stage position is saved in layout config

#### Scenario: Stage visual representation
- **GIVEN** stage position is "Top"
- **WHEN** canvas is rendered
- **THEN** stage area is highlighted at top
- **AND** label "STAGE" is displayed

### Requirement: Seat Properties Editor
The system SHALL allow editing of individual seat properties.

**Editable Properties:**
- Seat number
- Seat type
- Capacity
- Price
- Color

#### Scenario: Edit seat properties
- **GIVEN** seat is selected on canvas
- **WHEN** admin clicks on seat
- **THEN** properties panel opens
- **AND** shows current values (number, type, capacity, price, color)

#### Scenario: Change seat color
- **GIVEN** properties panel is open for seat
- **WHEN** admin selects new color from color picker
- **THEN** seat color changes immediately on canvas
- **AND** color is saved to database

#### Scenario: Change seat capacity
- **GIVEN** properties panel shows capacity as 4
- **WHEN** admin changes capacity to 6
- **THEN** capacity is updated
- **AND** total event capacity recalculates

### Requirement: Template Integration
The system SHALL integrate with seating layout templates for reusability.

#### Scenario: Save layout as template
- **GIVEN** seating layout is complete
- **WHEN** admin clicks "Save as Template"
- **AND** enters template name "Wedding Hall Standard"
- **THEN** current layout is saved to seating_layout_templates
- **AND** template appears in template list

#### Scenario: Load template
- **GIVEN** admin is creating new event
- **WHEN** admin selects template "Wedding Hall Standard"
- **THEN** all seats from template are loaded onto canvas
- **AND** seat positions match template
- **AND** admin can modify as needed

### Requirement: Real-time Validation
The system SHALL validate seating layout in real-time.

**Validations:**
- Seats within canvas bounds
- No seat overlaps
- Minimum spacing between seats
- Maximum seats per event

#### Scenario: Seat out of bounds
- **GIVEN** canvas size is 1200x800
- **WHEN** admin tries to drag seat to position (1300, 900)
- **THEN** seat is constrained to canvas bounds
- **AND** warning message is shown

#### Scenario: Maximum seats exceeded
- **GIVEN** event has 500 seats (maximum limit)
- **WHEN** admin tries to add 501st seat
- **THEN** operation is blocked
- **AND** error message explains limit

### Requirement: Mobile and Touch Support
The system SHALL support touch-based interaction for tablets.

#### Scenario: Touch drag on tablet
- **GIVEN** admin opens editor on iPad
- **WHEN** admin touches and drags seat
- **THEN** seat moves smoothly with finger
- **AND** seat snaps to grid on release

#### Scenario: Pinch to zoom
- **GIVEN** admin is on touch device
- **WHEN** admin performs pinch gesture
- **THEN** canvas zooms in/out
- **AND** zoom centers on pinch point
