from fastapi import APIRouter, UploadFile, File, status, Query
from app.services.parser_service import parse_cart_image
from app.services.compare_service import compare_products

import os
import shutil

router = APIRouter()

UPLOAD_DIR = "uploads" 

os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_ss(file: UploadFile = File(...), pincode: str = Query(default="110077", description="Pincode for delivery location")):

    file_path = f"{UPLOAD_DIR}/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    products = parse_cart_image(file_path)
    print(f"[upload] parsed products: {products}")
    
    results = await compare_products(products, pincode=pincode)
    
    return results

    