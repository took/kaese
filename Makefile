# Install requirements
install:
	python3 -m pip install -r requirements.txt || pip install -r requirements.txt
	sudo apt install python3-tk || echo "TKInter is optional"
	sudo apt install python3-coverage || echo "Only needed for unit tests"
	python -m pip install coverage
.PHONY: install

# Run the game
run:
	python3 main.py --size-x=10 --size-y=10 --loglevel=INFO
.PHONY: run

# Run the unit tests
test:
	coverage run -m unittest discover
	coverage report
.PHONY: test

# Generate the coverage report
coverage:
	coverage run -m unittest discover
	coverage report
	coverage html
	open htmlcov/index.html > /dev/null 2>&1
.PHONY: coverage
