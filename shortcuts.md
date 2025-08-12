# Keyboard Shortcuts Database

This document contains all the keyboard shortcuts that our shortcut tips system should detect and notify users about.

## Excel

[x] Ctrl + Up key – Jump to the beggining of data region
[x] Ctrl + Space - Select entire column
[x] Shift + Space - Select entire row
[x] Ctrl + Page Up/Page Down - toggle sheets
[ ] Tab – Move one cell right
[ ] Shift + Tab – Move one cell left
[ ] Enter – Move one cell down
[ ] Shift + Enter – Move one cell up
[ ] Ctrl + Home – Go to A1
[ ] Ctrl + End – Go to last used cell
[ ] Ctrl + Page Up / Page Down – Switch between worksheets


## Windows (General OS)

[x] Ctrl + C - Copy
[x] Ctrl + X - Cut
[x] Ctrl + V - Paste
[ ] Ctrl + Z - Undo
[ ] Ctrl + Y - Redo
[ ] Ctrl + A - Select all
[ ] Ctrl + S - Save
[ ] Alt + Tab - Switch between open apps
[ ] Windows + D - Show/hide desktop
[ ] Windows + E - Open File Explorer
[ ] Windows + Shift + S - Screenshot selection (Snipping Tool)
[ ] Windows + L - Lock computer

## Excel

[ ] Ctrl + Arrow Keys - Jump to the edge of data region
[ ] Ctrl + Shift + Arrow Keys - Select to edge of data region
[x] Ctrl + Space - Select entire column
[x] Shift + Space - Select entire row
[ ] Ctrl + Shift + L - Toggle filters
[ ] Ctrl + T - Convert range to table
[ ] Alt + = - AutoSum
[ ] Ctrl + Shift + "+" - Insert row/column
[ ] Ctrl + "-" - Delete row/column
[ ] F2 - Edit selected cell
[ ] Ctrl + 1 - Format cells
[x] Ctrl + Page Up/Page Down - Switch between worksheets
[ ] Ctrl + Z - Undo
[ ] Ctrl + Y - Redo

## VS Code / Cursor

[ ] Ctrl + P - Quick open file
[ ] Ctrl + Shift + P - Command palette
[ ] Ctrl + / - Toggle line comment
[ ] Alt + Up/Down - Move line up/down
[ ] Shift + Alt + Up/Down - Duplicate line
[ ] Ctrl + Shift + K - Delete line
[ ] Ctrl + D - Select next occurrence
[ ] Ctrl + Shift + L - Select all occurrences of selection
[ ] Ctrl + F - Find
[ ] Ctrl + H - Replace
[ ] Ctrl + ` - Toggle terminal
[ ] Ctrl + B - Toggle sidebar
[ ] F12 - Go to definition

## Chrome

[ ] Ctrl + T - Open new tab
[ ] Ctrl + Shift + T - Reopen closed tab
[ ] Ctrl + W - Close current tab
[ ] Ctrl + Tab - Switch to next tab
[ ] Ctrl + Shift + Tab - Switch to previous tab
[ ] Ctrl + N - New window
[ ] Ctrl + Shift + N - New incognito window
[ ] Ctrl + L - Focus address bar
[ ] Alt + D - Focus address bar
[ ] Ctrl + R - Reload page
[ ] Ctrl + Shift + R - Hard reload (ignore cache)
[ ] Ctrl + J - Downloads
[ ] Ctrl + H - History
[ ] F12 - Open DevTools

---

## Testing Notes

- **[ ] Untested**: Shortcut needs to be tested for detection
- **[x] Working**: Shortcut is properly detected and notifications work
- **[x] Failed**: Shortcut detection failed, needs investigation
- **[x] Partial**: Shortcut works in some contexts but not others

## How to Test

1. **Context Menu Actions**: Right-click and select the action (e.g., right-click → Copy)
2. **Direct Shortcut Usage**: Use the keyboard shortcut directly
3. **Check Notifications**: Verify that the appropriate shortcut tip appears
4. **Excel Column/Row Selection**: Click on column headers (A, B, C) or row headers (1, 2, 3) in Excel
5. **Excel Sheet Navigation**: Click on sheet tabs (Sheet1, Sheet2, etc.) to test Ctrl + Page Up/Page Down

## Detection Methods

- **Context Menu Analysis**: OCR analysis of right-click menus
- **Keyboard Monitoring**: Direct detection of key combinations
- **Action Mapping**: Mapping detected actions to relevant shortcuts
- **Excel Header Detection**: Detecting clicks on column/row headers for Ctrl+Space/Shift+Space
- **Excel Sheet Tab Detection**: Detecting clicks on sheet tabs for Ctrl+Page Up/Page Down
