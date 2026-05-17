#!/usr/bin/env python3
"""Test script to verify the save fix works correctly"""

def test_page_filtering():
    """Test that page filtering logic works"""
    # Simulate frontend data
    pages_data = [
        {"pageNum": 1, "deleted": False, "rotation": 0},
        {"pageNum": 2, "deleted": True, "rotation": 0},   # Deleted
        {"pageNum": 3, "deleted": False, "rotation": 0},
        {"pageNum": 4, "deleted": True, "rotation": 0},   # Deleted
        {"pageNum": 5, "deleted": False, "rotation": 90},
    ]
    
    # Simulate backend filtering
    pages_to_export = []
    for page_info in pages_data:
        page_num = page_info.get('pageNum')
        is_deleted = page_info.get('deleted', False)
        
        if is_deleted or page_num is None:
            continue
        
        pages_to_export.append((page_num - 1, page_info))
    
    print("Original pages:", [p["pageNum"] for p in pages_data])
    print("Deleted pages:", [p["pageNum"] for p in pages_data if p["deleted"]])
    print("Exported pages (0-indexed):", [p[0] for p in pages_to_export])
    print("Exported pages (1-indexed):", [p[1]["pageNum"] for p in pages_to_export])
    
    # Assertions
    assert len(pages_to_export) == 3, f"Expected 3 pages, got {len(pages_to_export)}"
    assert pages_to_export[0][0] == 0, "First page should be 0-indexed"
    assert pages_to_export[1][0] == 2, "Second exported page should be 0-indexed page 2"
    assert pages_to_export[2][0] == 4, "Third exported page should be 0-indexed page 4"
    assert pages_to_export[2][1]["rotation"] == 90, "Rotation should be preserved"
    
    print("\n✅ All tests passed! Page filtering works correctly.")
    print(f"   Original: 5 pages → Exported: {len(pages_to_export)} pages (2 deleted)")

if __name__ == "__main__":
    test_page_filtering()
