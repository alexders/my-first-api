from fastapi import FastAPI

app = FastAPI()


@app.get("/getmessage")
async def read_root():
    return {"message": "Hello, World!"}
