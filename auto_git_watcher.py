#!/usr/bin/env python3
"""
LevlStudio Auto Git Watcher
Automatically commits and pushes changes when files are modified
"""

import os
import time
import subprocess
from datetime import datetime
from pathlib import Path

class GitAutoWatcher:
    def __init__(self, repo_path="/Volumes/Jul_23_2025/LevlStudio_Project"):
        self.repo_path = Path(repo_path)
        self.last_check = time.time()
        self.check_interval = 30  # Check every 30 seconds
        
    def get_git_status(self):
        """Get current git status"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"], 
                cwd=self.repo_path, 
                capture_output=True, 
                text=True
            )
            return result.stdout.strip()
        except Exception as e:
            print(f"Error checking git status: {e}")
            return ""
    
    def commit_and_push_changes(self):
        """Commit and push any changes"""
        try:
            # Add all changes
            subprocess.run(["git", "add", "."], cwd=self.repo_path, check=True)
            
            # Create commit message with timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_msg = f"""Auto-commit: LevlStudio updates - {timestamp}

🤖 Automated commit via file watcher

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"""
            
            # Commit changes
            subprocess.run(
                ["git", "commit", "-m", commit_msg], 
                cwd=self.repo_path, 
                check=True
            )
            
            print(f"✅ Auto-committed changes at {timestamp}")
            
            # Push handled by post-commit hook
            return True
            
        except subprocess.CalledProcessError as e:
            if "nothing to commit" in str(e):
                return False
            print(f"Error committing changes: {e}")
            return False
    
    def watch(self):
        """Main watch loop"""
        print("🔍 LevlStudio Auto Git Watcher Started")
        print(f"📁 Watching: {self.repo_path}")
        print(f"⏱️  Check interval: {self.check_interval}s")
        print("🔄 Press Ctrl+C to stop")
        
        try:
            while True:
                status = self.get_git_status()
                
                if status:  # If there are changes
                    print(f"📝 Changes detected:")
                    for line in status.split('\n'):
                        if line.strip():
                            print(f"   {line}")
                    
                    if self.commit_and_push_changes():
                        print("🚀 Changes pushed to GitHub!")
                    
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Auto-watcher stopped")

def main():
    watcher = GitAutoWatcher()
    watcher.watch()

if __name__ == "__main__":
    main()