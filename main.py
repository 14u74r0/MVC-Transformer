from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app import config
from app.controllers.routes import router
from app.models.vision_model import VisionModel


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Cargando modelo {config.MODEL_ID} (la primera vez se descarga)...")
    app.state.model = VisionModel()
    print(f"Listo en {app.state.model.info()['device']}")
    yield


app = FastAPI(title="Visor de imágenes", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=config.VIEWS_DIR / "static"), name="static")
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host=config.HOST, port=config.PORT)
