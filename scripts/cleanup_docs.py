#!/usr/bin/env python3
"""
Documentation Cleanup Script
Removes outdated docs and organizes markdown files
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Any
import re
from datetime import datetime

class DocumentationCleaner:
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.archive_dir = self.root_dir / "archive" / "docs"
        self.outdated_files = []
        self.duplicate_files = []
        
    def run_cleanup(self):
        """Run complete documentation cleanup"""
        print("🧹 Starting documentation cleanup...")
        
        # Create archive directory
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Find and process outdated files
        self.find_outdated_docs()
        self.find_duplicate_docs()
        self.archive_outdated_files()
        self.organize_remaining_docs()
        self.create_documentation_index()
        
        print("✅ Documentation cleanup complete!")
    
    def find_outdated_docs(self):
        """Find outdated documentation files"""
        print("🔍 Finding outdated documentation...")
        
        outdated_patterns = [
            r".*TODO.*\.md$",
            r".*OUTDATED.*\.md$",
            r".*DEPRECATED.*\.md$",
            r".*OLD.*\.md$",
            r".*LEGACY.*\.md$"
        ]
        
        # Keywords that indicate outdated content
        outdated_keywords = [
            "TODO", "OUTDATED", "DEPRECATED", "FIXME", "LEGACY", "OLD VERSION",
            "NOT MAINTAINED", "ARCHIVED", "REPLACED BY"
        ]
        
        for md_file in self.root_dir.rglob("*.md"):
            # Check filename patterns
            if any(re.match(pattern, md_file.name, re.IGNORECASE) for pattern in outdated_patterns):
                self.outdated_files.append({
                    "file": md_file,
                    "reason": "filename_pattern",
                    "severity": "high"
                })
                continue
            
            # Check content for outdated keywords
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Count outdated keywords
                keyword_count = sum(1 for keyword in outdated_keywords if keyword.lower() in content.lower())
                
                if keyword_count >= 3:  # If 3 or more outdated keywords found
                    self.outdated_files.append({
                        "file": md_file,
                        "reason": f"contains {keyword_count} outdated keywords",
                        "severity": "medium"
                    })
                elif keyword_count >= 1:
                    self.outdated_files.append({
                        "file": md_file,
                        "reason": f"contains {keyword_count} outdated keywords",
                        "severity": "low"
                    })
                    
            except Exception as e:
                print(f"⚠️  Error reading {md_file}: {e}")
    
    def find_duplicate_docs(self):
        """Find duplicate documentation files"""
        print("🔄 Finding duplicate documentation...")
        
        # Group files by content similarity
        file_groups = {}
        
        for md_file in self.root_dir.rglob("*.md"):
            if md_file in [f["file"] for f in self.outdated_files]:
                continue  # Skip already identified outdated files
                
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Create a simple hash based on content length and first few lines
                content_hash = f"{len(content)}_{content[:100]}"
                
                if content_hash not in file_groups:
                    file_groups[content_hash] = []
                file_groups[content_hash].append(md_file)
                
            except Exception:
                continue
        
        # Find groups with multiple files
        for content_hash, files in file_groups.items():
            if len(files) > 1:
                # Keep the most appropriately named file, archive others
                files.sort(key=lambda f: self._get_file_priority(f))
                keep_file = files[0]
                
                for file in files[1:]:
                    self.outdated_files.append({
                        "file": file,
                        "reason": f"duplicate of {keep_file.name}",
                        "severity": "medium"
                    })
    
    def _get_file_priority(self, file_path: Path) -> int:
        """Get priority score for file (lower is better)"""
        name = file_path.name.lower()
        
        # Prefer files with descriptive names
        if "readme" in name:
            return 0
        elif "guide" in name or "manual" in name:
            return 1
        elif "summary" in name:
            return 2
        elif "todo" in name or "outdated" in name:
            return 10
        else:
            return 5
    
    def archive_outdated_files(self):
        """Archive outdated files"""
        print("📦 Archiving outdated files...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for item in self.outdated_files:
            source_file = item["file"]
            
            # Create archive path
            archive_path = self.archive_dir / f"{timestamp}_{source_file.name}"
            
            try:
                # Move file to archive
                shutil.move(str(source_file), str(archive_path))
                
                # Create metadata file
                metadata_file = archive_path.with_suffix('.metadata.json')
                metadata = {
                    "original_path": str(source_file),
                    "archived_at": timestamp,
                    "reason": item["reason"],
                    "severity": item["severity"]
                }
                
                import json
                with open(metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                print(f"  📦 Archived: {source_file.name}")
                
            except Exception as e:
                print(f"  ❌ Failed to archive {source_file.name}: {e}")
    
    def organize_remaining_docs(self):
        """Organize remaining documentation files"""
        print("📁 Organizing remaining documentation...")
        
        # Create organized structure
        docs_dir = self.root_dir / "docs"
        docs_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (docs_dir / "guides").mkdir(exist_ok=True)
        (docs_dir / "api").mkdir(exist_ok=True)
        (docs_dir / "deployment").mkdir(exist_ok=True)
        (docs_dir / "development").mkdir(exist_ok=True)
        
        # Move remaining markdown files to appropriate directories
        for md_file in self.root_dir.rglob("*.md"):
            if md_file.parent == docs_dir or md_file.parent.parent == docs_dir:
                continue  # Skip files already in docs directory
            
            if md_file.name.lower() in ["readme.md", "index.md"]:
                continue  # Keep root README files
            
            # Determine target directory based on content and name
            target_dir = self._determine_target_directory(md_file)
            
            if target_dir:
                target_path = docs_dir / target_dir / md_file.name
                
                # Handle filename conflicts
                counter = 1
                original_target = target_path
                while target_path.exists():
                    stem = original_target.stem
                    suffix = original_target.suffix
                    target_path = original_target.parent / f"{stem}_{counter}{suffix}"
                    counter += 1
                
                try:
                    shutil.move(str(md_file), str(target_path))
                    print(f"  📁 Moved: {md_file.name} → {target_dir}/")
                except Exception as e:
                    print(f"  ❌ Failed to move {md_file.name}: {e}")
    
    def _determine_target_directory(self, file_path: Path) -> str:
        """Determine target directory for documentation file"""
        name = file_path.name.lower()
        content = ""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
        except Exception:
            pass
        
        # API documentation
        if any(keyword in name or keyword in content for keyword in [
            "api", "endpoint", "route", "rest", "swagger"
        ]):
            return "api"
        
        # Deployment documentation
        if any(keyword in name or keyword in content for keyword in [
            "deploy", "production", "vercel", "supabase", "airflow", "docker"
        ]):
            return "deployment"
        
        # Development documentation
        if any(keyword in name or keyword in content for keyword in [
            "setup", "install", "development", "coding", "implementation"
        ]):
            return "development"
        
        # Guides (default)
        return "guides"
    
    def create_documentation_index(self):
        """Create a comprehensive documentation index"""
        print("📋 Creating documentation index...")
        
        docs_dir = self.root_dir / "docs"
        
        index_content = [
            "# 📚 Documentation Index",
            "",
            "This is the main documentation index for the Casablanca Insights project.",
            "",
            "## 📁 Directory Structure",
            "",
            "```",
            "docs/",
            "├── guides/          # User guides and tutorials",
            "├── api/             # API documentation",
            "├── deployment/      # Deployment and production guides",
            "├── development/     # Development setup and guidelines",
            "└── archive/         # Archived outdated documentation",
            "```",
            "",
            "## 📖 Quick Start",
            "",
            "1. **Setup**: See `development/setup.md` for initial setup",
            "2. **Deployment**: See `deployment/` for production deployment",
            "3. **API**: See `api/` for API documentation",
            "4. **Guides**: See `guides/` for user guides",
            "",
            "## 🔄 Recent Changes",
            "",
            f"- **{datetime.now().strftime('%Y-%m-%d')}**: Documentation cleanup and reorganization",
            "- Moved outdated files to `archive/docs/`",
            "- Organized remaining docs by category",
            "",
            "## 📋 Documentation Status",
            "",
            "| Category | Status | Last Updated |",
            "|----------|--------|--------------|",
        ]
        
        # Generate status table
        categories = ["guides", "api", "deployment", "development"]
        for category in categories:
            category_dir = docs_dir / category
            if category_dir.exists():
                files = list(category_dir.glob("*.md"))
                status = "✅ Complete" if len(files) > 0 else "⚠️  Needs content"
                last_updated = self._get_last_updated(category_dir) if files else "N/A"
                index_content.append(f"| {category.title()} | {status} | {last_updated} |")
            else:
                index_content.append(f"| {category.title()} | ❌ Missing | N/A |")
        
        index_content.extend([
            "",
            "## 🗂️  File Index",
            "",
        ])
        
        # Generate file index
        for category in categories:
            category_dir = docs_dir / category
            if category_dir.exists():
                files = list(category_dir.glob("*.md"))
                if files:
                    index_content.append(f"### {category.title()}")
                    for file in sorted(files):
                        title = self._extract_title(file)
                        index_content.append(f"- [{title}]({category}/{file.name})")
                    index_content.append("")
        
        # Write index file
        with open(docs_dir / "index.md", 'w') as f:
            f.write("\n".join(index_content))
    
    def _get_last_updated(self, directory: Path) -> str:
        """Get last updated date for directory"""
        try:
            files = list(directory.glob("*.md"))
            if files:
                latest_file = max(files, key=lambda f: f.stat().st_mtime)
                timestamp = datetime.fromtimestamp(latest_file.stat().st_mtime)
                return timestamp.strftime("%Y-%m-%d")
        except Exception:
            pass
        return "Unknown"
    
    def _extract_title(self, file_path: Path) -> str:
        """Extract title from markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for first heading
            lines = content.split('\n')
            for line in lines:
                if line.startswith('# '):
                    return line[2:].strip()
                elif line.startswith('## '):
                    return line[3:].strip()
            
            # Fallback to filename
            return file_path.stem.replace('_', ' ').title()
        except Exception:
            return file_path.stem.replace('_', ' ').title()
    
    def generate_cleanup_report(self) -> str:
        """Generate cleanup report"""
        report = [
            "# 🧹 Documentation Cleanup Report",
            "",
            f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 📊 Summary",
            f"- **Files Archived**: {len(self.outdated_files)}",
            f"- **High Priority**: {len([f for f in self.outdated_files if f['severity'] == 'high'])}",
            f"- **Medium Priority**: {len([f for f in self.outdated_files if f['severity'] == 'medium'])}",
            f"- **Low Priority**: {len([f for f in self.outdated_files if f['severity'] == 'low'])}",
            "",
            "## 📦 Archived Files",
            "",
        ]
        
        # Group by severity
        for severity in ['high', 'medium', 'low']:
            files = [f for f in self.outdated_files if f['severity'] == severity]
            if files:
                report.append(f"### {severity.title()} Priority")
                for file in files:
                    report.append(f"- **{file['file'].name}** - {file['reason']}")
                report.append("")
        
        report.extend([
            "## 📁 New Structure",
            "",
            "Documentation has been reorganized into the following structure:",
            "",
            "- `docs/guides/` - User guides and tutorials",
            "- `docs/api/` - API documentation",
            "- `docs/deployment/` - Deployment guides",
            "- `docs/development/` - Development setup",
            "- `archive/docs/` - Archived outdated files",
            "",
            "## 🎯 Next Steps",
            "",
            "1. Review archived files and decide on final disposition",
            "2. Update any broken links in remaining documentation",
            "3. Add missing documentation for uncovered areas",
            "4. Establish documentation maintenance schedule"
        ])
        
        return "\n".join(report)

def main():
    """Main cleanup execution"""
    cleaner = DocumentationCleaner()
    cleaner.run_cleanup()
    
    # Generate and save report
    report = cleaner.generate_cleanup_report()
    
    with open("docs_cleanup_report.md", "w") as f:
        f.write(report)
    
    print("📄 Cleanup report saved to: docs_cleanup_report.md")

if __name__ == "__main__":
    main() 