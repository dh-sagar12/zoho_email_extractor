.PHONY: start install help

help:
	@echo "Available commands:"
	@echo "  make install  - Install dependencies from requirements.txt"
	@echo "  make start    - Start the FastAPI application with uvicorn"
	@echo "  make help     - Show this help message"

install:
	pip install -r requirements.txt

start:
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

