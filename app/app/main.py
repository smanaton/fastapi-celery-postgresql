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

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


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
                <th>Status</th>
                <th>Result</th>
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
        getStatus(task.id)
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
        const html = `
        <tr>
            <td>${taskID}</td>
            <td>${task.type}</td>
            <td>${task.task_uuid}</td>
            <td>${task.task_name}</td>
            <td>${task.task_status}</td>
            <td>${task.task_result}</td>
        </tr>`;
        const newRow = document.getElementById('tasks').insertRow(0);
        newRow.innerHTML = html;

        const taskStatus = task.task_status;
        if (taskStatus === 'SUCCESS' || taskStatus === 'FAILURE') return false;
        setTimeout(function() {
        getStatus(task.id);
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
    task_result: AsyncResult = None

    if task.type == schemas.TaskType.short:
        task_result = create_short_task.delay()
    if task.type == schemas.TaskType.medium:
        task_result = create_medium_task.delay()
    if task.type == schemas.TaskType.long:
        task_result = create_long_task.delay()

    db_task = models.Task(
        type=task.type,
        task_uuid=task_result.id,
        task_name=task_result.name,
        task_status=task_result.status,
        task_result=task_result.result,
    )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    pprint(db_task.dict())

    return db_task


@app.get("/tasks/{task_id}", response_model=schemas.Task)
def read_task(task_id: str, db: Session = Depends(get_db)):
    db_task: models.Task = (
        db.query(models.Task).filter(models.Task.id == task_id).first()
    )

    pprint(db_task.dict())

    task_result = AsyncResult(db_task.task_uuid, app=celery_app)
    # task_result = app.AsyncResult(task_id)

    # PENDING (waiting for execution or unknown task id)
    # print(task_result.result)
    # if task_result.state == "SUCCESS":
    #     result = task_result.result
    # else:
    #     result = None

    if task_result.status != db_task.task_status:
        db_task.task_name = (task_result.name,)
        db_task.task_result = task_result.result
        db_task.task_status = task_result.status

        db.commit()

    return db_task
