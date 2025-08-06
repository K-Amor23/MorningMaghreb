#!/usr/bin/env python3
"""
Comprehensive Codebase Audit Script
Checks for linting issues, unused imports, dead code, and outdated documentation
"""

import os
import re
import ast
import subprocess
from pathlib import Path
from typing import List, Dict, Set, Tuple
import json

class CodebaseAuditor:
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.issues = []
        self.dead_code = []
        self.outdated_docs = []
        
    def run_full_audit(self) -> Dict:
        """Run complete codebase audit"""
        print("🔍 Starting comprehensive codebase audit...")
        
        results = {
            "linting_issues": self.check_linting_issues(),
            "unused_imports": self.find_unused_imports(),
            "dead_code": self.find_dead_code(),
            "outdated_docs": self.find_outdated_docs(),
            "todo_items": self.find_todo_items(),
            "duplicate_files": self.find_duplicate_files(),
            "summary": {}
        }
        
        # Generate summary
        results["summary"] = {
            "total_issues": len(results["linting_issues"]) + len(results["unused_imports"]) + len(results["dead_code"]),
            "critical_issues": len([i for i in results["linting_issues"] if i.get("severity") == "error"]),
            "files_with_issues": len(set(i["file"] for i in results["linting_issues"] + results["unused_imports"])),
            "todo_count": len(results["todo_items"]),
            "outdated_docs_count": len(results["outdated_docs"])
        }
        
        return results
    
    def check_linting_issues(self) -> List[Dict]:
        """Check for Python linting issues using flake8"""
        print("📝 Checking for linting issues...")
        issues = []
        
        try:
            # Run flake8 on Python files
            cmd = ["python", "-m", "flake8", "--format=json", "--max-line-length=120"]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.root_dir)
            
            if result.returncode != 0:
                try:
                    flake8_output = json.loads(result.stdout)
                    for file_issues in flake8_output:
                        for issue in file_issues.get("errors", []):
                            issues.append({
                                "file": file_issues["path"],
                                "line": issue["line_number"],
                                "column": issue["column_number"],
                                "code": issue["code"],
                                "text": issue["text"],
                                "severity": "error" if issue["code"].startswith("E") else "warning"
                            })
                except json.JSONDecodeError:
                    # Parse text output if JSON fails
                    for line in result.stdout.split('\n'):
                        if line.strip():
                            parts = line.split(':')
                            if len(parts) >= 4:
                                issues.append({
                                    "file": parts[0],
                                    "line": int(parts[1]),
                                    "column": int(parts[2]),
                                    "code": parts[3].split()[0],
                                    "text": ':'.join(parts[3:]),
                                    "severity": "error"
                                })
        except Exception as e:
            print(f"⚠️  Could not run flake8: {e}")
        
        return issues
    
    def find_unused_imports(self) -> List[Dict]:
        """Find unused imports in Python files"""
        print("🔍 Finding unused imports...")
        unused_imports = []
        
        for py_file in self.root_dir.rglob("*.py"):
            if ".venv" in str(py_file) or "node_modules" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse AST to find imports
                tree = ast.parse(content)
                imports = []
                used_names = set()
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.append(node.module)
                        for alias in node.names:
                            imports.append(alias.name)
                    elif isinstance(node, ast.Name):
                        used_names.add(node.id)
                
                # Check for unused imports (simplified check)
                for imp in imports:
                    if imp not in used_names and not any(imp in name for name in used_names):
                        unused_imports.append({
                            "file": str(py_file),
                            "import": imp,
                            "severity": "warning"
                        })
                        
            except Exception as e:
                print(f"⚠️  Error parsing {py_file}: {e}")
        
        return unused_imports
    
    def find_dead_code(self) -> List[Dict]:
        """Find potentially dead code (unused functions, classes)"""
        print("💀 Finding dead code...")
        dead_code = []
        
        for py_file in self.root_dir.rglob("*.py"):
            if ".venv" in str(py_file) or "node_modules" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                functions = []
                classes = []
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        functions.append(node.name)
                    elif isinstance(node, ast.ClassDef):
                        classes.append(node.name)
                
                # Simple heuristic: functions/classes that might be unused
                # (This is a simplified check - would need more sophisticated analysis)
                for func in functions:
                    if func.startswith('_') and not func.startswith('__'):
                        dead_code.append({
                            "file": str(py_file),
                            "type": "function",
                            "name": func,
                            "severity": "info"
                        })
                        
            except Exception as e:
                print(f"⚠️  Error analyzing {py_file}: {e}")
        
        return dead_code
    
    def find_outdated_docs(self) -> List[Dict]:
        """Find outdated documentation files"""
        print("📚 Finding outdated documentation...")
        outdated_docs = []
        
        # Check for TODO/OUTDATED in markdown files
        for md_file in self.root_dir.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if any(keyword in line.upper() for keyword in ['TODO', 'OUTDATED', 'FIXME', 'DEPRECATED']):
                        outdated_docs.append({
                            "file": str(md_file),
                            "line": i,
                            "content": line.strip(),
                            "severity": "warning"
                        })
                        
            except Exception as e:
                print(f"⚠️  Error reading {md_file}: {e}")
        
        return outdated_docs
    
    def find_todo_items(self) -> List[Dict]:
        """Find all TODO items in the codebase"""
        print("📋 Finding TODO items...")
        todos = []
        
        for file_path in self.root_dir.rglob("*"):
            if file_path.is_file() and not any(skip in str(file_path) for skip in ['.venv', 'node_modules', '.git']):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if 'TODO' in line.upper():
                            todos.append({
                                "file": str(file_path),
                                "line": i,
                                "content": line.strip(),
                                "severity": "info"
                            })
                            
                except Exception:
                    pass  # Skip files that can't be read as text
        
        return todos
    
    def find_duplicate_files(self) -> List[Dict]:
        """Find potential duplicate files"""
        print("🔄 Finding duplicate files...")
        duplicates = []
        
        # Simple file size and name similarity check
        files_by_size = {}
        for file_path in self.root_dir.rglob("*"):
            if file_path.is_file() and not any(skip in str(file_path) for skip in ['.venv', 'node_modules', '.git']):
                try:
                    size = file_path.stat().st_size
                    if size > 100:  # Only check files larger than 100 bytes
                        if size not in files_by_size:
                            files_by_size[size] = []
                        files_by_size[size].append(file_path)
                except Exception:
                    pass
        
        # Check for potential duplicates
        for size, files in files_by_size.items():
            if len(files) > 1:
                # Check for similar names
                for i, file1 in enumerate(files):
                    for file2 in files[i+1:]:
                        name1 = file1.name.lower()
                        name2 = file2.name.lower()
                        
                        # Check for similar names
                        if (name1.replace('_', '').replace('-', '') == 
                            name2.replace('_', '').replace('-', '') or
                            name1 in name2 or name2 in name1):
                            duplicates.append({
                                "file1": str(file1),
                                "file2": str(file2),
                                "size": size,
                                "severity": "warning"
                            })
        
        return duplicates
    
    def generate_report(self, results: Dict) -> str:
        """Generate a comprehensive audit report"""
        report = []
        report.append("# 🔍 Codebase Audit Report")
        report.append("")
        
        # Summary
        summary = results["summary"]
        report.append("## 📊 Summary")
        report.append(f"- **Total Issues**: {summary['total_issues']}")
        report.append(f"- **Critical Issues**: {summary['critical_issues']}")
        report.append(f"- **Files with Issues**: {summary['files_with_issues']}")
        report.append(f"- **TODO Items**: {summary['todo_count']}")
        report.append(f"- **Outdated Docs**: {summary['outdated_docs_count']}")
        report.append("")
        
        # Critical Issues
        critical_issues = [i for i in results["linting_issues"] if i.get("severity") == "error"]
        if critical_issues:
            report.append("## 🚨 Critical Issues")
            for issue in critical_issues[:10]:  # Show first 10
                report.append(f"- **{issue['file']}:{issue['line']}** - {issue['text']}")
            if len(critical_issues) > 10:
                report.append(f"- ... and {len(critical_issues) - 10} more")
            report.append("")
        
        # Unused Imports
        if results["unused_imports"]:
            report.append("## 📦 Unused Imports")
            for imp in results["unused_imports"][:10]:
                report.append(f"- **{imp['file']}** - `{imp['import']}`")
            if len(results["unused_imports"]) > 10:
                report.append(f"- ... and {len(results['unused_imports']) - 10} more")
            report.append("")
        
        # TODO Items
        if results["todo_items"]:
            report.append("## 📋 TODO Items")
            for todo in results["todo_items"][:10]:
                report.append(f"- **{todo['file']}:{todo['line']}** - {todo['content']}")
            if len(results["todo_items"]) > 10:
                report.append(f"- ... and {len(results['todo_items']) - 10} more")
            report.append("")
        
        # Outdated Docs
        if results["outdated_docs"]:
            report.append("## 📚 Outdated Documentation")
            for doc in results["outdated_docs"][:5]:
                report.append(f"- **{doc['file']}:{doc['line']}** - {doc['content']}")
            if len(results["outdated_docs"]) > 5:
                report.append(f"- ... and {len(results['outdated_docs']) - 5} more")
            report.append("")
        
        # Recommendations
        report.append("## 💡 Recommendations")
        if summary['critical_issues'] > 0:
            report.append("1. **Fix critical linting issues first** - These may cause runtime errors")
        if results["unused_imports"]:
            report.append("2. **Remove unused imports** - This will improve code clarity and performance")
        if results["todo_items"]:
            report.append("3. **Address TODO items** - Prioritize based on business impact")
        if results["outdated_docs"]:
            report.append("4. **Update outdated documentation** - Ensure docs reflect current state")
        if results["duplicate_files"]:
            report.append("5. **Review duplicate files** - Consider consolidating similar files")
        
        return "\n".join(report)

def main():
    """Main audit execution"""
    auditor = CodebaseAuditor()
    results = auditor.run_full_audit()
    
    # Generate and save report
    report = auditor.generate_report(results)
    
    with open("audit_report.md", "w") as f:
        f.write(report)
    
    # Save detailed results as JSON
    with open("audit_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("✅ Audit complete!")
    print(f"📄 Report saved to: audit_report.md")
    print(f"📊 Detailed results saved to: audit_results.json")
    
    # Print summary
    summary = results["summary"]
    print(f"\n📊 Summary:")
    print(f"   Total Issues: {summary['total_issues']}")
    print(f"   Critical Issues: {summary['critical_issues']}")
    print(f"   TODO Items: {summary['todo_count']}")

if __name__ == "__main__":
    main() 