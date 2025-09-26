#!/usr/bin/env python3
"""
Test script to verify TrendAgent environment setup
"""

def test_imports():
    """Test all required imports"""
    try:
        # Core packages
        import pandas as pd
        import numpy as np
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import seaborn as sns
        from scipy import stats
        import os
        import json
        from sqlalchemy import create_engine
        from dotenv import load_dotenv
        
        # LangChain imports
        from langgraph.graph import StateGraph, END, START
        from langchain.agents import initialize_agent
        from langchain_community.agent_toolkits.load_tools import load_tools
        from typing import TypedDict, Optional, List
        from langchain_groq import ChatGroq
        from langchain.tools import tool
        
        print("✅ All imports successful!")
        print(f"📦 Pandas version: {pd.__version__}")
        print(f"📦 NumPy version: {np.__version__}")
        print(f"📦 Matplotlib version: {matplotlib.__version__}")
        
        # Import scipy main module for version
        import scipy
        print(f"📦 SciPy version: {scipy.__version__}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_trendagent_syntax():
    """Test TrendAgent file syntax"""
    try:
        import py_compile
        py_compile.compile('agents/TrendAgent.py', doraise=True)
        print("✅ TrendAgent.py syntax is valid!")
        return True
    except py_compile.PyCompileError as e:
        print(f"❌ Syntax error in TrendAgent.py: {e}")
        return False

def main():
    """Run all tests"""
    print("🔍 Testing TrendAgent Environment Setup")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_imports()
    
    # Test TrendAgent syntax
    syntax_ok = test_trendagent_syntax()
    
    # Summary
    print("\n" + "=" * 50)
    if imports_ok and syntax_ok:
        print("🎉 All tests passed! Environment is ready!")
        print("\n📋 Next steps:")
        print("   1. Set up your .env file with API keys")
        print("   2. Configure your PostgreSQL database")
        print("   3. Test with actual data")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()