prod:
	python main.py

test:
	python -m unittest -v

dev:
	python main.py --port 8080

prof:
	python do_profile.py
	snakeviz output.prof