import asyncio
import os
import logging

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from enum import Enum
from pydantic import BaseModel
from typing import Any, Union
from sqlalchemy.orm import Session

from celery.result import AsyncResult
from .tasks import (
    create_short_task,
    create_medium_task,
    create_long_task,
    app as celery_app,
)

from pprint import pprint
from .database import SessionLocal, engine
from . import crud, models, schemas

logger = logging.getLogger(__name__)

# Create table if not exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

print(f"PID[{os.getpid()}] app")

class BackgroundService:
    
    def __init__(self, loop: asyncio.AbstractEventLoop, tasks: list):
        self.loop = loop
        self.running = False
        self.tasks = tasks
        
    async def work(self):
        print(f"Start background service")
        
        while True:
            print(f"Run background service... total_tasks[{len(self.tasks)}]")
            db = SessionLocal()    
            for task_id in self.tasks:
                print(f"update task, task_id[{task_id}] total_tasks[{len(self.tasks)}]")
                
                db_task: models.Task = (
                    db.query(models.Task).filter(models.Task.id == task_id).first()
                )
                task_result = AsyncResult(db_task.celery_task_id, app=celery_app)
                # task_result = app.AsyncResult(task_id)

                # PENDING (waiting for execution or unknown task id)
                # print(task_result.result)
                # if task_result.state == "SUCCESS":
                #     result = task_result.result
                # else:
                #     result = None

                db_task.celery_task_status = task_result.status
                db_task.celery_task_result = task_result.result
                db_task.celery_date_done = task_result.date_done

                # extended fields, ref: [TaskExtended](https://docs.celeryq.dev/en/latest/internals/reference/celery.backends.database.models.html#celery.backends.database.models.TaskExtended`)
                db_task.celery_task_name = task_result.name
                # TODO: pickle values here
                # db_task.celery_task_args = task_result.args
                # db_task.celery_task_kwargs = task_result.kwargs
                db_task.celery_task_worker = task_result.worker
                db_task.celery_task_retries = task_result.retries
                db_task.celery_task_queue = task_result.queue

                print(f"update task [{db_task.dict()}]")
                
                db.commit()
                
                if task_result.status == "SUCCESS":
                    self.tasks.remove(task_id)
                    
            db.close()
            # Sleep for 1 second
            await asyncio.sleep(2)


    async def start(self):
        self.task = self.loop.create_task(self.work())
    
    async def stop(self):
        self.task.cancel()
        try:
            await self.task
        except asyncio.CancelledError:
            print("Clean up background service")

tasks = []
service = BackgroundService(asyncio.get_running_loop(), tasks)

@app.on_event("startup")
async def startup():
    print(f"PID[{os.getpid()}] app startup")
    # schedule a task on main loop
    await service.start()

@app.on_event("shutdown")
async def shutdown():
    # close ProcessPoolExecutor
    logger.info(f"PID[{os.getpid()}] app shutdown")
    await service.stop()
    

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

html_content = """
<html>
    <head>
        <title>Some HTML in here</title>
    </head>
    <body>
        <div class="starter-template">
        <h1>FastAPI + Celery + Docker</h1>
        <hr><br>
        <div>
            <h3>Tasks</h3>
            <p>Pick a task length.</p>
            <div class="btn-group" role="group" aria-label="Basic example">
            <button type="button" class="btn btn-primary" onclick="handleClick('short')">Short</a>
            <button type="button" class="btn btn-primary" onclick="handleClick('medium')">Medium</a>
            <button type="button" class="btn btn-primary" onclick="handleClick('long')">Long</a>
            </div>
        </div>
        <br><br>
        <div>
            <h3>Task Status</h3>
            <br>
            <table class="table">
            <thead>
                <tr>
                <th>ID</th>
                <th>Type</th>
                <th>C_ID</th>
                <th>C_Status</th>
                <th>C_Result</th>
                <th>C_DateDone</th>
                <th>C_Name</th>
                <th>C_Args</th>
                <th>C_Kwargs</th>
                <th>C_Worker</th>
                <th>C_Retries</th>
                <th>C_Queue</th>
                </tr>
            </thead>
            <tbody id="tasks">
            </tbody>
            </table>
        </div>
        </div>
    </body>
    <script type="text/javascript">
    (function() {
        console.log('Sanity Check!');
    })();

    function handleClick(type) {
    fetch('/tasks', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json'
        },
        body: JSON.stringify({ type: type }),
    })
    .then(response => response.json())
    .then(task => {
        const task_id = task.id 
        getStatus(task_id)
    })
    }

    function getStatus(taskID) {
    fetch(`/tasks/${taskID}`, {
        method: 'GET',
        headers: {
        'Content-Type': 'application/json'
        },
    })
    .then(response => response.json())
    .then(task => {
        console.log(task)
        if (!task) {
            setTimeout(function() {
                getStatus(taskID);
            }, 1000);
            return false
        }
        const html = `
        <tr>
            <td>${task.id}</td>
            <td>${task.type}</td>
            <td>${task.celery_task_id}</td>
            <td>${task.celery_task_status}</td>
            <td>${task.celery_task_result}</td>
            <td>${task.celery_task_date_done}</td>
            <td>${task.celery_task_name}</td>
            <td>${task.celery_task_status}</td>
            <td>${task.celery_task_args}</td>
            <td>${task.celery_task_kwargs}</td>
            <td>${task.celery_task_worker}</td>
            <td>${task.celery_task_retries}</td>
            <td>${task.celery_task_queue}</td>
        </tr>`;
        const newRow = document.getElementById('tasks').insertRow(0);
        newRow.innerHTML = html;

        const taskStatus = task.celery_task_status;
        if ( taskStatus === 'SUCCESS' || taskStatus === 'FAILURE') return true;

        setTimeout(function() {
            getStatus(taskID);
        }, 1000);
    })
    .catch(err => console.log(err));
    }
    </script>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def read_index():
    return HTMLResponse(content=html_content, status_code=200)


@app.post("/tasks", status_code=201, response_model=schemas.Task)
def create_task(task: schemas.TaskIn, db: Session = Depends(get_db)):
    task_result: AsyncResult

    if task.type == schemas.TaskType.short:
        task_result = create_short_task.delay()
    if task.type == schemas.TaskType.medium:
        task_result = create_medium_task.delay()
    if task.type == schemas.TaskType.long:
        task_result = create_long_task.delay()

    celery_task_id = task_result.id
    
    db_task = models.Task(
        type=task.type,
        celery_task_id=celery_task_id,
    )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    pprint(db_task.dict())

    task_id = db_task.id
    # global tasks
    tasks.append(task_id)
    
    return db_task

@app.get("/tasks/{task_id}", response_model=schemas.Task)
def read_task(task_id: str, db: Session = Depends(get_db)):
    db_task: models.Task = (
        db.query(models.Task).filter(models.Task.id == task_id).first()
    )

    pprint(db_task.dict())

    # Query task status from celery app
    # task_result = AsyncResult(db_task.celery_task_id, app=celery_app)
    # # task_result = app.AsyncResult(task_id)

    # # PENDING (waiting for execution or unknown task id)
    # # print(task_result.result)
    # # if task_result.state == "SUCCESS":
    # #     result = task_result.result
    # # else:
    # #     result = None

    # db_task.celery_task_status = task_result.status
    # db_task.celery_task_result = task_result.result
    # db_task.celery_date_done = task_result.date_done

    # # extended fields, ref: [TaskExtended](https://docs.celeryq.dev/en/latest/internals/reference/celery.backends.database.models.html#celery.backends.database.models.TaskExtended`)
    # db_task.celery_task_name = task_result.name
    # # TODO: pickle values here
    # # db_task.celery_task_args = task_result.args
    # # db_task.celery_task_kwargs = task_result.kwargs
    # db_task.celery_task_worker = task_result.worker
    # db_task.celery_task_retries = task_result.retries
    # db_task.celery_task_queue = task_result.queue

    # db.commit()

    return db_task
