from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from src.model.model import Meal, Workout, StravaUrl
from src.model import utils, strava

client = MongoClient("mongodb+srv://tfgmarcaranda:liferegister@life-register.80mgt.mongodb.net/?retryWrites=true&w=majority&appName=life-register")
db = client["liferegister"]
collection = db["register"]
collection.create_index("date", unique=True)

router = APIRouter()

# Custom serializer para ObjectId
def serialize_document(document):
  return {**document, "_id": str(document["_id"])}

@router.get("/registedDay") 
async def get_registed_day(date: str, email: Optional[str] = None, userEmail: str = Depends(utils.get_current_userEmail)):
  if not email:
    email = userEmail
  
  try:
    documentDB = collection.find_one({"date": date, "userEmail": email})
    if documentDB:
      return serialize_document(documentDB)
    else:
      return {"message": "No hay registros para este día"}
  except:
    raise HTTPException(status_code=500, detail="Error al obtener los registros")

@router.get("/registedDayMeals")
async def get_registed_day_meals(date: str, email: str, userEmail: str = Depends(utils.get_current_userEmail)):
  if not email:
    email = userEmail
  
  try:
    documentDB = collection.find_one({"date": date, "userEmail": email})
    if documentDB and "meals" in documentDB:
      return documentDB["meals"]
    else:
      return {"message": "No hay comidas registradas para este día"}
  except:
    raise HTTPException(status_code=500, detail="Error al obtener las comidas registradas")

@router.get("/registedDayWorkouts")
async def get_registed_day_workouts(date: str, email: str, userEmail: str = Depends(utils.get_current_userEmail)):
  if not email:
    email = userEmail
  
  try:
    documentDB = collection.find_one({"date": date, "userEmail": email})
    if documentDB and "workouts" in documentDB:
      return documentDB["workouts"]
    else:
      return {"message": "No hay ejercicios registrados para este día"}
  except:
    raise HTTPException(status_code=500, detail="Error al obtener los ejercicios registrados")

@router.put("/register/meal")
async def register_meal(meal: Meal, userEmail: str = Depends(utils.get_current_userEmail)):
  try:
    meal_check(meal)

    meal_dict = meal.dict(exclude={"meal"})
    meal_dict["userEmail"] = userEmail

    documentDB = collection.find_one({"date": meal.date})
    if documentDB:
      if "meals" in documentDB:
        mealDB = documentDB["meals"]
        newMealDB = meal_db_refactor(meal.dict(), mealDB)
      else:
        newMealDB = meal_db_refactor(meal.dict(), None)
      result = collection.update_one({"date": meal.date}, {"$set": {"meals": newMealDB}})
    else:
      newMealDB = meal_db_refactor(meal.dict(), None)
      meal_dict["meals"] = newMealDB
      result = collection.insert_one(meal_dict)
        
    if result.acknowledged:
      return {"message": "Meal registered successfully"}
    else:
      raise HTTPException(status_code=500, detail="Error al registrar la comida")
  except DuplicateKeyError:
    raise HTTPException(status_code=400, detail="Ya existe una comida con ese nombre")
    
@router.put("/register/workout")
async def register_workout(workout: Workout, userEmail: str = Depends(utils.get_current_userEmail)):
  try:
    workout_check(workout)

    workout_dict = workout.dict(exclude={"workout"})
    workout_dict["userEmail"] = userEmail

    documentDB = collection.find_one({"date": workout.date})
    if documentDB:
      if "workouts" in documentDB:
        workoutDB = documentDB["workouts"]
        newWorkoutDB = workout_db_refactor(workout.dict(), workoutDB)
      else:
        newWorkoutDB = workout_db_refactor(workout.dict(), None)
      result = collection.update_one({"date": workout.date}, {"$set": {"workouts": newWorkoutDB}})
    else:
      newWorkoutDB = workout_db_refactor(workout.dict(), None)
      workout_dict["workouts"] = newWorkoutDB
      result = collection.insert_one(workout_dict)

    if result.acknowledged:
      return {"message": "Workout registered successfully"}
    else:
      raise HTTPException(status_code=500, detail="Error al registrar el ejercicio")
  except DuplicateKeyError:
    raise HTTPException(status_code=400, detail="Ya existe un ejercicio con ese nombre")
  
@router.put("/register/strava")
def get_strava_data(stravaUrl: StravaUrl):
  try:
    stravaData = strava.get_url_data(stravaUrl.url, stravaUrl.code)
    return stravaData
  except:
    raise HTTPException(status_code=500, detail="Error al obtener los datos de Strava")

def meal_check(meal):
  if not meal.date:
    raise HTTPException(status_code=400, detail="La fecha de la comida es obligatoria")
  
def meal_db_refactor(meal, mealDB):
  if mealDB is not None:
    index = len(mealDB) + 1
    meal_index = f"meal-{index}"
    mealDB.append({meal_index: meal["meal"]})
    return mealDB
  else:
    index = 1
    meal_index = f"meal-{index}"
    return [{meal_index: meal["meal"]}]
  
def workout_check(workout):
  if not workout.date:
    raise HTTPException(status_code=400, detail="La fecha del ejercicio es obligatoria")
  
def workout_db_refactor(workout, workoutDB):
  if workoutDB is not None:
    index = len(workoutDB) + 1
    workout_index = f"workout-{index}"
    workoutDB.append({workout_index: workout["workout"]})
    return workoutDB
  else:
    index = 1
    workout_index = f"workout-{index}"
    return [{workout_index: workout["workout"]}]