from pydantic import BaseModel
from backend.src.products.models import ProductGetScheme

class ProductCartInfo(BaseModel):
    product_data: ProductGetScheme
    quantity: int
