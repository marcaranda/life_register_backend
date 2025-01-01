from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from pymongo import MongoClient
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

# Encriptación de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Secret key para firmar el JWT
SECRET_KEY = "liferegisterkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Tiempo de expiración del token

client = MongoClient("mongodb+srv://tfgmarcaranda:liferegister@life-register.80mgt.mongodb.net/?retryWrites=true&w=majority&appName=life-register")
db = client["liferegister"]
collection = db["user"]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login") 

# Funciones de autenticación
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Crear el token JWT
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Función para verificar el token JWT
def verify_token(token: str) -> Optional[dict]:
    try:
        # Decodificar el JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Verificar si el token ha expirado
        if "exp" in payload and payload["exp"] < datetime.utcnow().timestamp():
            return None  # El token ha expirado

        return payload  # El payload contiene los datos decodificados del JWT

    except JWTError as e:
        # Puedes loguear o agregar detalles adicionales sobre el error
        print(f"Token verification failed: {e}")
        return None  # Token no es válido
    
def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if not payload:
        return None
    email = payload.get("email")
    documentDB = collection.find_one({"email": email})
    return documentDB

def get_current_userEmail(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if not payload:
        return None
    email = payload.get("email")
    if email is None:
        return None
    return email
#@app.get("/protected")
#def get_protected_data(current_user: models.User = Depends(utils.get_current_user)):
    #return {"message": f"Hello, {current_user.username}"}