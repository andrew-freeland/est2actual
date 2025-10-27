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

SERVICE_NAME="estimate-insight-agent"
REGION="${GCP_REGION:-us-central1}"

echo "📋 Configuration:"
echo "   Project: $GCP_PROJECT_ID"
echo "   Service: $SERVICE_NAME"
echo "   Region: $REGION"
echo

# Build and deploy
echo "🔨 Building and deploying to Cloud Run..."

gcloud run deploy "$SERVICE_NAME" \
    --source . \
    --platform managed \
    --region "$REGION" \
    --project "$GCP_PROJECT_ID" \
    --allow-unauthenticated \
    --set-env-vars "GCP_PROJECT_ID=$GCP_PROJECT_ID,GCP_REGION=$REGION" \
    --memory 1Gi \
    --timeout 300

echo
echo "✅ Deployment complete!"
echo
echo "Service URL:"
gcloud run services describe "$SERVICE_NAME" \
    --region "$REGION" \
    --project "$GCP_PROJECT_ID" \
    --format="value(status.url)"

