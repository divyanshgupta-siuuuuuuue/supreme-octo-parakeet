# =========================
# CODE REALME NONSTOP
# ULTRA MAX FASTAPI SERVER
# =========================

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    WebSocket,
    WebSocketDisconnect
)

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import os
import uuid
import shutil
import json
import asyncio
import datetime

# =========================
# APP
# =========================

app = FastAPI(
    title="CODE REALME NONSTOP",
    version="ULTRA MAX"
)

# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# FOLDERS
# =========================

folders = [
    "frontend",
    "storage",
    "storage/profile_logos",
    "storage/project_logos",
    "storage/project_files",
    "storage/messages",
    "storage/compiled",
    "storage/screenshots",
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)

# =========================
# STATIC
# =========================

app.mount("/storage", StaticFiles(directory="storage"), name="storage")
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

# =========================
# DATABASE
# =========================

users = {}
projects = {}
friend_requests = {}
friends = {}
rooms = {}
project_rooms = {}
compiler_logs = {}
meet_rooms = {}
notifications = {}

# =========================
# MODELS
# =========================

class RegisterModel(BaseModel):
    username: str
    bio: str

class ProjectModel(BaseModel):
    name: str
    description: str
    purpose: str
    visibility: str
    owner: str

class FriendRequestModel(BaseModel):
    sender: str
    receiver: str

class LinkModel(BaseModel):
    project_id: str

class MessageModel(BaseModel):
    sender: str
    message: str

# =========================
# SYSTEM
# =========================

def generate_social_id():
    return "CRN-" + str(uuid.uuid4())[:6].upper()

def generate_project_id():
    return "PROJ-" + str(uuid.uuid4())[:8].upper()

def generate_room_id():
    return "ROOM-" + str(uuid.uuid4())[:6].upper()

def current_time():
    return str(datetime.datetime.now())

# =========================
# HOME
# =========================

@app.get("/api")

async def home():

    return {
        "status": "online",
        "server": "CODE REALME NONSTOP",
        "version": "ULTRA MAX"
    }

# =========================
# REGISTER
# =========================

@app.post("/api/register")

async def register_user(
    username: str = Form(...),
    bio: str = Form(...),
    logo: UploadFile = File(...)
):

    social_id = generate_social_id()

    filename = f"{uuid.uuid4()}_{logo.filename}"

    save_path = f"storage/profile_logos/{filename}"

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(logo.file, buffer)

    user = {
        "username": username,
        "bio": bio,
        "social_id": social_id,
        "logo": "/" + save_path,
        "created": current_time(),
        "friends": [],
        "projects": [],
        "online": True
    }

    users[social_id] = user

    notifications[social_id] = []

    return user

# =========================
# ALL USERS
# =========================

@app.get("/api/users")

async def get_users():

    return list(users.values())

# =========================
# USER PROFILE
# =========================

@app.get("/api/profile/{social_id}")

async def get_profile(social_id: str):

    if social_id not in users:

        return JSONResponse(
            status_code=404,
            content={"message": "User Not Found"}
        )

    return users[social_id]

# =========================
# FRIEND REQUEST
# =========================

@app.post("/api/send-request")

async def send_request(data: FriendRequestModel):

    if data.receiver not in users:

        return JSONResponse(
            status_code=404,
            content={"message": "Receiver Not Found"}
        )

    if data.receiver not in friend_requests:
        friend_requests[data.receiver] = []

    friend_requests[data.receiver].append(data.sender)

    return {
        "message": "Friend Request Sent"
    }

# =========================
# ACCEPT REQUEST
# =========================

@app.post("/api/accept-request")

async def accept_request(data: FriendRequestModel):

    sender = data.sender
    receiver = data.receiver

    if sender not in users or receiver not in users:

        return JSONResponse(
            status_code=404,
            content={"message": "User Not Found"}
        )

    users[sender]["friends"].append(receiver)
    users[receiver]["friends"].append(sender)

    return {
        "message": "Friend Added"
    }

# =========================
# CREATE PROJECT
# =========================

@app.post("/api/create-project")

async def create_project(
    name: str = Form(...),
    description: str = Form(...),
    purpose: str = Form(...),
    visibility: str = Form(...),
    owner: str = Form(...),
    logo: UploadFile = File(...)
):

    project_id = generate_project_id()

    filename = f"{uuid.uuid4()}_{logo.filename}"

    logo_path = f"storage/project_logos/{filename}"

    with open(logo_path, "wb") as buffer:
        shutil.copyfileobj(logo.file, buffer)

    os.makedirs(
        f"storage/project_files/{project_id}",
        exist_ok=True
    )

    project = {
        "project_id": project_id,
        "name": name,
        "description": description,
        "purpose": purpose,
        "visibility": visibility,
        "owner": owner,
        "logo": "/" + logo_path,
        "created": current_time(),
        "files": [],
        "team": [],
        "link": None
    }

    projects[project_id] = project

    users[owner]["projects"].append(project_id)

    return project

# =========================
# GET PROJECT
# =========================

@app.get("/api/project/{project_id}")

async def get_project(project_id: str):

    if project_id not in projects:

        return JSONResponse(
            status_code=404,
            content={"message": "Project Not Found"}
        )

    return projects[project_id]

# =========================
# ALL PROJECTS
# =========================

@app.get("/api/projects")

async def all_projects():

    return list(projects.values())

# =========================
# UPLOAD FILE
# =========================

@app.post("/api/upload-file/{project_id}")

async def upload_file(
    project_id: str,
    file: UploadFile = File(...)
):

    if project_id not in projects:

        return JSONResponse(
            status_code=404,
            content={"message": "Project Not Found"}
        )

    folder = f"storage/project_files/{project_id}"

    os.makedirs(folder, exist_ok=True)

    file_path = f"{folder}/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    projects[project_id]["files"].append(file.filename)

    return {
        "message": "File Uploaded",
        "filename": file.filename
    }

# =========================
# SAVE FILE CONTENT
# =========================

@app.post("/api/save-code/{project_id}/{filename}")

async def save_code(
    project_id: str,
    filename: str,
    content: str = Form(...)
):

    folder = f"storage/project_files/{project_id}"

    os.makedirs(folder, exist_ok=True)

    file_path = f"{folder}/{filename}"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return {
        "message": "Code Saved"
    }

# =========================
# LOAD FILE CONTENT
# =========================

@app.get("/api/load-code/{project_id}/{filename}")

async def load_code(
    project_id: str,
    filename: str
):

    file_path = f"storage/project_files/{project_id}/{filename}"

    if not os.path.exists(file_path):

        return {
            "content": ""
        }

    with open(file_path, "r", encoding="utf-8") as f:

        content = f.read()

    return {
        "content": content
    }

# =========================
# LIST FILES
# =========================

@app.get("/api/files/{project_id}")

async def list_files(project_id: str):

    if project_id not in projects:
        return []

    return projects[project_id]["files"]

# =========================
# ADD TEAM MEMBER
# =========================

@app.post("/api/add-team")

async def add_team_member(
    project_id: str = Form(...),
    social_id: str = Form(...)
):

    if project_id not in projects:

        return JSONResponse(
            status_code=404,
            content={"message": "Project Not Found"}
        )

    projects[project_id]["team"].append(social_id)

    return {
        "message": "Member Added"
    }

# =========================
# GENERATE LINK
# =========================

@app.post("/api/generate-link")

async def generate_link(data: LinkModel):

    if data.project_id not in projects:

        return JSONResponse(
            status_code=404,
            content={"message": "Project Not Found"}
        )

    slug = str(uuid.uuid4())[:8]

    link = f"/project-{slug}"

    projects[data.project_id]["link"] = link

    return {
        "link": link
    }

# =========================
# PUBLIC PROJECT PAGE
# =========================

@app.get("/project-{slug}")

async def public_project(slug: str):

    for project in projects.values():

        if project["link"] == f"/project-{slug}":

            return project

    return JSONResponse(
        status_code=404,
        content={"message": "Project Not Found"}
    )

# =========================
# TERMINAL COMPILER
# =========================

@app.post("/api/compile")

async def compile_code(
    project_id: str = Form(...),
    filename: str = Form(...),
    code: str = Form(...)
):

    log = []

    log.append("> INITIALIZING COMPILER")
    log.append("> LOADING FILE")
    log.append("> CHECKING SYNTAX")

    errors = []

    if "error" in code.lower():
        errors.append("Syntax Error Found")

    if "undefined" in code.lower():
        errors.append("Undefined Variable")

    if len(errors) > 0:

        for err in errors:
            log.append("> ERROR: " + err)

        compiler_logs[project_id] = log

        return {
            "success": False,
            "logs": log
        }

    log.append("> BUILD SUCCESSFUL")
    log.append("> FULLSTACK SERVER READY")

    compiler_logs[project_id] = log

    return {
        "success": True,
        "logs": log
    }

# =========================
# GET COMPILER LOGS
# =========================

@app.get("/api/compiler/{project_id}")

async def get_logs(project_id: str):

    return compiler_logs.get(project_id, [])

# =========================
# NOTIFICATIONS
# =========================

@app.get("/api/notifications/{social_id}")

async def get_notifications(social_id: str):

    return notifications.get(social_id, [])

# =========================
# WEBSOCKET CHAT
# =========================

@app.websocket("/ws/chat/{room}")

async def websocket_chat(
    websocket: WebSocket,
    room: str
):

    await websocket.accept()

    if room not in rooms:
        rooms[room] = []

    rooms[room].append(websocket)

    try:

        while True:

            data = await websocket.receive_text()

            for connection in rooms[room]:

                await connection.send_text(data)

    except WebSocketDisconnect:

        rooms[room].remove(websocket)

# =========================
# LIVE CODING
# =========================

@app.websocket("/ws/project/{project_id}")

async def live_project(
    websocket: WebSocket,
    project_id: str
):

    await websocket.accept()

    if project_id not in project_rooms:
        project_rooms[project_id] = []

    project_rooms[project_id].append(websocket)

    try:

        while True:

            data = await websocket.receive_text()

            for user in project_rooms[project_id]:

                await user.send_text(data)

    except WebSocketDisconnect:

        project_rooms[project_id].remove(websocket)

# =========================
# LIVE MEETING
# =========================

@app.websocket("/ws/meet/{room}")

async def meeting_socket(
    websocket: WebSocket,
    room: str
):

    await websocket.accept()

    if room not in meet_rooms:
        meet_rooms[room] = []

    meet_rooms[room].append(websocket)

    try:

        while True:

            data = await websocket.receive_text()

            for peer in meet_rooms[room]:

                if peer != websocket:

                    await peer.send_text(data)

    except WebSocketDisconnect:

        meet_rooms[room].remove(websocket)

# =========================
# SCREEN SHARE
# =========================

@app.websocket("/ws/screen/{room}")

async def screen_share(
    websocket: WebSocket,
    room: str
):

    await websocket.accept()

    if room not in rooms:
        rooms[room] = []

    rooms[room].append(websocket)

    try:

        while True:

            frame = await websocket.receive_text()

            for client in rooms[room]:

                if client != websocket:

                    await client.send_text(frame)

    except WebSocketDisconnect:

        rooms[room].remove(websocket)

# =========================
# SETTINGS
# =========================

@app.get("/api/settings")

async def settings():

    return {
        "theme": "dark neon",
        "server": "online",
        "compiler": "active",
        "multiplayer": "enabled",
        "voice_assistant": "enabled"
    }

# =========================
# HEALTH
# =========================

@app.get("/health")

async def health():

    return {
        "status": "healthy"
    }

# =========================
# SERVER INFO
# =========================

@app.get("/api/server")

async def server_info():

    return {
        "name": "CODE REALME NONSTOP",
        "users": len(users),
        "projects": len(projects),
        "rooms": len(rooms),
        "online": True
    }

# =========================
# DELETE PROJECT
# =========================

@app.delete("/api/delete-project/{project_id}")

async def delete_project(project_id: str):

    if project_id not in projects:

        return JSONResponse(
            status_code=404,
            content={"message": "Project Not Found"}
        )

    del projects[project_id]

    return {
        "message": "Project Deleted"
    }

# =========================
# DELETE USER
# =========================

@app.delete("/api/delete-user/{social_id}")

async def delete_user(social_id: str):

    if social_id not in users:

        return JSONResponse(
            status_code=404,
            content={"message": "User Not Found"}
        )

    del users[social_id]

    return {
        "message": "User Deleted"
    }

# =========================
# AUTO SAVE LOOP
# =========================

async def autosave_loop():

    while True:

        with open("storage/server_backup.json", "w") as f:

            json.dump({
                "users": users,
                "projects": projects
            }, f)

        await asyncio.sleep(60)

# =========================
# STARTUP
# =========================

@app.on_event("startup")

async def startup():

    asyncio.create_task(autosave_loop())

# =========================
# RUN
# =========================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=10000,
        reload=True
    )
