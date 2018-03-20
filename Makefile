install:
	rsync -avz --exclude __pycache__ --exclude '*flymake*' --exclude '.ipynb*' --exclude '*~' --delete Theme1-ParcoursDeGraphes Theme3-ArbresCouvrants environment.yml cocalc-algo:
