from pydantic import BaseModel
from products.models import ProductGetScheme

class ProductCartInfo(BaseModel):
    product_data: ProductGetScheme
    quantity: int
