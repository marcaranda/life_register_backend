from pydantic import BaseModel
from typing import List, Dict

class MealItem(BaseModel):
  name: str
  quantity: int
  unit: str

class Meal(BaseModel):
  date: str
  meal : List[MealItem]
  
class WorkoutItem(BaseModel):
  name : str
  type : str
  customType : str
  url : str
  duration : str
  intensity : str
  calories : str

class Workout(BaseModel):
  date: str
  workout : WorkoutItem