from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.db import IMGRequest, MEncode


app = FastAPI(
    title="GalleryApi"
)

img = IMGRequest()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/images", tags=['Images'])
def get_user(limit: int, skip: int):
    if limit < 20:
        img_list = list(img.get_public_images(limit, skip))
        return {"images": MEncode(img_list).encode()}
    else:
        return {"status": "Error"}
