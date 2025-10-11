import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
# ensure services on PYTHONPATH
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.orchestrator import run_enhanced_orchestrator_workflow

query = "query_postgresql_tool SELECT datetime, temp, statedistrict FROM weather_data ORDER BY datetime DESC LIMIT 5"
print('Running orchestrator with query:', query)
res = run_enhanced_orchestrator_workflow(query)
print('RESULT:')
print(res)
