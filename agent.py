import dspy
import sqlite3
from dotenv import load_dotenv
from tools import execute_sql, get_schema, generate_portfolio_report

class FinanceAgentSignature(dspy.Signature):
    """
    ====> (1.1.1) TU DESCRIPCIÓN/PROMPT PARA EL ASISTENTE FINANCIERO AQUÍ
    """
    question = dspy.InputField(desc="Pregunta sobre portafolios o activos.")
    initial_schema = dspy.InputField(desc="Esquema de la base de datos financiera.")
    answer = dspy.OutputField(desc="Respuesta al cliente.")

class FinanceAgent(dspy.Module):
    def __init__(self, tools: list[dspy.Tool]):
        super().__init__()
        self.agent = dspy.ReAct(FinanceAgentSignature, tools=tools, max_iters=7)

    def forward(self, question: str, initial_schema: str) -> dspy.Prediction:
        return self.agent(question=question, initial_schema=initial_schema)

def configure_llm():
    load_dotenv()
    llm = dspy.LM(model="openai/gpt-4o-mini", max_tokens=4000)
    dspy.settings.configure(lm=llm)
    return llm

def create_agent(conn: sqlite3.Connection, query_history: list[str] | None = None) -> dspy.Module:
    configure_llm()

    execute_sql_tool = dspy.Tool(
        name="execute_sql",
        desc="", # ===> (1.1.2) TU DESCRIPCIÓN AQUÍ
        func=lambda query: execute_sql(conn, query, query_history),
    )

    get_schema_tool = dspy.Tool(
        name="get_schema",
        desc="", # ===> (1.1.2) TU DESCRIPCIÓN AQUÍ
        func=lambda table_name: get_schema(conn, table_name),
    )

    report_tool = dspy.Tool(
        name="generate_portfolio_report",
        desc="", # ===> TU DESCRIPCIÓN AQUÍ
        func=generate_portfolio_report
    )

    all_tools = [execute_sql_tool, get_schema_tool] # Agrega report_tool cuando esté lista
    return FinanceAgent(tools=all_tools)
