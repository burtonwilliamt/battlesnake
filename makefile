prod:
	python main.py

test:
	python -m unittest -v

dev:
	python main.py --port 8080