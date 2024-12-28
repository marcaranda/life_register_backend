from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from src.model.model import User
from src.model import utils

client = MongoClient("mongodb+srv://tfgmarcaranda:liferegister@life-register.80mgt.mongodb.net/?retryWrites=true&w=majority&appName=life-register")
db = client["liferegister"]
collection = db["user"]
collection.create_index("email", unique=True)

router = APIRouter()

# Custom serializer para ObjectId
def serialize_document(document):
  return {**document, "_id": str(document["_id"])}

@router.get("/getUser/{email}")
async def get_user(email: str):
  try:
    documentDB = collection.find_one({"email": email})
    if documentDB:
      return serialize_document(documentDB)
    else:
      return {"message": "No existe el usuario"}
  except:
    raise HTTPException(status_code=500, detail="Error al obtener el usuario")
  
@router.get("/getUsers")
async def get_users_name(name: str, userEmail: str = Depends(utils.get_current_userEmail)):
  try:
    documentsDB = collection.find({"name": {"$regex": f"^{name}", "$options": "i"}})
    users = [{"name": doc["name"], "email": doc["email"]} for doc in documentsDB if doc["email"] != userEmail]
    return users
  except:
    raise HTTPException(status_code=500, detail="Error al obtener los usuarios")

@router.post("/registerUser")
async def register_user(user: User):
  try:
    user_dict = user.dict(exclude={"password"})
    user_dict["password"] = utils.get_password_hash(user.password)

    result = collection.insert_one(user_dict)
    if result.acknowledged:
      token = utils.create_access_token({"email": str(user.email)})
      return {"token": token, "token_type": "bearer"}
    else:
      raise HTTPException(status_code=500, detail="Error al registrar la comida")
  except DuplicateKeyError:
    raise HTTPException(status_code=400, detail="El usuario ya existe")
  except:
    raise HTTPException(status_code=500, detail="Error al registrar el usuario")
  
@router.post("/login")
async def login(formData: OAuth2PasswordRequestForm = Depends()):
  try:
    documentDB = collection.find_one({"email": formData.username})
    if documentDB and utils.verify_password(formData.password, documentDB["password"]):
      token = utils.create_access_token({"email": str(formData.username)})
      return {"token": token, "token_type": "bearer"}
    else:
      return {"message": "Usuario o contraseña incorrectos"}
  except:
    raise HTTPException(status_code=500, detail="Error al iniciar sesión")
  
@router.get("/friends/list")
async def get_friends(userEmail: str = Depends(utils.get_current_userEmail)):
  try:
    documentDB = collection.find_one({"email": userEmail})
    if documentDB and "friends" in documentDB:
      return documentDB["friends"]
    else:
      return {"message": "No tienes amigos"}
  except:
    raise HTTPException(status_code=500, detail="Error al obtener los amigos")
  
async def new_friendship(email: str, userEmail: str):
  try:
    result1 = collection.update_one({"email": email}, {"$push": {"friends": userEmail}})
    result2 = collection.update_one({"email": userEmail}, {"$push": {"friends": email}})

    if result1.acknowledged and result2.acknowledged:
      return {"message": "Amistad aceptada"}
  except:
    raise HTTPException(status_code=500, detail="Error al enviar la solicitud")