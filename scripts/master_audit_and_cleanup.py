#!/usr/bin/env python3
"""
Master Audit and Cleanup Script
Runs comprehensive audit and cleanup tasks in sequence
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import json

class MasterAuditAndCleanup:
    def __init__(self):
        self.root_dir = Path(".")
        self.scripts_dir = self.root_dir / "scripts"
        self.reports_dir = self.root_dir / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = {
            "timestamp": self.timestamp,
            "steps": [],
            "summary": {}
        }
    
    def run_full_audit_and_cleanup(self):
        """Run complete audit and cleanup process"""
        print("🚀 Starting Master Audit and Cleanup Process")
        print("=" * 60)
        
        # Step 1: Codebase Audit
        self.run_codebase_audit()
        
        # Step 2: Documentation Cleanup
        self.run_documentation_cleanup()
        
        # Step 3: Scraper Consolidation
        self.run_scraper_consolidation()
        
        # Step 4: Generate Master Report
        self.generate_master_report()
        
        print("=" * 60)
        print("✅ Master Audit and Cleanup Complete!")
        print(f"📄 Master report saved to: reports/master_audit_report_{self.timestamp}.md")
    
    def run_codebase_audit(self):
        """Run codebase audit"""
        print("\n🔍 Step 1: Running Codebase Audit")
        print("-" * 40)
        
        try:
            # Run the audit script
            audit_script = self.scripts_dir / "audit_codebase.py"
            if audit_script.exists():
                result = subprocess.run(
                    [sys.executable, str(audit_script)],
                    capture_output=True,
                    text=True,
                    cwd=self.root_dir
                )
                
                if result.returncode == 0:
                    print("✅ Codebase audit completed successfully")
                    
                    # Check for generated files
                    audit_report = self.root_dir / "audit_report.md"
                    audit_results = self.root_dir / "audit_results.json"
                    
                    if audit_report.exists():
                        # Move to reports directory
                        new_report_path = self.reports_dir / f"codebase_audit_{self.timestamp}.md"
                        audit_report.rename(new_report_path)
                        print(f"📄 Audit report saved to: {new_report_path}")
                    
                    if audit_results.exists():
                        # Move to reports directory
                        new_results_path = self.reports_dir / f"codebase_audit_results_{self.timestamp}.json"
                        audit_results.rename(new_results_path)
                        print(f"📊 Audit results saved to: {new_results_path}")
                    
                    self.results["steps"].append({
                        "name": "codebase_audit",
                        "status": "success",
                        "output": result.stdout,
                        "error": result.stderr
                    })
                else:
                    print(f"❌ Codebase audit failed: {result.stderr}")
                    self.results["steps"].append({
                        "name": "codebase_audit",
                        "status": "failed",
                        "output": result.stdout,
                        "error": result.stderr
                    })
            else:
                print("⚠️  Audit script not found, skipping codebase audit")
                self.results["steps"].append({
                    "name": "codebase_audit",
                    "status": "skipped",
                    "reason": "script not found"
                })
                
        except Exception as e:
            print(f"❌ Error running codebase audit: {e}")
            self.results["steps"].append({
                "name": "codebase_audit",
                "status": "error",
                "error": str(e)
            })
    
    def run_documentation_cleanup(self):
        """Run documentation cleanup"""
        print("\n🧹 Step 2: Running Documentation Cleanup")
        print("-" * 40)
        
        try:
            # Run the cleanup script
            cleanup_script = self.scripts_dir / "cleanup_docs.py"
            if cleanup_script.exists():
                result = subprocess.run(
                    [sys.executable, str(cleanup_script)],
                    capture_output=True,
                    text=True,
                    cwd=self.root_dir
                )
                
                if result.returncode == 0:
                    print("✅ Documentation cleanup completed successfully")
                    
                    # Check for generated files
                    cleanup_report = self.root_dir / "docs_cleanup_report.md"
                    if cleanup_report.exists():
                        # Move to reports directory
                        new_report_path = self.reports_dir / f"docs_cleanup_{self.timestamp}.md"
                        cleanup_report.rename(new_report_path)
                        print(f"📄 Cleanup report saved to: {new_report_path}")
                    
                    self.results["steps"].append({
                        "name": "documentation_cleanup",
                        "status": "success",
                        "output": result.stdout,
                        "error": result.stderr
                    })
                else:
                    print(f"❌ Documentation cleanup failed: {result.stderr}")
                    self.results["steps"].append({
                        "name": "documentation_cleanup",
                        "status": "failed",
                        "output": result.stdout,
                        "error": result.stderr
                    })
            else:
                print("⚠️  Cleanup script not found, skipping documentation cleanup")
                self.results["steps"].append({
                    "name": "documentation_cleanup",
                    "status": "skipped",
                    "reason": "script not found"
                })
                
        except Exception as e:
            print(f"❌ Error running documentation cleanup: {e}")
            self.results["steps"].append({
                "name": "documentation_cleanup",
                "status": "error",
                "error": str(e)
            })
    
    def run_scraper_consolidation(self):
        """Run scraper consolidation"""
        print("\n🏗️  Step 3: Running Scraper Consolidation")
        print("-" * 40)
        
        try:
            # Run the consolidation script
            consolidation_script = self.scripts_dir / "consolidate_scrapers.py"
            if consolidation_script.exists():
                result = subprocess.run(
                    [sys.executable, str(consolidation_script)],
                    capture_output=True,
                    text=True,
                    cwd=self.root_dir
                )
                
                if result.returncode == 0:
                    print("✅ Scraper consolidation completed successfully")
                    
                    # Check if scrapers directory was created
                    scrapers_dir = self.root_dir / "scrapers"
                    if scrapers_dir.exists():
                        print(f"📁 New scrapers structure created at: {scrapers_dir}")
                        
                        # Count files in new structure
                        scraper_files = list(scrapers_dir.rglob("*.py"))
                        print(f"📦 Created {len(scraper_files)} scraper files")
                    
                    self.results["steps"].append({
                        "name": "scraper_consolidation",
                        "status": "success",
                        "output": result.stdout,
                        "error": result.stderr
                    })
                else:
                    print(f"❌ Scraper consolidation failed: {result.stderr}")
                    self.results["steps"].append({
                        "name": "scraper_consolidation",
                        "status": "failed",
                        "output": result.stdout,
                        "error": result.stderr
                    })
            else:
                print("⚠️  Consolidation script not found, skipping scraper consolidation")
                self.results["steps"].append({
                    "name": "scraper_consolidation",
                    "status": "skipped",
                    "reason": "script not found"
                })
                
        except Exception as e:
            print(f"❌ Error running scraper consolidation: {e}")
            self.results["steps"].append({
                "name": "scraper_consolidation",
                "status": "error",
                "error": str(e)
            })
    
    def generate_master_report(self):
        """Generate master report"""
        print("\n📋 Step 4: Generating Master Report")
        print("-" * 40)
        
        # Calculate summary statistics
        successful_steps = [s for s in self.results["steps"] if s["status"] == "success"]
        failed_steps = [s for s in self.results["steps"] if s["status"] == "failed"]
        skipped_steps = [s for s in self.results["steps"] if s["status"] == "skipped"]
        
        self.results["summary"] = {
            "total_steps": len(self.results["steps"]),
            "successful": len(successful_steps),
            "failed": len(failed_steps),
            "skipped": len(skipped_steps),
            "success_rate": len(successful_steps) / len(self.results["steps"]) * 100 if self.results["steps"] else 0
        }
        
        # Generate report content
        report_content = [
            "# 🚀 Master Audit and Cleanup Report",
            "",
            f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Timestamp**: {self.timestamp}",
            "",
            "## 📊 Summary",
            "",
            f"- **Total Steps**: {self.results['summary']['total_steps']}",
            f"- **Successful**: {self.results['summary']['successful']}",
            f"- **Failed**: {self.results['summary']['failed']}",
            f"- **Skipped**: {self.results['summary']['skipped']}",
            f"- **Success Rate**: {self.results['summary']['success_rate']:.1f}%",
            "",
            "## 📋 Step Details",
            "",
        ]
        
        # Add step details
        for step in self.results["steps"]:
            status_emoji = {
                "success": "✅",
                "failed": "❌",
                "skipped": "⚠️",
                "error": "💥"
            }.get(step["status"], "❓")
            
            report_content.append(f"### {status_emoji} {step['name'].replace('_', ' ').title()}")
            report_content.append(f"- **Status**: {step['status']}")
            
            if "reason" in step:
                report_content.append(f"- **Reason**: {step['reason']}")
            
            if "error" in step and step["error"]:
                report_content.append(f"- **Error**: {step['error']}")
            
            report_content.append("")
        
        # Add recommendations
        report_content.extend([
            "## 💡 Recommendations",
            "",
        ])
        
        if failed_steps:
            report_content.append("### 🚨 Critical Issues")
            report_content.append("The following steps failed and need immediate attention:")
            for step in failed_steps:
                report_content.append(f"- **{step['name']}**: {step.get('error', 'Unknown error')}")
            report_content.append("")
        
        if successful_steps:
            report_content.append("### ✅ Successful Improvements")
            report_content.append("The following improvements were successfully implemented:")
            for step in successful_steps:
                if step["name"] == "codebase_audit":
                    report_content.append("- **Code Quality**: Identified and documented code issues")
                elif step["name"] == "documentation_cleanup":
                    report_content.append("- **Documentation**: Cleaned up outdated docs and organized structure")
                elif step["name"] == "scraper_consolidation":
                    report_content.append("- **Scrapers**: Consolidated scrapers into modular structure")
            report_content.append("")
        
        # Add next steps
        report_content.extend([
            "## 🎯 Next Steps",
            "",
            "1. **Review Failed Steps**: Address any failed steps before proceeding",
            "2. **Code Quality**: Fix critical linting issues identified in the audit",
            "3. **Documentation**: Review archived files and update any broken links",
            "4. **Scrapers**: Test the new scraper structure and update any dependencies",
            "5. **Continuous Improvement**: Set up automated checks to prevent regressions",
            "",
            "## 📁 Generated Files",
            "",
            "The following files were generated during this process:",
            "",
        ])
        
        # List generated files
        for file_path in self.reports_dir.glob(f"*{self.timestamp}*"):
            report_content.append(f"- `{file_path.relative_to(self.root_dir)}`")
        
        # Add new directory structures
        new_structures = []
        if (self.root_dir / "scrapers").exists():
            new_structures.append("- `scrapers/` - New modular scraper structure")
        if (self.root_dir / "docs").exists():
            new_structures.append("- `docs/` - Organized documentation structure")
        if (self.root_dir / "archive").exists():
            new_structures.append("- `archive/docs/` - Archived outdated documentation")
        
        if new_structures:
            report_content.extend([
                "",
                "## 🏗️  New Structures",
                "",
                "The following new directory structures were created:",
                ""
            ])
            report_content.extend(new_structures)
        
        # Write report
        report_file = self.reports_dir / f"master_audit_report_{self.timestamp}.md"
        with open(report_file, 'w') as f:
            f.write("\n".join(report_content))
        
        # Save detailed results as JSON
        results_file = self.reports_dir / f"master_audit_results_{self.timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"📄 Master report saved to: {report_file}")
        print(f"📊 Detailed results saved to: {results_file}")
    
    def print_summary(self):
        """Print summary of results"""
        print("\n" + "=" * 60)
        print("📊 FINAL SUMMARY")
        print("=" * 60)
        
        summary = self.results["summary"]
        print(f"✅ Successful Steps: {summary['successful']}")
        print(f"❌ Failed Steps: {summary['failed']}")
        print(f"⚠️  Skipped Steps: {summary['skipped']}")
        print(f"📈 Success Rate: {summary['success_rate']:.1f}%")
        
        if summary['failed'] > 0:
            print("\n🚨 CRITICAL: Some steps failed. Please review the report and address issues.")
        elif summary['successful'] == summary['total_steps']:
            print("\n🎉 SUCCESS: All steps completed successfully!")
        else:
            print("\n⚠️  WARNING: Some steps were skipped. Review the report for details.")

def main():
    """Main execution"""
    auditor = MasterAuditAndCleanup()
    auditor.run_full_audit_and_cleanup()
    auditor.print_summary()

if __name__ == "__main__":
    main() 