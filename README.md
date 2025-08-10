# Shortcut Coach

## Goal
Shortcut Coach is a local desktop tool for Windows that tracks your computer usage in real time and suggests faster keyboard shortcuts for the actions you perform — **live**.

Example: If you right-click and select “Copy,” Shortcut Coach instantly shows a tip:

> Tip: Press `Ctrl+C` next time — it’s faster.

The goal is to help you replace slow, repetitive mouse actions with quicker keyboard shortcuts, improving your workflow over time without invasive tracking.

---

## Key Principles
- **Live feedback**: Suggestions appear within a second of the action.
- **Privacy-first**: No screenshots, no file paths, no clipboard content stored.
- **Local-only**: Runs fully on your machine, using Ollama for AI-generated tips.

---

## Tech Stack
- **Python**: Core logic and event tracking.
- **pynput**: Global keyboard and mouse event hooks.
- **pywin32**: Foreground window tracking, clipboard listener.
- **SQLite**: Storing events and suggestions.
- **win10toast_click**: Native Windows toast notifications.
- **Ollama**: Local LLM (e.g., `llama3.1:8b`) for natural language tips.

---

## Roadmap

### Phase 1 — Basic Tracking
1. **Log mouse clicks**  
   Track left and right clicks with timestamp.  
2. **Log keyboard events**  
   Record all key presses/releases.  
3. **Detect active window changes**  
   Log app name and window title when focus changes.  
4. **Measure session length**  
   Track how long the user stays in each active window.  

### Phase 2 — Input Event Categorization
5. **Classify keys into categories**  
   Identify actions like `COPY_SHORTCUT`, `PASTE_SHORTCUT`, `ALT_TAB`.  
6. **Track right-click + clipboard events**  
   Detect when clipboard changes.  
7. **Detect context-menu Copy**  
   If clipboard changes without `Ctrl+C`, trigger “Use Ctrl+C” tip.  

### Phase 3 — Real-time Feedback
8. **Show toast notifications**  
   Instant suggestions with `win10toast_click`.  
9. **Debounce tips**  
   Avoid spam by limiting frequency per tip/app.  

### Phase 4 — Shortcut Knowledge
10. **Static YAML shortcut library**  
    Store global and per-app shortcuts.  
11. **Match events to known shortcuts**  
    Detect when a faster shortcut exists.  

### Phase 5 — Ollama Integration
12. **Generate tip text with Ollama**  
    Turn event data into personalized, motivational tips.  

### Phase 6 — Polish MVP
13. **System tray menu**  
    Pause/resume tracking, quit app.  
14. **Settings**  
    Toggle tips and adjust cooldowns.  

---

## Example Usage Flow
1. Start Shortcut Coach.  
2. Work normally — it silently tracks mouse/keyboard events.  
3. Right-click → Copy in Chrome.  
4. Shortcut Coach detects the action and shows:  

> Tip: Press `Ctrl+C` next time — it’s faster.  

5. After a week, you’ve adopted multiple new shortcuts.

---

## Privacy Notice
- No screenshots or keystroke content are stored.
- Only key **categories** (like “Copy” or “Paste”) are saved for detection.
- All data stays local unless you manually export it.

---

## Planned Output for Phase 1
```bash
2025-08-10 14:05:23 | Right Click | X=233, Y=412
2025-08-10 14:05:27 | Key Press: ctrl
Active Window: Chrome - YouTube
