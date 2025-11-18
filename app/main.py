from fastapi import FastAPI, Request, HTTPException
from app.quiz_solver import solve_quiz
from app.llm_utils import MY_SECRET, MY_EMAIL

app = FastAPI()

@app.post("/quiz")
async def quiz_endpoint(request: Request):
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    email = data.get("email")
    secret = data.get("secret")
    url = data.get("url")
    
    if secret != MY_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")
    if not url or not email:
        raise HTTPException(status_code=400, detail="Missing url or email")
    
    try:
        result = await solve_quiz(url, email, secret)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
