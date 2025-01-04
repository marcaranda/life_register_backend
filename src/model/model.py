from pydantic import BaseModel
from typing import List

class User(BaseModel):
  name: str
  email: str
  password: str

class MealItem(BaseModel):
  name: str
  quantity: int
  unit: str
  saveMacros: bool

class Meal(BaseModel):
  date: str
  meal : List[MealItem]
  
class WorkoutItem(BaseModel):
  name : str
  type : str
  url : str
  duration : str
  intensity : str
  calories : str

class Workout(BaseModel):
  date: str
  workout : WorkoutItem

class StravaUrl(BaseModel):
  url: str
  code: str