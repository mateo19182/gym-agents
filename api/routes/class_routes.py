from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import insert, text
from db import engine, gym_classes

router = APIRouter(prefix="/classes", tags=["classes"])

class GymClass(BaseModel):
    class_id: int = Field(..., description="Unique identifier for the class")
    instructor_name: str = Field(..., description="Name of the instructor", max_length=32)
    class_name: str = Field(..., description="Name of the class", max_length=32)
    start_time: str = Field(..., description="Start time in HH:MM format", pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    duration_mins: int = Field(..., description="Duration in minutes", gt=0, le=180)

    class Config:
        json_schema_extra = {
            "example": {
                "class_id": 5,
                "instructor_name": "John Smith",
                "class_name": "CrossFit",
                "start_time": "14:30",
                "duration_mins": 60
            }
        }

@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_gym_class(gym_class: GymClass):
    try:
        with engine.connect() as connection:
            stmt = insert(gym_classes).values(**gym_class.dict())
            with connection.begin() as transaction:
                transaction.execute(stmt)
        return {
            "message": "Gym class added successfully",
            "class": gym_class.dict()
        }
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error)
        )

@router.get("/", response_model=dict)
async def get_classes():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT * FROM gym_classes ORDER BY start_time"))
            classes = [dict(row._mapping) for row in result]
        return {"classes": classes}
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error)
        )
