from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import sys
sys.path.append('.')
from .predict_too import run_predict_agent
import json

app = FastAPI()

@app.post('/predict')
async def predict(request: Request):
    try:
        data = await request.json()
        raw_input = json.dumps(data)
        result = run_predict_agent(raw_input)
        return JSONResponse(content={"result": result})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

# To run: uvicorn predict_api:app --reload
