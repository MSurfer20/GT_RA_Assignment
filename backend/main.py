import json
import os
import uuid
import logging
from typing import List

from fastapi import BackgroundTasks, Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import shutil
import ijson

from .tasks import process_data_task
from .database import Base, engine, get_db
from .models import Task
from .schemas import TaskResponse, TaskListResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(title="JSON Processing API", version="1.0")

# Setup CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/upload", response_model=TaskResponse)
def upload_dataset(payload_file: UploadFile = File(...), db_session: Session = Depends(get_db)):
    if not payload_file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="Only JSON files are supported")
        
    uid = str(uuid.uuid4())
    file_path = f"data/{uid}.json"
    
    try:
        # Stream the file directly to disk to prevent loading massive payloads into RAM
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(payload_file.file, buffer)
            
        dataset_id = "unknown"
        # Extract dataset_id without loading the entire JSON
        with open(file_path, "rb") as f:
            parser = ijson.parse(f)
            for prefix, event, value in parser:
                if prefix == 'dataset_id':
                    dataset_id = value
                    break
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=400, detail="Failed to process or parse JSON file")

    # Create the task record in the database
    new_task = Task(id=uid, status="Pending", dataset_id=dataset_id)
    db_session.add(new_task)
    db_session.commit()
    db_session.refresh(new_task)

    process_data_task.delay(uid)
    
    return new_task

@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: str, db_session: Session = Depends(get_db)):
    record = db_session.query(Task).filter(Task.id == task_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Task not found")
    return record

@app.get("/api/tasks", response_model=List[TaskListResponse])
def list_tasks(db_session: Session = Depends(get_db)):
    return db_session.query(Task).order_by(Task.created_at.desc()).all()

app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def serve_index():
    return FileResponse("frontend/index.html")


