from flask import Flask, request, jsonify
from app import ClaudeAPIClient, XMLParser, PromptCache, ResumeGenerator
import json
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Configurar logging
log_file = 'app.log'
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# Configurar el manejador de archivos con rotación
file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Añadir el manejador al logger de la aplicación
app.logger.addHandler(file_handler)

api_client = ClaudeAPIClient()
xml_parser = XMLParser()
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

def clean_old_logs():
    """Elimina los mensajes de log del mes pasado"""
    if not os.path.exists(log_file):
        return

    one_month_ago = datetime.now() - timedelta(days=30)
    temp_file = log_file + '.temp'

    with open(log_file, 'r') as input_file, open(temp_file, 'w') as output_file:
        for line in input_file:
            try:
                log_date = datetime.strptime(line[:19], '%Y-%m-%d %H:%M:%S')
                if log_date >= one_month_ago:
                    output_file.write(line)
            except ValueError:
                # Si no se puede parsear la fecha, mantener la línea
                output_file.write(line)

    os.replace(temp_file, log_file)

@app.route('/generate_resume', methods=['POST'])
def generate_resume():
    # Limpiar logs antiguos antes de registrar nuevos valores
    clean_old_logs()

    try:
        # data = request.json
        data = request.get_json(force=True)  # Force JSON parsing
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON in request body"}), 400

    job_posting = data.get('job_posting')
    profile_pdf = data.get('profile_pdf')

    if not job_posting or not profile_pdf:
        return jsonify({"error": "Both job_posting and profile_pdf are required"}), 400

    try:
        # Escape special characters in the input strings
        job_posting_escaped = escape_special_chars(job_posting)
        profile_pdf_escaped = escape_special_chars(profile_pdf)

        # Registrar los valores completos
        # app.logger.info(f"job_posting: {job_posting_escaped}")
        # app.logger.info(f"profile_pdf: {profile_pdf_escaped}")

        print(f"job_posting: {job_posting_escaped}")
        print(f"profile_pdf: {profile_pdf_escaped}")

        result = resume_generator.generate_resume_package(job_posting_escaped, profile_pdf_escaped, api_client, xml_parser)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)