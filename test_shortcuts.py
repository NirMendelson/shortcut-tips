#!/usr/bin/env python3
"""
Test Script - Demonstrates all the shortcuts that can trigger notifications
Run this to see what shortcuts are available in the database
"""

from server.shortcuts_database import (
    get_all_shortcuts, 
    get_shortcuts_by_category, 
    search_shortcuts,
    get_shortcut_for_action
)

def main():
    print("🎯 SHORTCUT TIPS - Available Shortcuts Database")
    print("=" * 60)
    
    # Get all shortcuts
    all_shortcuts = get_all_shortcuts()
    print(f"\n📊 Total shortcuts available: {len(all_shortcuts)}")
    
    # Show shortcuts by category
    categories = [
        "app_switching", "window_control", "file_operations", 
        "text_editing", "web_browsing", "system_control",
        "task_management", "media_control", "accessibility",
        "virtual_desktops", "screenshots", "language_input",
        "context_menu", "applications", "gaming_multimedia"
    ]
    
    for category in categories:
        shortcuts = get_shortcuts_by_category(category)
        if shortcuts:
            print(f"\n🔹 {category.replace('_', ' ').title()}:")
            for shortcut, description in shortcuts.items():
                print(f"   {shortcut:<20} - {description}")
    
    # Test search functionality
    print(f"\n🔍 SEARCH EXAMPLES:")
    print("=" * 40)
    
    search_terms = ["copy", "window", "browser", "game", "volume"]
    for term in search_terms:
        results = search_shortcuts(term)
        print(f"\nSearching for '{term}':")
        for shortcut, description in results[:3]:  # Show first 3 results
            print(f"   {shortcut:<20} - {description}")
        if len(results) > 3:
            print(f"   ... and {len(results) - 3} more results")
    
    # Test action lookup
    print(f"\n🎯 ACTION LOOKUP EXAMPLES:")
    print("=" * 40)
    
    actions = ["copy", "paste", "delete", "rename", "refresh"]
    for action in actions:
        shortcut, description = get_shortcut_for_action(action)
        if shortcut:
            print(f"   {action:<15} → {shortcut:<20} - {description}")
        else:
            print(f"   {action:<15} → No shortcut found")
    
    print(f"\n✨ These are all the shortcuts that can trigger notifications!")
    print("   When you right-click and select a context menu item,")
    print("   the system will automatically suggest the appropriate keyboard shortcut.")

if __name__ == "__main__":
    main()
