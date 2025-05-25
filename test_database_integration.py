#!/usr/bin/env python3
"""
Test script for database integration
Tests the new database functionality with existing collection Excel files
"""

import sys
from pathlib import Path
import logging

# Add utils to path
sys.path.append(str(Path(__file__).parent))

from utils.database_utils import TumorboardDatabase, sync_all_collection_files
from utils.data_analysis_utils import TumorboardAnalyzer, generate_full_analysis_report
from utils.excel_export_utils import sync_all_collections_to_database

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_database_creation():
    """Test database creation and initialization"""
    print("=== Testing Database Creation ===")
    try:
        db = TumorboardDatabase()
        print(f"✓ Database created at: {db.db_path}")
        
        stats = db.get_statistics()
        if stats is not None:
            print(f"✓ Database statistics retrieved")
            print(f"  - Entities: {stats['total_entities']}")
            print(f"  - Sessions: {stats['total_sessions']}")
            print(f"  - Patients: {stats['total_patients']}")
        else:
            print("✗ Failed to get database statistics")
            
        return True
    except Exception as e:
        print(f"✗ Database creation failed: {e}")
        return False

def test_collection_sync():
    """Test syncing collection Excel files to database"""
    print("\n=== Testing Collection File Sync ===")
    try:
        success = sync_all_collection_files()
        if success:
            print("✓ Collection files synced successfully")
            
            # Check updated statistics
            db = TumorboardDatabase()
            stats = db.get_statistics()
            if stats:
                print(f"  - Entities after sync: {stats['total_entities']}")
                print(f"  - Sessions after sync: {stats['total_sessions']}")
                print(f"  - Patients after sync: {stats['total_patients']}")
                
                if stats['total_patients'] > 0:
                    print("✓ Data successfully imported")
                else:
                    print("⚠ No patient data found - check if collection files exist")
            
            return True
        else:
            print("✗ Collection sync failed")
            return False
            
    except Exception as e:
        print(f"✗ Collection sync error: {e}")
        return False

def test_data_analysis():
    """Test data analysis functionality"""
    print("\n=== Testing Data Analysis ===")
    try:
        analyzer = TumorboardAnalyzer()
        
        # Test patient statistics
        patient_stats = analyzer.get_patient_statistics()
        if patient_stats:
            print("✓ Patient statistics generated")
            print(f"  - Tumorboard types: {len(patient_stats['by_tumorboard_type'])}")
        else:
            print("✗ Failed to generate patient statistics")
            return False
        
        # Test temporal analysis
        temporal_analysis = analyzer.get_temporal_analysis()
        if temporal_analysis:
            print("✓ Temporal analysis generated")
        else:
            print("✗ Failed to generate temporal analysis")
            return False
        
        # Test diagnosis analysis
        diagnosis_analysis = analyzer.get_diagnosis_analysis()
        if diagnosis_analysis:
            print("✓ Diagnosis analysis generated")
        else:
            print("✗ Failed to generate diagnosis analysis")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Data analysis error: {e}")
        return False

def test_excel_export():
    """Test Excel export functionality"""
    print("\n=== Testing Excel Export ===")
    try:
        db = TumorboardDatabase()
        export_path = db.export_to_excel()
        
        if export_path and Path(export_path).exists():
            print(f"✓ Excel export successful: {export_path}")
            
            # Check file size
            file_size = Path(export_path).stat().st_size
            print(f"  - File size: {file_size} bytes")
            
            return True
        else:
            print("✗ Excel export failed")
            return False
            
    except Exception as e:
        print(f"✗ Excel export error: {e}")
        return False

def test_comprehensive_report():
    """Test comprehensive analysis report generation"""
    print("\n=== Testing Comprehensive Report ===")
    try:
        results = generate_full_analysis_report()
        
        if results['success']:
            print("✓ Comprehensive report generated successfully")
            if results.get('excel_report'):
                print(f"  - Excel report: {results['excel_report']}")
            if results.get('charts_directory'):
                print(f"  - Charts directory: {results['charts_directory']}")
            return True
        else:
            print("✗ Comprehensive report generation failed")
            if 'error' in results:
                print(f"  - Error: {results['error']}")
            return False
            
    except Exception as e:
        print(f"✗ Comprehensive report error: {e}")
        return False

def main():
    """Run all tests"""
    print("Starting Database Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Database Creation", test_database_creation),
        ("Collection Sync", test_collection_sync),
        ("Data Analysis", test_data_analysis),
        ("Excel Export", test_excel_export),
        ("Comprehensive Report", test_comprehensive_report)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"✗ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{test_name:<25} {status}")
        if success:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Database integration is working correctly.")
    else:
        print("⚠ Some tests failed. Check the output above for details.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 