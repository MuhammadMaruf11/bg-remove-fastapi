from sqlalchemy import Column, Integer, String, DateTime, Text
from database.database import Base
from datetime import datetime, timezone

class ProcessedImage(Base):
    __tablename__ = "processed_images"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    # Background chara image
    processed_image_data = Column(Text) 
    # Original image (Toggle er jonno lagle)
    original_image_data = Column(Text)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))