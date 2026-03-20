from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import Optional, List
import os
import shutil

# Create FastAPI app
app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# =========================
# PATHS (FIXED)
# =========================

# Correct frontend path (go OUT of backend folder)
BASE_DIR = os.path.dirname(__file__)
frontend_path = os.path.join(BASE_DIR, "..", "frontend")

# Ensure frontend exists
os.makedirs(frontend_path, exist_ok=True)

# Images folder
images_path = os.path.join(frontend_path, "images")
os.makedirs(images_path, exist_ok=True)

# =========================
# STATIC FILES (FIXED)
# =========================

# Serve static frontend files (css/js)
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# Serve uploaded images
app.mount("/images", StaticFiles(directory=images_path), name="images")

# Root route (serve index.html)
@app.get("/")
async def serve_frontend():
    return FileResponse(os.path.join(frontend_path, "index.html"))

# =========================
# DATABASE
# =========================

DATABASE_URL = "sqlite:///products.db"
engine = create_engine(DATABASE_URL, echo=False)

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    price: str
    image: str
    desc: str

SQLModel.metadata.create_all(engine)

# =========================
# ROUTES
# =========================

@app.get("/products", response_model=List[Product])
def get_products():
    with Session(engine) as session:
        return session.exec(select(Product)).all()

@app.post("/products", response_model=Product)
def add_product(
    name: str = Form(...),
    price: str = Form(...),
    image: str = Form(...),
    desc: str = Form(...)
):
    with Session(engine) as session:
        product = Product(name=name, price=price, image=image, desc=desc)
        session.add(product)
        session.commit()
        session.refresh(product)
        return product

# =========================
# IMAGE UPLOAD
# =========================

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    file_location = os.path.join(images_path, file.filename)

    with open(file_location, "wb+") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"url": f"/images/{file.filename}"}