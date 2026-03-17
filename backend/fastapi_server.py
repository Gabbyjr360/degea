from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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

# Frontend path
frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
if not os.path.exists(frontend_path):
    os.makedirs(frontend_path)

# Serve frontend
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
# Serve uploaded images
images_path = os.path.join(frontend_path, "images")
if not os.path.exists(images_path):
    os.makedirs(images_path)
@app.get("/")
async def serve_frontend():
    return FileResponse(os.path.join("frontend", "index.html"))

# Database setup
DATABASE_URL = "sqlite:///products.db"
engine = create_engine(DATABASE_URL, echo=False)

# Models
class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    price: str
    image: str  # image URL
    desc: str

# Create database tables
SQLModel.metadata.create_all(engine)

# Routes

@app.get("/products", response_model=List[Product])
def get_products():
    with Session(engine) as session:
        products = session.exec(select(Product)).all()
        return products

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

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    # Save file to images folder
    file_location = os.path.join(images_path, file.filename)
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
    return {"url": f"/images/{file.filename}"}