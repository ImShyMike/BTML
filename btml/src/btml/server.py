"""Server backend for BTML's online IDE."""

import fastapi
import uvicorn
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from .__about__ import __version__
from .parser import Parser
from .transpiler import transpile

HOST, PORT = "0.0.0.0", 8000

app = fastapi.FastAPI(
    title="BTML Server",
    description="A language server for the BTML programming language.",
    version=__version__,
    debug=True,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TranspileRequest(BaseModel):
    """Request model for transpiling BTML code."""

    code: str


@app.get("/")
@app.get("/status")
@app.get("/health")
async def root():
    """Check if the server is running."""
    return {"response": "Server is up!", "error": None}


@app.get("/version")
async def version():
    """Get the version of the BTML server."""
    return {"response": app.version, "error": None}


@app.post("/transpile")
async def transpile_code(transpile_request: TranspileRequest):
    """Transpile BTML code to another HTML."""

    if not transpile_request.code:
        return {"response": None, "error": "No code provided for transpilation."}

    parser_instance = Parser()

    try:
        parsed_code = parser_instance.produce_ast(transpile_request.code)
    except Exception as e:  # pylint: disable=broad-except
        return {"response": None, "error": f"Parsing failed: {str(e)}"}

    try:
        transpiled_code = transpile(parsed_code)
    except Exception as e:  # pylint: disable=broad-except
        return {"response": None, "error": f"Transpilation failed: {str(e)}"}

    return {"response": transpiled_code, "error": None}


@app.get("/favicon.ico")
async def favicon():
    """Return a No Content response for favicon requests."""
    return fastapi.responses.Response(status_code=204)


if __name__ == "__main__":
    uvicorn.run("btml.server.main:app", host=HOST)
