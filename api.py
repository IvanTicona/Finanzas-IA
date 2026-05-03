import ast
import sqlite3
import uuid
from datetime import datetime
from typing import Annotated

from fastapi import FastAPI, Depends, Body, BackgroundTasks
import dspy
from pydantic import BaseModel

from database import setup_database
from tools import get_schema, execute_sql
from agent import create_agent

app = FastAPI(title="Finance AI Assistant")

class AgentResponse(BaseModel):
    original_query: str
    sql_queries: list[str]
    agent_answer: str

class AgentAsyncStartResponse(BaseModel):
    query_id: uuid.UUID
    status: str = "pending"

class AgentAsyncFinishResponse(AgentResponse):
    query_id: uuid.UUID
    status: str = "finished"

def get_db_connection() -> sqlite3.Connection:
    return setup_database()

def get_db_schema(conn: Annotated[sqlite3.Connection, Depends(get_db_connection)]) -> str:
    return get_schema(conn)

def get_query_history() -> list[str]:
    return []

def query_agent(
    agent: dspy.Module,
    user_query: str,
    db_schema: str,
    query_history: list[str],
    track_query: bool = False,
    query_id: uuid.UUID | None = None,
    db_conn: sqlite3.Connection | None = None
) -> AgentResponse:
    outputs = agent(question=user_query, initial_schema=db_schema)
    results = AgentResponse(
        original_query=user_query,
        sql_queries=query_history,
        agent_answer=outputs.answer
    )
    if track_query and query_id is not None:
        cursor = db_conn.cursor()
        cursor.execute(
            "UPDATE queries SET status='finished', result=? WHERE id=?",
            (results.model_dump_json(), str(query_id)),
        )
        db_conn.commit()

    return results

@app.post("/finance/queries")
def query_finance(
    db_schema: Annotated[str, Depends(get_db_schema)],
    db_conn: Annotated[sqlite3.Connection, Depends(get_db_connection)],
    query_history: Annotated[list[str], Depends(get_query_history)],
    user_query: str = Body(..., embed=True),
) -> AgentResponse:
    agent = create_agent(db_conn, query_history)
    return query_agent(agent, user_query, db_schema, query_history)

@app.post("/finance/async_queries")
def async_query_finance(
    db_schema: Annotated[str, Depends(get_db_schema)],
    background_tasks: BackgroundTasks,
    db_conn: Annotated[sqlite3.Connection, Depends(get_db_connection)],
    query_history: Annotated[list[str], Depends(get_query_history)],
    user_query: str = Body(..., embed=True),
) -> AgentAsyncStartResponse:
    query_id = uuid.uuid4()
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO queries (id, status, result) VALUES (?, 'pending', '')",
        (str(query_id),),
    )
    db_conn.commit()
    agent = create_agent(db_conn, query_history)
    background_tasks.add_task(query_agent, agent, user_query, db_schema, query_history, True, query_id, db_conn)
    return AgentAsyncStartResponse(query_id=query_id)

@app.get("/finance/async_queries")
def get_async_query_result(
    db_conn: Annotated[sqlite3.Connection, Depends(get_db_connection)],
    query_id: uuid.UUID,
) -> AgentAsyncStartResponse | AgentAsyncFinishResponse:
    result = execute_sql(db_conn, f"SELECT * FROM queries WHERE id = '{query_id}'")
    rows = ast.literal_eval(result)
    if not rows:
        return AgentAsyncStartResponse(query_id=query_id, status="pending")

    _, status, result_json = rows[0]
    if status != "finished" or not result_json:
        return AgentAsyncStartResponse(query_id=query_id, status=status)

    response = AgentResponse.model_validate_json(result_json)
    return AgentAsyncFinishResponse(
        original_query=response.original_query,
        sql_queries=response.sql_queries,
        agent_answer=response.agent_answer,
        query_id=query_id
    )
