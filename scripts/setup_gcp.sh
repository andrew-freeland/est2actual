#!/bin/bash
# Setup script for Google Cloud Platform resources

set -e

echo "🔧 Setting up GCP resources for Estimate Insight Agent Pro"
echo "============================================================"
echo

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Get project ID
read -p "Enter your GCP Project ID: " PROJECT_ID

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Project ID cannot be empty"
    exit 1
fi

echo
echo "📋 Project ID: $PROJECT_ID"
echo

# Set project
echo "Setting active project..."
gcloud config set project "$PROJECT_ID"

# Enable required APIs
echo
echo "🔌 Enabling required APIs..."
gcloud services enable aiplatform.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable run.googleapis.com

# Create Firestore database (if not exists)
echo
echo "🗄️  Setting up Firestore..."
echo "Note: If Firestore is already set up, you may see an error (safe to ignore)"
gcloud firestore databases create --location=us-central1 --type=firestore-native || true

# Authenticate for local development
echo
echo "🔐 Setting up local authentication..."
gcloud auth application-default login

# Update .env file
echo
echo "📝 Creating .env file..."
cat > .env << EOF
# Google Cloud Configuration
GCP_PROJECT_ID=$PROJECT_ID
GCP_REGION=us-central1
FIRESTORE_COLLECTION=project_insights
EOF

echo
echo "✅ Setup complete!"
echo
echo "Next steps:"
echo "1. Install Python dependencies: pip install -r requirements.txt"
echo "2. Create test data: python scripts/create_test_data.py"
echo "3. Run analysis: python main.py sample_data/estimate.xlsx sample_data/actual.xlsx --quick"

