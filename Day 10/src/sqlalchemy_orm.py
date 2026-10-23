from decimal import Decimal
from sqlalchemy import String, Numeric, Integer, ForeignKey, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from src.config import sqlalchemy_url

engine = create_engine(sqlalchemy_url(), pool_pre_ping=True)

class Base(DeclarativeBase):
    pass

class Category(Base):
    __tablename__ = "categories"
    category_id: Mapped[int] = mapped_column(primary_key=True)
    category_name: Mapped[str] = mapped_column(String(100), unique=True)
    products: Mapped[list["Product"]] = relationship(back_populates="category")

class Product(Base):
    __tablename__ = "products"
    product_id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.category_id"))
    product_name: Mapped[str] = mapped_column(String(200))
    sku: Mapped[str] = mapped_column(String(50))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    stock_quantity: Mapped[int] = mapped_column(Integer)
    category: Mapped[Category] = relationship(back_populates="products")

def list_products(max_price: Decimal | None = None) -> list[Product]:
    statement = select(Product).order_by(Product.product_id)
    if max_price is not None:
        statement = statement.where(Product.unit_price <= max_price)
    with Session(engine) as session:
        return list(session.scalars(statement).all())

def create_category(category_name: str) -> int:
    with Session(engine) as session:
        existing = session.scalar(select(Category).where(Category.category_name == category_name))
        if existing:
            return existing.category_id
        category = Category(category_name=category_name)
        session.add(category)
        session.flush()
        category_id = category.category_id
        session.commit()
        return category_id

if __name__ == "__main__":
    for p in list_products():
        print(p.product_id, p.product_name, p.unit_price)
