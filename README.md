# Topicos IA: Finanzas-IA (Gestor de Portafolio)

Este repositorio contiene el código base para un Agente de Inteligencia Artificial especializado en el análisis de portafolios de inversión (Acciones, Criptomonedas y ETFs).

## 1. Descripción del Sistema
La aplicación permite a los usuarios interactuar con su información financiera mediante lenguaje natural. El sistema traduce estas peticiones a consultas SQL, las ejecuta en una base de datos segura y devuelve una respuesta razonada.

### Arquitectura Técnica:
- **Motor de IA:** [DSPy](https://dspy-docs.vercel.app/) utilizando el patrón ReAct.
- **Modelo:** `gpt-4o-mini` (OpenAI).
- **Backend:** FastAPI con soporte para tareas asíncronas (`BackgroundTasks`).
- **Base de Datos:** SQLite.

## 2. Esquema de Datos
El agente debe comprender la relación entre las siguientes tablas para resolver las consultas:
- `clients`: Información de inversores (id, full_name, risk_profile).
- `assets`: Catálogo de activos (ticker, name, asset_type).
- `transactions`: Historial de movimientos (id, client_id, ticker, tx_type, quantity, price_usd).
- `queries`: Registro de estado para operaciones asíncronas.

## 3. Tareas del Proyecto

### 3.1. Ingeniería de Prompts (agent.py)
Usted debe completar la definición del agente en `agent.py`:
- **Signature Prompt:** Defina el comportamiento del analista en el docstring de `FinanceAgentSignature`. Debe incluir reglas sobre cómo tratar datos sensibles y la importancia de la precisión numérica.
- **Tool Descriptions:** Implemente las descripciones (`desc`) de cada herramienta al instanciar `dspy.Tool`. Una descripción ambigua impedirá que el agente sepa cuándo usar SQL o cuándo generar un reporte.

### 3.2. Implementación de Herramienta de Reportes (tools.py)
Implemente la lógica necesaria en la función `generate_portfolio_report`. 
- **Requisito:** La función debe recibir una lista de datos (de una consulta SQL) y guardarlos en un archivo con formato `.csv`.
- **Validación:** Debe retornar un mensaje confirmando la ubicación del archivo o detallando cualquier error ocurrido.

### 3.3. Reto de Seguridad: Solo Lectura (tools.py)
El agente no debe tener permisos para modificar la base de datos.
- **Tarea:** Modifique `execute_sql` para que solo permita consultas que comiencen con la palabra clave `SELECT`. Si detecta un `DROP`, `DELETE` o `UPDATE`, debe bloquear la ejecución y devolver un mensaje de error de seguridad al agente.

### 3.4. Reto de Concurrencia (api.py)
Actualmente, el historial de consultas (`query_history`) es una variable global.
- **Tarea:** Identifique el fallo de diseño que ocurre cuando dos usuarios consultan la API al mismo tiempo. Refactorice el código para que el historial sea específico de cada solicitud (aislamiento de estado).

## 4. Configuración y Ejecución

1. **Instalación de dependencias:**
   ```bash
   uv sync
   ```
2. **Variables de Entorno:**
   Cree un archivo `.env` en la raíz del proyecto:
   ```env
   OPENAI_API_KEY=tu_clave_aqui
   ```
3. **Ejecución del Servidor:**
   ```bash
   fastapi dev api.py
   ```
