from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime
import uuid

app = FastAPI()
security = HTTPBearer()

# in-memory database (temporary)
users_db = {}
blogs_db = []

# schema data (pydantic)
class RegisterUser(BaseModel):
    nama: str
    nim: str
    kelas: str

class BlogPost(BaseModel):
    judul: str
    isi: str

# endpoint registrasi & generate token
@app.post("/api/register", status_code=201)
def register(user: RegisterUser):
    user_id = len(users_db) + 1
    token = str(uuid.uuid4())

    user_data = {
        "id": user_id,
        "nama": user.nama,
        "nim": user.nim,
        "kelas": user.kelas,
        "created_at": datetime.now().isoformat()
    }

    # menyimpan token yang terhubung dengan user
    users_db[token] = user_data

    return {
        "access_token": token,
        "token_type": "bearer",
        "mahasiswa": user_data
    }

# dependency untuk memverifikasi token
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak valid atau belum registrasi",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return users_db[token]

# endpoint untuk membuat blog post
@app.post("/api/blogs", status_code=201)
def create_blog(blog: BlogPost, current_user: dict = Depends(get_current_user)):
    blog_entry = {
        "id": len(blogs_db) + 1,
        "judul": blog.judul,
        "isi": blog.isi,
        "author_id": current_user["id"],
        "author_nama": current_user["nama"],
        "author_nim": current_user["nim"],
        "author_kelas": current_user["kelas"],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    blogs_db.append(blog_entry)
    return blog_entry

# endpoint untuk mendapatkan semua blog post
@app.get("/api/blogs", status_code=200)
def get_blogs():
    return blogs_db