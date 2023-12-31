from sqlalchemy import Column, DateTime, Integer, String, func
from .database import Base


class BaseModel(Base):
    """Base database table representation to reuse."""
    __abstract__ = True
    creation_date = Column(DateTime(timezone=True), server_default=func.now())
    update_date = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        fields = ""
        for column in self.__table__.columns:
            if fields == "":
                fields = f"{column.name}='{getattr(self, column.name)}'"
            else:
                fields = f"{fields}, {column.name}='{getattr(self, column.name)}'"
        return f"<{self.__class__.__name__}({fields})>"


class Piece(BaseModel):
    STATUS_CREATED = "Created"
    STATUS_MANUFACTURING = "Manufacturing"
    STATUS_MANUFACTURED = "Manufactured"

    __tablename__ = "piece"
    id = Column(Integer, primary_key=True)
    status = Column(String(256), default=STATUS_CREATED)
    order_id = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<Piece(id={self.id}, status='{self.status}', order_id={self.order_id})>"
