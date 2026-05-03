import dspy
import sqlite3
from dotenv import load_dotenv
from tools import execute_sql, get_schema, generate_portfolio_report

class FinanceAgentSignature(dspy.Signature):
    """
    Sos un asistente financiero especializado en análisis de portafolios de inversión.
    Tenés acceso a una base de datos SQLite con información de clientes, activos y transacciones.

    Reglas obligatorias:
    - Respondé SIEMPRE con datos reales obtenidos de la base de datos. Nunca inventes cifras.
    - Si no encontrás datos para responder, indicalo explícitamente.
    - No compartas información de un cliente cuando se pregunta por otro.
    - Usá precisión numérica exacta: no redondees a menos que el usuario lo pida.
    - Antes de escribir cualquier SQL con JOINs o columnas específicas, usá get_schema para verificar los nombres exactos. No asumas columnas — verificalas siempre.
    - El capital invertido en una transacción siempre es quantity * price_usd. Nunca uses price_usd solo como medida de capital o volumen.
    - Generá un reporte CSV solo cuando el usuario lo solicite explícitamente.
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
        desc="Ejecuta una consulta SQL SELECT en la base de datos financiera. "
             "Usá este tool para obtener datos de clientes, activos o transacciones. "
             "Solo acepta consultas SELECT; cualquier otra operación será bloqueada.",
        func=lambda query: execute_sql(conn, query, query_history),
    )

    get_schema_tool = dspy.Tool(
        name="get_schema",
        desc="Devuelve el esquema de la base de datos. Sin argumentos lista todas las tablas; "
             "con el nombre de una tabla devuelve sus columnas y tipos. "
             "Usá este tool antes de escribir SQL si no conocés la estructura exacta.",
        func=lambda table_name: get_schema(conn, table_name),
    )

    report_tool = dspy.Tool(
        name="generate_portfolio_report",
        desc="Guarda datos de un portafolio en un archivo CSV. "
             "Recibe una lista de tuplas con los datos y el nombre del archivo de destino. "
             "Usá este tool SOLO cuando el usuario solicite explícitamente un reporte, archivo o exportación.",
        func=generate_portfolio_report,
    )

    all_tools = [execute_sql_tool, get_schema_tool, report_tool]
    return FinanceAgent(tools=all_tools)
