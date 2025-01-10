from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app import ClaudeAPIClient, XMLParser, PromptCache, ResumeGenerator
import json
import base64
import logging
from logging.handlers import RotatingFileHandler
from PyPDF2 import PdfReader
import io
import os


# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()
# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://ladsan1977.github.io"
    ],
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
    allow_credentials=True,
    max_age=3600,
)

class ResumeRequest(BaseModel):
    job_posting: str
    profile_pdf: str  # Base64 encoded PDF content

api_client = ClaudeAPIClient()
# xml_parser = XMLParser()
prompt_cache = PromptCache()
resume_generator = ResumeGenerator(prompt_cache)

def escape_special_chars(text):
    """
    Escapa los caracteres especiales en una cadena de texto para su uso seguro en JSON.
    
    :param text: La cadena de texto a escapar
    :return: La cadena de texto con caracteres especiales escapados
    """
    # json.dumps() escapa automáticamente los caracteres especiales
    # [1:-1] se usa para quitar las comillas dobles que json.dumps() añade al principio y al final
    return json.dumps(text)[1:-1]

@app.post('/generate_resume')
async def generate_resume(request: Request):
    try:
        body = await request.json()

        resume_request = ResumeRequest(**body)

        pdf_content = base64.b64decode(resume_request.profile_pdf)

        # Create a PDF reader object
        pdf_reader = PdfReader(io.BytesIO(pdf_content))
        
        # Extract text from all pages
        profile_content = ""
        for page in pdf_reader.pages:
            profile_content += page.extract_text()
        
        # logger.debug(f"Extracted text from PDF: {profile_content[:400]}...")

        if not resume_request.job_posting or not profile_content:
            return {"error": "Both job_posting and profile_pdf are required"}, 400
        
        job_posting_escaped = escape_special_chars(resume_request.job_posting)
        profile_pdf_escaped = escape_special_chars(profile_content)

        result = resume_generator.generate_resume_package(job_posting_escaped, profile_pdf_escaped, api_client)
        result_dict = json.loads(result)
        # logger.debug(f"Result --> {result}")

        response_dict = {
            **result_dict
        }
        # Devolver la respuesta JSON
        return JSONResponse(content=response_dict)

    except Exception as e:
         return JSONResponse(content={"error": str(e)}, status_code=400)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)