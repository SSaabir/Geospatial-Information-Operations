#!/usr/bin/env python3
"""
Simple Report Viewer for Orchestrator Results
============================================
This script helps you easily view orchestrator reports and manage visualizations.
"""

import sys
import os
import json
from datetime import datetime

sys.path.append(os.path.dirname(__file__))

def view_latest_report(query=None):
    """View the latest report from orchestrator."""
    if not query:
        query = input("Enter your query (or press Enter for default): ").strip()
        if not query:
            query = "comprehensive weather analysis for colombo from database"
    
    print("🔍 GENERATING REPORT...")
    print("=" * 60)
    
    try:
        from orchestrator import run_orchestrator_workflow
        result = run_orchestrator_workflow(query)
        
        print(f"📝 Query: {query}")
        print(f"🔄 Workflow Type: {result.get('workflow_type', 'Unknown')}")
        print(f"⏰ Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n" + "=" * 60)
        
        # Show collector results
        if result.get('collector_result'):
            print("📊 COLLECTOR RESULTS:")
            print("-" * 30)
            try:
                collector_data = json.loads(result['collector_result']) if isinstance(result['collector_result'], str) else result['collector_result']
                if 'rows' in collector_data:
                    print(f"📈 Database records found: {collector_data.get('row_count', 'Unknown')}")
                elif 'temp' in collector_data:
                    print(f"🌡️ Current Temperature: {collector_data['temp']}°C")
                    print(f"🌡️ Conditions: {collector_data.get('conditions', 'Unknown')}")
                print()
            except:
                print("Raw collector data available\n")
        
        # Show trend analysis summary
        if result.get('trend_result'):
            print("📈 TREND ANALYSIS SUMMARY:")
            print("-" * 30)
            try:
                trend_data = json.loads(result['trend_result']) if isinstance(result['trend_result'], str) else result['trend_result']
                if 'dataset_info' in trend_data:
                    info = trend_data['dataset_info']
                    print(f"📊 Records Analyzed: {info.get('shape', [0])[0]} entries")
                    date_range = info.get('date_range', {})
                    print(f"📅 Date Range: {date_range.get('start', 'N/A')} to {date_range.get('end', 'N/A')}")
                    print(f"🔢 Data Fields: {len(info.get('columns', []))} variables")
                print()
            except:
                print(f"Detailed trend analysis completed ({len(str(result['trend_result']))} chars)\n")
        
        # Show final report
        if result.get('report_result'):
            print("📋 WEATHER SUMMARY FOR YOU:")
            print("=" * 60)
            print(result['report_result'])
            print("=" * 60)
        elif result.get('final_output'):
            print("📋 ANALYSIS RESULTS:")
            print("=" * 60)
            print(result['final_output'])
            print("=" * 60)
        else:
            print("📋 Quick Data View (detailed analysis not generated for this query type)")
            print("💡 Try asking: 'analyze colombo weather trends' for a full report")
        
        # Show visualization info
        visualizations_dir = "agents/visualizations"
        if os.path.exists(visualizations_dir):
            viz_files = [f for f in os.listdir(visualizations_dir) if f.endswith('.png')]
            if viz_files:
                print(f"\n📊 VISUALIZATIONS GENERATED: {len(viz_files)} charts")
                print(f"📁 Location: {os.path.abspath(visualizations_dir)}")
                print("📈 Charts:", ", ".join(viz_files[:5]) + ("..." if len(viz_files) > 5 else ""))
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def clean_visualizations():
    """Clean up old visualization files."""
    print("🧹 CLEANING OLD VISUALIZATIONS...")
    
    # Check for scattered visualization directories
    viz_dirs = []
    root_dir = os.path.dirname(os.path.dirname(__file__))
    
    for root, dirs, files in os.walk(root_dir):
        if 'visualizations' in dirs:
            viz_path = os.path.join(root, 'visualizations')
            viz_files = [f for f in os.listdir(viz_path) if f.endswith('.png')]
            if viz_files:
                viz_dirs.append((viz_path, len(viz_files)))
    
    if len(viz_dirs) > 1:
        print(f"⚠️ Found {len(viz_dirs)} visualization directories:")
        for viz_dir, count in viz_dirs:
            print(f"   📁 {viz_dir}: {count} files")
        
        # Keep only the agents/visualizations directory
        keep_dir = os.path.join(os.path.dirname(__file__), "visualizations")
        for viz_dir, count in viz_dirs:
            if viz_dir != keep_dir:
                try:
                    import shutil
                    shutil.rmtree(viz_dir)
                    print(f"✅ Removed: {viz_dir}")
                except Exception as e:
                    print(f"❌ Could not remove {viz_dir}: {e}")
    else:
        print("✅ Visualizations are already organized")

def main():
    """Main interface for the report viewer."""
    print("🎯 ORCHESTRATOR REPORT VIEWER")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. View latest report")
        print("2. Custom query report")
        print("3. Clean visualizations")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '1':
            view_latest_report()
        elif choice == '2':
            query = input("Enter your query: ").strip()
            if query:
                view_latest_report(query)
        elif choice == '3':
            clean_visualizations()
        elif choice == '4':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    # If arguments provided, run directly
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        view_latest_report(query)
    else:
        main()