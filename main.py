from fastapi import FastAPI

app = FastAPI (
    title = "Evangelismo API"
    description = "Esta api esta dedicada a..."
)


@app.get("/")
def read_root():
    return {"Hello": "World"}
