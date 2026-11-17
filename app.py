from fastapi import APIRouter, FastAPI

app = FastAPI()
router = APIRouter()

try:
    router.frontend("/", directory='dist')
    app.include_router(router)
except RuntimeError:
    pass
