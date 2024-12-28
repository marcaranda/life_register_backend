from fastapi import APIRouter, HTTPException, Depends
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from src.model import utils
from src.service.user import get_user, new_friendship

client = MongoClient("mongodb+srv://tfgmarcaranda:liferegister@life-register.80mgt.mongodb.net/?retryWrites=true&w=majority&appName=life-register")
db = client["liferegister"]
collection = db["friendship"]
collection.create_index("email", unique=True)

router = APIRouter()

# Custom serializer para ObjectId
def serialize_document(document):
  return {**document, "_id": str(document["_id"])}

@router.get("/friends/request")
async def get_request_friends(userEmail: str = Depends(utils.get_current_userEmail)):
  try:
    documentsDB = collection.find({"email": userEmail, "status": "pending"})
    users = []
    for doc in documentsDB:
      user = await get_user(doc["userEmail"])
      users.append({"name": user["name"], "email": user["email"]})
    return users
  except:
    raise HTTPException(status_code=500, detail="Error al obtener las solicitudes de amistad")

@router.post("/friends/request")
async def request_friend(email: str, userEmail: str = Depends(utils.get_current_userEmail)):
  try:
    result = collection.insert_one({"email": email, "userEmail": userEmail, "status": "pending"})
    if result.acknowledged:
      return {"message": "Solicitud enviada"}
    else:
      raise HTTPException(status_code=500, detail="Error al enviar la solicitud")
  except DuplicateKeyError:
    raise HTTPException(status_code=400, detail="Ya has enviado una solicitud a este usuario")
  except:
    raise HTTPException(status_code=500, detail="Error al enviar la solicitud")
  
@router.put("/friends/accept")
async def accept_friend(email: str, userEmail: str = Depends(utils.get_current_userEmail)):
  try:
    result = collection.update_one({"email": userEmail, "userEmail": email}, {"$set": {"status": "accepted"}})
    resultUser = await new_friendship(email, userEmail)
    if result.acknowledged:
      return {"message": "Amistad aceptada"}
    else:
      raise HTTPException(status_code=500, detail="Error al aceptar la solicitud")
  except:
    raise HTTPException(status_code=500, detail="Error al aceptar la solicitud")
  
@router.delete("/friends/reject")
async def reject_friend(email: str, userEmail: str = Depends(utils.get_current_userEmail)):
  try:
    result = collection.delete_one({"email": userEmail, "userEmail": email})
    if result.acknowledged:
      return {"message": "Amistad rechazada"}
    else:
      raise HTTPException(status_code=500, detail="Error al rechazar la solicitud")
  except:
    raise HTTPException(status_code=500, detail="Error al rechazar la solicitud")
  
@router.delete("/friends/cancel")
async def cancel_friend(email: str, userEmail: str = Depends(utils.get_current_userEmail)):
  try:
    result = collection.delete_one({"email": email, "userEmail": userEmail})
    if result.acknowledged:
      return {"message": "Solicitud cancelada"}
    else:
      raise HTTPException(status_code=500, detail="Error al cancelar la solicitud")
  except:
    raise HTTPException(status_code=500, detail="Error al cancelar la solicitud")