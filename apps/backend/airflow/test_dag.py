#!/usr/bin/env python3
"""
Test script for Casablanca ETL DAG

This script validates the DAG structure and configuration without running the actual pipeline.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent.parent
sys.path.append(str(backend_path))

def test_dag_import():
    """Test if the DAG can be imported successfully"""
    try:
        # Import the DAG
        from dags.casablanca_etl_dag import dag
        
        print("✅ DAG imported successfully")
        print(f"   DAG ID: {dag.dag_id}")
        print(f"   Schedule: {dag.schedule_interval}")
        print(f"   Start Date: {dag.start_date}")
        print(f"   Tags: {dag.tags}")
        
        # Check tasks
        tasks = dag.tasks
        print(f"   Number of tasks: {len(tasks)}")
        
        # List all tasks
        print("   Tasks:")
        for task in tasks:
            print(f"     - {task.task_id} ({task.__class__.__name__})")
        
        return True
        
    except Exception as e:
        print(f"❌ DAG import failed: {e}")
        return False

def test_dag_structure():
    """Test DAG structure and dependencies"""
    try:
        from dags.casablanca_etl_dag import dag
        
        # Check for required tasks
        required_tasks = [
            'fetch_ir_reports',
            'extract_pdf_data', 
            'translate_to_gaap',
            'store_data',
            'validate_data',
            'send_success_alert',
            'send_failure_alert'
        ]
        
        task_ids = [task.task_id for task in dag.tasks]
        
        print("🔍 Checking DAG structure...")
        
        # Check if all required tasks exist
        missing_tasks = [task for task in required_tasks if task not in task_ids]
        if missing_tasks:
            print(f"❌ Missing tasks: {missing_tasks}")
            return False
        else:
            print("✅ All required tasks present")
        
        # Check task dependencies
        print("🔍 Checking task dependencies...")
        
        # Expected dependencies
        expected_deps = [
            ('fetch_ir_reports', 'extract_pdf_data'),
            ('extract_pdf_data', 'translate_to_gaap'),
            ('translate_to_gaap', 'store_data'),
            ('store_data', 'validate_data'),
            ('validate_data', 'send_success_alert')
        ]
        
        for upstream, downstream in expected_deps:
            upstream_task = dag.get_task(upstream)
            downstream_task = dag.get_task(downstream)
            
            if downstream_task in upstream_task.downstream_list:
                print(f"✅ {upstream} → {downstream}")
            else:
                print(f"❌ Missing dependency: {upstream} → {downstream}")
                return False
        
        # Check failure alert dependencies
        failure_task = dag.get_task('send_failure_alert')
        if failure_task.trigger_rule == 'one_failed':
            print("✅ Failure alert trigger rule correct")
        else:
            print(f"❌ Failure alert trigger rule incorrect: {failure_task.trigger_rule}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ DAG structure test failed: {e}")
        return False

def test_imports():
    """Test if all required modules can be imported"""
    try:
        print("🔍 Testing imports...")
        
        # Test ETL imports
        from etl.etl_orchestrator import ETLOrchestrator
        from etl.fetch_ir_reports import IRReportFetcher
        from etl.extract_from_pdf import PDFExtractor
        from etl.translate_labels import LabelTranslator
        from storage.local_fs import LocalFileStorage
        from models.financials import ETLJob, JobType, JobStatus
        
        print("✅ All ETL modules imported successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during import: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Casablanca ETL DAG")
    print("=" * 40)
    
    # Run tests
    tests = [
        ("Import Test", test_imports),
        ("DAG Import Test", test_dag_import),
        ("DAG Structure Test", test_dag_structure)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Results Summary")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! DAG is ready for deployment.")
        return 0
    else:
        print("⚠️  Some tests failed. Please fix issues before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 