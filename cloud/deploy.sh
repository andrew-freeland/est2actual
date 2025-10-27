#!/bin/bash
# Deploy to Google Cloud Run

set -e

echo "🚀 Deploying Estimate Insight Agent Pro to Cloud Run"
echo "======================================================"
echo

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "❌ .env file not found. Run scripts/setup_gcp.sh first."
    exit 1
fi

if [ -z "$GCP_PROJECT_ID" ]; then
    echo "❌ GCP_PROJECT_ID not set in .env"
    exit 1
fi

SERVICE_NAME="${SERVICE_NAME:-estimate-insight-agent}"
REGION="${GCP_REGION:-us-central1}"
DEPLOYMENT_MODE="${DEPLOYMENT_MODE:-web}"  # Options: web, api

echo "📋 Configuration:"
echo "   Project: $GCP_PROJECT_ID"
echo "   Service: $SERVICE_NAME"
echo "   Region: $REGION"
echo "   Mode: $DEPLOYMENT_MODE (web UI with integrated API)"
echo

# Set environment variables based on deployment mode
ENV_VARS="GCP_PROJECT_ID=$GCP_PROJECT_ID,GCP_REGION=$REGION,FLASK_ENV=production"

# Build and deploy
echo "🔨 Building and deploying to Cloud Run..."
echo "   Note: Deploying web UI (includes upload form + backend API)"

gcloud run deploy "$SERVICE_NAME" \
    --source . \
    --platform managed \
    --region "$REGION" \
    --project "$GCP_PROJECT_ID" \
    --allow-unauthenticated \
    --set-env-vars "$ENV_VARS" \
    --memory 1Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 0

echo
echo "✅ Deployment complete!"
echo
echo "🌐 Service URL:"
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region "$REGION" \
    --project "$GCP_PROJECT_ID" \
    --format="value(status.url)")

echo "$SERVICE_URL"
echo
echo "📝 Quick Test:"
echo "   1. Visit the web UI: $SERVICE_URL"
echo "   2. Upload estimate.xlsx and actual.xlsx files"
echo "   3. View AI-generated insights and charts"
echo
echo "💡 API Endpoints (if needed):"
echo "   Health Check: $SERVICE_URL/"
echo "   Analysis API: $SERVICE_URL/analyze (POST)"
echo "   Patterns View: $SERVICE_URL/patterns"
echo
echo "🔐 Note: Service is configured for unauthenticated access."
echo "   For production, consider adding authentication."

