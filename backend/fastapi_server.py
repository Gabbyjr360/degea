from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Allow all origins for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"]
)

class Product(BaseModel):
    id: int
    name: str
    price: str
    image: str
    desc: str

products: List[Product] = []

@app.get("/products", response_model=List[Product])
def get_products():
    return products

@app.post("/products", response_model=Product)
def add_product(product: Product):
    products.append(product)
    return product


