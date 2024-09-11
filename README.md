## Start API

1. Create a virtual environment (hyper console) located in directory of the project

python3 -m venv claude-env

2. Activate the virtual environment

source claude-env/bin/activate

3. Install antrophic

pip install anthropic


4. Install requirements

pip install -r requirements.txt

5. Update some packages

pip install anthropic --upgrade
pip install --upgrade Flask
pip install --upgrade Werkzeug

6. Execute the main

python3 main.py

## Para ejecutar la API en local

1. Renombrar main_local.py como main.py
2. Verificar los comentarios y descomentar todo lo que dice para que funcione en local.  Al mismo tiempo comentar todo lo que dice para API. Especialmente en resume_generator.py