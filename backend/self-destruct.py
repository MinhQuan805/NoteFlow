"""
Cleanup script for NoteFlow backend.
Deletes all generated/cached data to prepare for a fresh start or GitHub push.

Usage:
    python cleanup.py           # Interactive mode (asks for confirmation)
    python cleanup.py --force   # Force delete without confirmation
"""

import os
import shutil
import sys

# Directories and files to delete
CLEANUP_TARGETS = [
    # User uploads
    "uploads",
    
    # RAG data (per-notebook faiss indexes and document pickles)
    "data",
    
    # Local TinyDB database files
    "db",
    
    # Debug outputs (LLM responses for troubleshooting)
    "debug",
    
    # Legacy/global RAG files (if any)
    "faiss_index",
    "documents.pkl",
    
    # Python cache
    "__pycache__",
    "ai/__pycache__",
    "routers/__pycache__",
    "config/__pycache__",
    "schemas/__pycache__",
    "libs/__pycache__",
    
    # Test files
    "test_ingest.txt",
]

def get_size(path):
    """Get size of file or directory in bytes."""
    if os.path.isfile(path):
        return os.path.getsize(path)
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total += os.path.getsize(fp)
    return total

def format_size(size):
    """Format size in human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"

def cleanup(force=False):
    """Delete all cleanup targets."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("=" * 50)
    print("NoteFlow Backend Cleanup Script")
    print("=" * 50)
    print()
    
    # Find existing targets
    existing = []
    for target in CLEANUP_TARGETS:
        if os.path.exists(target):
            size = get_size(target)
            existing.append((target, size))
    
    if not existing:
        print("✓ Nothing to clean up! All directories are already clean.")
        return
    
    print("The following will be DELETED:")
    print("-" * 50)
    total_size = 0
    for target, size in existing:
        icon = "📁" if os.path.isdir(target) else "📄"
        print(f"  {icon} {target:<30} ({format_size(size)})")
        total_size += size
    print("-" * 50)
    print(f"  Total: {format_size(total_size)}")
    print()
    
    if not force:
        response = input("Are you sure you want to delete these? [y/N]: ").strip().lower()
        if response != 'y':
            print("Cancelled.")
            return
    
    print()
    print("Deleting...")
    
    for target, _ in existing:
        try:
            if os.path.isdir(target):
                shutil.rmtree(target)
                print(f"  ✓ Deleted directory: {target}")
            else:
                os.remove(target)
                print(f"  ✓ Deleted file: {target}")
        except Exception as e:
            print(f"  ✗ Failed to delete {target}: {e}")
    
    print()
    print("=" * 50)
    print("✓ Cleanup complete!")

if __name__ == "__main__":
    force = "--force" in sys.argv or "-f" in sys.argv
    cleanup(force=force)
