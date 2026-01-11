import uvicorn
from fastapi import FastAPI

from src.api.objects import router as objects_router
from src.api.users import router as users_router

app = FastAPI()

app.include_router(users_router)
app.include_router(objects_router)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
