from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def home():
    return {"message": "MetricMind Backend is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}