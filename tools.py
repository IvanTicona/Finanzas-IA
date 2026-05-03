import sqlite3
import csv

def execute_sql(conn: sqlite3.Connection, query: str, query_history: list[str] | None = None) -> str:
    if not query.strip().upper().startswith("SELECT"):
        return "Error de seguridad: solo se permiten consultas SELECT. Operación bloqueada."

    if query_history is not None: query_history.append(query)
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        if cursor.description: return str(cursor.fetchall())
        conn.commit()
        return "Consulta ejecutada correctamente."
    except sqlite3.Error as e:
        return f"Error: {e}"

def get_schema(conn: sqlite3.Connection, table_name: str | None = None) -> str:
    cursor = conn.cursor()
    if table_name:
        cursor.execute(f"PRAGMA table_info({table_name});")
        return str([(col[1], col[2]) for col in cursor.fetchall()])
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return str([table[0] for table in cursor.fetchall()])

def generate_portfolio_report(data: list[tuple], filename: str) -> str:
    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerows(data)
        return f"Reporte generado exitosamente en '{filename}'."
    except Exception as e:
        return f"Error al generar el reporte: {e}"
