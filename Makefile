# Makefile for Estimate Insight Agent Pro
# Simplifies common development tasks

.PHONY: help install test-data demo demo-ai demo-full setup clean deploy api api-prod test-api

help:
	@echo "Estimate Insight Agent Pro - Available Commands"
	@echo "================================================"
	@echo ""
	@echo "CLI Commands:"
	@echo "  make install      - Install Python dependencies"
	@echo "  make setup        - Setup GCP resources"
	@echo "  make test-data    - Generate sample Excel files"
	@echo "  make demo         - Run quick demo (no AI)"
	@echo "  make demo-ai      - Run demo with Gemini insights"
	@echo "  make demo-full    - Run demo with AI + memory storage"
	@echo ""
	@echo "API Commands:"
	@echo "  make api          - Run API server (development)"
	@echo "  make api-prod     - Run API server (production with gunicorn)"
	@echo "  make test-api     - Test API endpoints"
	@echo ""
	@echo "Deployment:"
	@echo "  make deploy       - Deploy to Google Cloud Run"
	@echo "  make clean        - Remove generated files"
	@echo ""

install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	@echo "✅ Installation complete!"

setup:
	@echo "🔧 Setting up GCP resources..."
	./scripts/setup_gcp.sh

test-data:
	@echo "📊 Generating test data..."
	python scripts/create_test_data.py

demo: test-data
	@echo "🚀 Running quick demo (no AI)..."
	@echo ""
	python main.py sample_data/estimate.xlsx sample_data/actual.xlsx \
		--project-name "Sample Project" \
		--quick

demo-ai: test-data
	@echo "🤖 Running demo with Gemini insights..."
	@echo ""
	python main.py sample_data/estimate.xlsx sample_data/actual.xlsx \
		--project-name "Sample Project"

demo-full: test-data
	@echo "🧠 Running full demo with AI + memory..."
	@echo ""
	python main.py sample_data/estimate.xlsx sample_data/actual.xlsx \
		--project-name "Sample Project" \
		--save-memory

api:
	@echo "🚀 Starting API server (development mode)..."
	@echo "Server will be available at http://localhost:8080"
	@echo ""
	python app.py

api-prod:
	@echo "🚀 Starting API server (production mode)..."
	@echo "Server will be available at http://localhost:8080"
	@echo ""
	gunicorn app:app --bind 0.0.0.0:8080 --workers 2 --threads 4 --timeout 300

test-api: test-data
	@echo "🧪 Testing API endpoints..."
	@echo ""
	./test_api.sh

deploy:
	@echo "🚀 Deploying to Cloud Run..."
	./cloud/deploy.sh

clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf sample_data/*.xlsx
	@echo "✅ Cleanup complete!"

# Development helpers
lint:
	@echo "🔍 Running linters..."
	@echo "Note: Install flake8 or ruff for linting"
	# flake8 . --max-line-length=100

format:
	@echo "✨ Formatting code..."
	@echo "Note: Install black for formatting"
	# black .

venv:
	@echo "🐍 Creating virtual environment..."
	python3 -m venv venv
	@echo "✅ Virtual environment created!"
	@echo "Activate with: source venv/bin/activate"

