default: start

activate:
	bash -c "source venv/bin/activate"

run:
	venv/bin/wave run app.py

db: 
	venv/bin/wavedb -access-key-id uzer -access-key-secret pa55word

copy_venv:
	venv/bin/pip freeze > requirements_venv.txt

clone_venv:
	venv/bin/pip install -r requirements_venv.txt
	cp wavedb venv/bin/
