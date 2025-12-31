from pydantic import BaseModel
from typing import Optional

class Program(BaseModel):
    id: str
    source: str  # youtube, stream, local
    url: str
    schedule_time: Optional[str] = None  # Para uso futuro (cronograma)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "morning_show",
                "source": "youtube",
                "url": "https://youtube.com/..."
            }
        }
