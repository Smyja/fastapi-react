from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
shift = FastAPI()


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

shift.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@shift.get("/",status_code=201)
async def root():
    return {"message": "Hello World"}

@shift.post("/api/v1/create",status_code=201)
async def create_shift():
    # print(request)
    return {"done"}


