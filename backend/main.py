from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import os

app = FastAPI(title="Todo App")

# Path to frontend folder
filepath_fe_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

# Serve static files (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory=filepath_fe_dir), name="static")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins (for dev)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve index.html at root
@app.get("/")
def home():
    return FileResponse(os.path.join(filepath_fe_dir, "index.html"))

@app.get("/.well-known/assetlinks.json")
def serve_android_assetlinks():
    return FileResponse("path/to/your/assetlinks.json")

@app.get("/.well-known/apple-app-site-association")
def serve_ios_association():
    return FileResponse("path/to/your/apple-app-site-association")
# ---------------------------
# Todo API
# ---------------------------
class TodoCreate(BaseModel):
    task: str
    completed: bool = False

class Todo(TodoCreate):
    id: int

todos: List[Todo] = []
next_id = 1

@app.post("/todos", response_model=Todo)
def create_todo(todo: TodoCreate):
    global next_id
    new_todo = Todo(id=next_id, task=todo.task, completed=todo.completed)
    next_id += 1
    todos.append(new_todo)
    return new_todo


todos: List[Todo] = []

@app.get("/todos", response_model=List[Todo])
def get_todos():
    return todos

@app.post("/todos", response_model=Todo)
def create_todo(todo: Todo):
    for t in todos:
        if t.id == todo.id:
            raise HTTPException(status_code=400, detail="Todo with this ID already exists")
    todos.append(todo)
    return todo

@app.put("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, updated: Todo):
    for index, todo in enumerate(todos):
        if todo.id == todo_id:
            todos[index] = updated
            return updated
    raise HTTPException(status_code=404, detail="Todo not found")

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    for index, todo in enumerate(todos):
        if todo.id == todo_id:
            todos.pop(index)
            return {"message": "Todo deleted"}
    raise HTTPException(status_code=404, detail="Todo not found")
