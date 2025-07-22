#!/usr/bin/env python3
"""
Setup Volume Scraper Integration with Airflow

This script helps set up the volume scraper integration with the existing Airflow DAG.
"""

import os
import sys
import shutil
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_volume_airflow_integration():
    """Set up volume scraper integration with Airflow"""
    
    print("🚀 Setting up Volume Scraper Integration with Airflow")
    print("=" * 60)
    
    # Step 1: Check if we're in the right directory
    current_dir = Path.cwd()
    airflow_dags_dir = current_dir / "apps" / "backend" / "airflow" / "dags"
    etl_dir = current_dir / "apps" / "backend" / "etl"
    
    print(f"\n📁 Current directory: {current_dir}")
    print(f"📁 Airflow DAGs directory: {airflow_dags_dir}")
    print(f"📁 ETL directory: {etl_dir}")
    
    # Step 2: Verify required files exist
    required_files = [
        "apps/backend/etl/volume_scraper.py",
        "apps/backend/etl/volume_data_integration.py",
        "apps/backend/etl/african_markets_scraper.py",
        "apps/backend/airflow/dags/casablanca_etl_with_volume_dag.py"
    ]
    
    print(f"\n🔍 Checking required files:")
    missing_files = []
    
    for file_path in required_files:
        full_path = current_dir / file_path
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  Missing files: {missing_files}")
        print("Please ensure all volume scraper files are in place before proceeding.")
        return False
    
    # Step 3: Copy ETL files to Airflow DAGs directory for imports
    print(f"\n📋 Step 3: Setting up ETL imports for Airflow")
    
    airflow_etl_dir = airflow_dags_dir / "etl"
    airflow_etl_dir.mkdir(exist_ok=True)
    
    etl_files_to_copy = [
        "volume_scraper.py",
        "volume_data_integration.py",
        "african_markets_scraper.py"
    ]
    
    for file_name in etl_files_to_copy:
        source_file = etl_dir / file_name
        dest_file = airflow_etl_dir / file_name
        
        if source_file.exists():
            shutil.copy2(source_file, dest_file)
            print(f"  ✅ Copied {file_name} to Airflow ETL directory")
        else:
            print(f"  ❌ Source file {file_name} not found")
    
    # Step 4: Create __init__.py for Python package
    init_file = airflow_etl_dir / "__init__.py"
    if not init_file.exists():
        init_file.touch()
        print(f"  ✅ Created __init__.py for ETL package")
    
    # Step 5: Check environment variables
    print(f"\n🔧 Step 4: Checking environment variables")
    
    required_env_vars = [
        "NEXT_PUBLIC_SUPABASE_URL",
        "NEXT_PUBLIC_SUPABASE_ANON_KEY"
    ]
    
    missing_env_vars = []
    for env_var in required_env_vars:
        if os.getenv(env_var):
            print(f"  ✅ {env_var} is set")
        else:
            print(f"  ❌ {env_var} is not set")
            missing_env_vars.append(env_var)
    
    if missing_env_vars:
        print(f"\n⚠️  Missing environment variables: {missing_env_vars}")
        print("Please set these in your Airflow environment or .env file")
    
    # Step 6: Create Airflow configuration
    print(f"\n⚙️  Step 5: Creating Airflow configuration")
    
    # Create a simple test script for Airflow
    test_script = airflow_dags_dir / "test_volume_integration.py"
    
    test_script_content = '''#!/usr/bin/env python3
"""
Test Volume Integration for Airflow

This script tests the volume scraper integration in the Airflow environment.
"""

import sys
import os
from pathlib import Path

# Add ETL directory to path
etl_dir = Path(__file__).parent / "etl"
sys.path.append(str(etl_dir))

def test_volume_scraper_import():
    """Test if volume scraper can be imported"""
    try:
        from volume_scraper import VolumeScraper
        print("✅ VolumeScraper imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import VolumeScraper: {e}")
        return False

def test_volume_integration_import():
    """Test if volume integration can be imported"""
    try:
        from volume_data_integration import VolumeDataIntegration
        print("✅ VolumeDataIntegration imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import VolumeDataIntegration: {e}")
        return False

def test_african_markets_import():
    """Test if African Markets scraper can be imported"""
    try:
        from african_markets_scraper import AfricanMarketsScraper
        print("✅ AfricanMarketsScraper imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import AfricanMarketsScraper: {e}")
        return False

def test_environment_variables():
    """Test if required environment variables are set"""
    required_vars = [
        "NEXT_PUBLIC_SUPABASE_URL",
        "NEXT_PUBLIC_SUPABASE_ANON_KEY"
    ]
    
    all_set = True
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var} is set")
        else:
            print(f"❌ {var} is not set")
            all_set = False
    
    return all_set

if __name__ == "__main__":
    print("🧪 Testing Volume Integration for Airflow")
    print("=" * 50)
    
    tests = [
        test_volume_scraper_import,
        test_volume_integration_import,
        test_african_markets_import,
        test_environment_variables
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Volume integration is ready for Airflow.")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
'''
    
    with open(test_script, 'w') as f:
        f.write(test_script_content)
    
    print(f"  ✅ Created test script: {test_script}")
    
    # Step 7: Create deployment instructions
    print(f"\n📋 Step 6: Creating deployment instructions")
    
    instructions_file = current_dir / "VOLUME_AIRFLOW_DEPLOYMENT.md"
    
    instructions_content = '''# Volume Scraper Airflow Integration - Deployment Guide

## 🎯 Overview

This guide explains how to deploy the volume scraper integration with Airflow for automated daily volume data collection.

## 📁 File Structure

```
apps/backend/airflow/dags/
├── casablanca_etl_with_volume_dag.py    # Enhanced DAG with volume data
├── etl/                                 # ETL modules for Airflow
│   ├── __init__.py
│   ├── volume_scraper.py
│   ├── volume_data_integration.py
│   └── african_markets_scraper.py
└── test_volume_integration.py           # Test script
```

## 🚀 Deployment Steps

### 1. Copy Files to Airflow

```bash
# Copy ETL files to Airflow DAGs directory
cp apps/backend/etl/volume_scraper.py apps/backend/airflow/dags/etl/
cp apps/backend/etl/volume_data_integration.py apps/backend/airflow/dags/etl/
cp apps/backend/etl/african_markets_scraper.py apps/backend/airflow/dags/etl/

# Copy the enhanced DAG
cp apps/backend/airflow/dags/casablanca_etl_with_volume_dag.py /path/to/airflow/dags/
```

### 2. Set Environment Variables

Add these to your Airflow environment or `.env` file:

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here
```

### 3. Install Dependencies

Ensure these Python packages are installed in your Airflow environment:

```bash
pip install supabase aiohttp beautifulsoup4 pandas
```

### 4. Test the Integration

Run the test script to verify everything works:

```bash
cd apps/backend/airflow/dags
python test_volume_integration.py
```

### 5. Deploy to Airflow

1. Copy the DAG file to your Airflow DAGs directory
2. Restart Airflow scheduler
3. Check the Airflow UI for the new DAG: `casablanca_etl_with_volume_pipeline`

## 📊 DAG Tasks

The enhanced DAG includes these new tasks:

1. **refresh_african_markets_with_volume** - Scrapes company data with volume
2. **scrape_volume_data** - Scrapes volume data from multiple sources
3. **integrate_volume_data** - Integrates volume data with database

### Task Dependencies

```
refresh_african_markets_with_volume >> scrape_volume_data >> integrate_volume_data >> 
fetch_ir_reports >> extract_pdf_data >> translate_to_gaap >> store_data >> validate_data >> 
[success_alert, failure_alert]
```

## 🔧 Configuration

### Schedule
- **Frequency**: Daily at 6:00 AM UTC
- **Retries**: 3 attempts with 5-minute delays
- **Max Active Runs**: 1 (prevents overlapping executions)

### Data Sources
- **African Markets** - Primary source for CSE data
- **Wafabourse** - Moroccan financial portal
- **Investing.com** - International financial data

### Output Locations
- **Temporary Files**: `/tmp/volume_data_YYYYMMDD/`
- **Database**: Supabase tables (volume_analysis, market_data)
- **Logs**: Airflow task logs

## 🧪 Testing

### Manual Testing
```bash
# Test volume scraper
cd apps/backend/etl
python volume_scraper.py

# Test volume integration
python volume_data_integration.py

# Test Airflow integration
cd ../airflow/dags
python test_volume_integration.py
```

### Airflow Testing
1. Trigger the DAG manually in Airflow UI
2. Monitor task execution in real-time
3. Check task logs for any errors
4. Verify data is stored in Supabase

## 📈 Monitoring

### Key Metrics to Monitor
- **Volume records collected** per day
- **Data quality score** (should be > 0.9)
- **High volume alerts** generated
- **Database update success rate**
- **Task execution time**

### Alerts
- **Success alerts** sent when pipeline completes
- **Failure alerts** sent when any task fails
- **Volume spike alerts** for unusual trading activity

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure ETL files are copied to Airflow DAGs directory
   - Check Python path configuration

2. **Database Connection Errors**
   - Verify Supabase credentials
   - Check network connectivity

3. **Scraping Failures**
   - Check if source websites are accessible
   - Verify scraping logic hasn't changed

4. **Volume Data Issues**
   - Check if volume data format has changed
   - Verify volume cleaning functions

### Debug Steps

1. **Check Airflow logs** for specific error messages
2. **Run test script** to verify imports and configuration
3. **Test individual components** outside of Airflow
4. **Verify environment variables** are set correctly

## 📞 Support

If you encounter issues:

1. Check the Airflow task logs
2. Run the test script to verify setup
3. Review the troubleshooting section above
4. Check the volume scraper documentation

## 🎉 Success Criteria

The integration is successful when:

- ✅ DAG runs daily without errors
- ✅ Volume data is collected from all sources
- ✅ Data is stored in Supabase database
- ✅ Volume alerts are generated
- ✅ Success notifications are sent
- ✅ Data quality score remains high

---

**Last Updated**: $(date)
**Version**: 1.0
'''
    
    with open(instructions_file, 'w') as f:
        f.write(instructions_content)
    
    print(f"  ✅ Created deployment guide: {instructions_file}")
    
    # Step 8: Summary
    print(f"\n🎉 Volume Airflow Integration Setup Complete!")
    print("=" * 60)
    
    print(f"\n📋 Summary:")
    print(f"  ✅ Enhanced DAG created: casablanca_etl_with_volume_dag.py")
    print(f"  ✅ ETL files copied to Airflow directory")
    print(f"  ✅ Test script created: test_volume_integration.py")
    print(f"  ✅ Deployment guide created: VOLUME_AIRFLOW_DEPLOYMENT.md")
    
    print(f"\n🚀 Next Steps:")
    print(f"  1. Test the integration: python apps/backend/airflow/dags/test_volume_integration.py")
    print(f"  2. Deploy to Airflow: Copy DAG file to your Airflow DAGs directory")
    print(f"  3. Set environment variables in Airflow")
    print(f"  4. Restart Airflow scheduler")
    print(f"  5. Monitor the new DAG: casablanca_etl_with_volume_pipeline")
    
    print(f"\n📖 For detailed instructions, see: VOLUME_AIRFLOW_DEPLOYMENT.md")
    
    return True

if __name__ == "__main__":
    setup_volume_airflow_integration() 