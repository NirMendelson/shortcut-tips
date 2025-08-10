# Shortcut Coach - Development Tasks

## Phase 1 — Basic Tracking [IN PROGRESS]

### Core Event Tracking
- [x] Set up project structure with server/ folder
- [x] Initialize SQLite database with basic schema
- [x] Implement global mouse click tracking (left/right clicks)
- [x] Implement global keyboard event tracking (key press/release)
- [x] Implement active window detection and tracking
- [x] Add console logging for real-time event display
- [x] Handle permission errors gracefully
- [x] Create requirements.txt with dependencies

### Testing & Polish
- [ ] Test on Windows 10/11
- [ ] Verify database logging works correctly
- [ ] Test permission handling
- [ ] Add basic error recovery

## Phase 2 — Input Event Categorization

### Event Classification
- [ ] Classify keys into action categories (COPY_SHORTCUT, PASTE_SHORTCUT, etc.)
- [ ] Implement clipboard change detection
- [ ] Detect context-menu actions (right-click + clipboard)
- [ ] Add event pattern recognition

### Database Schema Updates
- [ ] Extend events table with action categories
- [ ] Add patterns table for detected sequences

## Phase 3 — Real-time Feedback

### Toast Notifications
- [ ] Implement win10toast_click integration
- [ ] Add tip debouncing system
- [ ] Create tip display logic

## Phase 4 — Shortcut Knowledge

### Shortcut Library
- [ ] Create YAML shortcut definitions
- [ ] Implement shortcut matching engine
- [ ] Add per-application shortcuts

## Phase 5 — Ollama Integration

### AI-Powered Tips
- [ ] Set up Ollama with llama3.1:8b
- [ ] Implement tip generation from event data
- [ ] Add natural language tip formatting

## Phase 6 — Polish MVP

### User Experience
- [ ] System tray integration
- [ ] Settings configuration
- [ ] Pause/resume functionality
- [ ] User preferences

### Final Testing
- [ ] End-to-end testing
- [ ] Performance optimization
- [ ] User documentation 