from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import List
from enum import Enum

# ------------------------
# Categories
# ------------------------
class CategoryCreate(BaseModel):
    name: str

class CategoryResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(
        from_attributes=True
    )
        
# ------------------------
# Products
# ------------------------      
class ProductCreate(BaseModel):
    title: str
    description: str | None = None
    price: int = Field(0, ge = 1)
    quantity: int = Field(0, ge = 1)
    category_id: int

class ProductUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    price: int | None = Field(None, ge=1) 
    quantity: int | None = Field(None, ge=1)
    category_id: int | None = None
    
class ProductResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    price: int
    quantity: int
    category_id: int
    
    model_config = ConfigDict(
        from_attributes=True
    )
        
class ProductFilters(BaseModel):
    category_id: int | None = None
    min_price: int | None = Field(None, ge=0)
    max_price: int | None = Field(None, ge=0)

    limit: int = Field(20, ge=1, le=100)   
    offset: int = Field(0, ge=0)  

# ------------------------
# Cart
# ------------------------ 
class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: ProductResponse
    
    model_config = ConfigDict(
        from_attributes=True
    )
        
class AdminCartItemResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    product: ProductResponse
    
    model_config = ConfigDict(
        from_attributes=True
    )

class CartItemPayload(BaseModel):
    product_id: int
    quantity: int

class CartItemUpdate(BaseModel):
    quantity: int = Field(0, ge = 1)
    
# ------------------------
# Orders
# ------------------------    
class OrderItemResponse(BaseModel):
    product_id: int
    quantity: int
    price: float
    
    model_config = ConfigDict(
        from_attributes=True
    )

class OrderStatus(str, Enum):
    created = "created"
    paid = "paid"
    shipped = "shipped"
    canceled = "canceled"
    
     
class OrderUpdateStatus(BaseModel):
    status: OrderStatus
           
class OrderResponse(BaseModel):
    id: int
    total_price: float
    status: str
    items: List[OrderItemResponse]
    
    model_config = ConfigDict(
        from_attributes=True
    )

class AdminOrderResponse(BaseModel):
    id: int
    user_id: int
    total_price: float
    status: str
    items: List[OrderItemResponse]
    
    model_config = ConfigDict(
        from_attributes=True
    )
        
# ------------------------
# Username
# ------------------------         
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str

    model_config = ConfigDict(
        from_attributes=True
    )

class UserAuth(BaseModel):
    email: EmailStr
    password: str
    
class Token(BaseModel):
    access_token: str
    token_type: str
    

class UserRoleUpdate(BaseModel):
    user_id: int
    role: str 
    
class UserPasswordReset(BaseModel):
    user_id: int
    new_password: str
    