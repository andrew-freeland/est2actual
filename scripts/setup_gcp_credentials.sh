#!/bin/bash
# ============================================
# GCP Credentials Setup Script
# ============================================
# This script automates the entire GCP setup process

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  GCP Credentials Setup for Estimate Insight${NC}"
echo -e "${BLUE}============================================${NC}\n"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}✗ gcloud CLI not found${NC}"
    echo -e "${YELLOW}Please install: https://cloud.google.com/sdk/docs/install${NC}"
    exit 1
fi

echo -e "${GREEN}✓ gcloud CLI found${NC}\n"

# Get current project
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)

if [ -z "$CURRENT_PROJECT" ] || [ "$CURRENT_PROJECT" == "(unset)" ]; then
    echo -e "${YELLOW}No GCP project currently set.${NC}"
    echo -e "\nPlease enter your GCP Project ID:"
    echo -e "(Find it at: https://console.cloud.google.com/)"
    read -p "Project ID: " PROJECT_ID
    
    # Set the project
    gcloud config set project "$PROJECT_ID"
else
    echo -e "${BLUE}Current project: ${CURRENT_PROJECT}${NC}"
    read -p "Use this project? (y/n): " USE_CURRENT
    
    if [[ $USE_CURRENT =~ ^[Yy]$ ]]; then
        PROJECT_ID="$CURRENT_PROJECT"
    else
        read -p "Enter your Project ID: " PROJECT_ID
        gcloud config set project "$PROJECT_ID"
    fi
fi

echo -e "\n${GREEN}✓ Using project: ${PROJECT_ID}${NC}\n"

# Get region
REGION=${GCP_REGION:-us-central1}
echo -e "${BLUE}Region: ${REGION}${NC}"
echo -e "(Change by setting GCP_REGION environment variable)\n"

# Step 1: Enable APIs
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Step 1: Enabling required APIs...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo "Enabling Vertex AI API..."
gcloud services enable aiplatform.googleapis.com --project="$PROJECT_ID"
echo -e "${GREEN}✓ Vertex AI API enabled${NC}\n"

echo "Enabling Firestore API..."
gcloud services enable firestore.googleapis.com --project="$PROJECT_ID"
echo -e "${GREEN}✓ Firestore API enabled${NC}\n"

echo "Enabling Cloud Run API (for deployment)..."
gcloud services enable run.googleapis.com --project="$PROJECT_ID"
echo -e "${GREEN}✓ Cloud Run API enabled${NC}\n"

# Step 2: Create Service Account
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Step 2: Creating service account...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

SERVICE_ACCOUNT_NAME="estimate-insight"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# Check if service account exists
if gcloud iam service-accounts describe "$SERVICE_ACCOUNT_EMAIL" --project="$PROJECT_ID" &>/dev/null; then
    echo -e "${YELLOW}Service account already exists: ${SERVICE_ACCOUNT_EMAIL}${NC}"
    read -p "Use existing service account? (y/n): " USE_EXISTING
    
    if [[ ! $USE_EXISTING =~ ^[Yy]$ ]]; then
        read -p "Enter new service account name: " SERVICE_ACCOUNT_NAME
        SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
    fi
fi

# Create service account if it doesn't exist
if ! gcloud iam service-accounts describe "$SERVICE_ACCOUNT_EMAIL" --project="$PROJECT_ID" &>/dev/null; then
    gcloud iam service-accounts create "$SERVICE_ACCOUNT_NAME" \
        --display-name="Estimate Insight Service Account" \
        --project="$PROJECT_ID"
    echo -e "${GREEN}✓ Service account created: ${SERVICE_ACCOUNT_EMAIL}${NC}\n"
else
    echo -e "${GREEN}✓ Using service account: ${SERVICE_ACCOUNT_EMAIL}${NC}\n"
fi

# Step 3: Grant Permissions
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Step 3: Granting permissions...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo "Granting Vertex AI User role..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/aiplatform.user" \
    --condition=None \
    --quiet
echo -e "${GREEN}✓ Vertex AI User role granted${NC}\n"

echo "Granting Cloud Datastore User role..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/datastore.user" \
    --condition=None \
    --quiet
echo -e "${GREEN}✓ Cloud Datastore User role granted${NC}\n"

# Step 4: Create Service Account Key
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Step 4: Creating service account key...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

KEY_FILE="${HOME}/estimate-insight-key.json"
echo "Key will be saved to: ${KEY_FILE}"

gcloud iam service-accounts keys create "$KEY_FILE" \
    --iam-account="$SERVICE_ACCOUNT_EMAIL" \
    --project="$PROJECT_ID"

echo -e "${GREEN}✓ Service account key created${NC}"
echo -e "${YELLOW}⚠️  Keep this file secure! Never commit to git!${NC}\n"

# Step 5: Check Firestore
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Step 5: Checking Firestore database...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# Note: Firestore database creation requires manual action in console
echo -e "${YELLOW}⚠️  Firestore database must be created manually${NC}"
echo -e "Visit: https://console.cloud.google.com/firestore?project=${PROJECT_ID}"
echo -e "\nSteps:"
echo -e "  1. Click 'Create Database'"
echo -e "  2. Select 'Native Mode'"
echo -e "  3. Choose region: ${REGION}"
echo -e "  4. Start in 'Production Mode'\n"

read -p "Press Enter after creating Firestore database (or if already created)..."

# Step 6: Create .env file
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Step 6: Creating .env file...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

if [ -f ".env" ]; then
    echo -e "${YELLOW}.env file already exists${NC}"
    read -p "Overwrite? (y/n): " OVERWRITE
    if [[ ! $OVERWRITE =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Skipping .env creation${NC}"
        echo -e "${BLUE}Manually add these values to your .env:${NC}"
        echo -e "GCP_PROJECT_ID=${PROJECT_ID}"
        echo -e "GCP_REGION=${REGION}"
        echo -e "GOOGLE_APPLICATION_CREDENTIALS=${KEY_FILE}"
    else
        cat > .env << EOF
# GCP Configuration
GCP_PROJECT_ID=${PROJECT_ID}
GCP_REGION=${REGION}
GOOGLE_APPLICATION_CREDENTIALS=${KEY_FILE}

# Flask Configuration
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
FLASK_ENV=development
PORT=8080

# Service Configuration
SERVICE_NAME=estimate-insight-agent
EOF
        echo -e "${GREEN}✓ .env file created${NC}\n"
    fi
else
    cat > .env << EOF
# GCP Configuration
GCP_PROJECT_ID=${PROJECT_ID}
GCP_REGION=${REGION}
GOOGLE_APPLICATION_CREDENTIALS=${KEY_FILE}

# Flask Configuration
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
FLASK_ENV=development
PORT=8080

# Service Configuration
SERVICE_NAME=estimate-insight-agent
EOF
    echo -e "${GREEN}✓ .env file created${NC}\n"
fi

# Final Summary
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  Setup Complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "${GREEN}✓ Project: ${PROJECT_ID}${NC}"
echo -e "${GREEN}✓ Service Account: ${SERVICE_ACCOUNT_EMAIL}${NC}"
echo -e "${GREEN}✓ Key File: ${KEY_FILE}${NC}"
echo -e "${GREEN}✓ APIs Enabled: Vertex AI, Firestore, Cloud Run${NC}"
echo -e "${GREEN}✓ .env configured${NC}\n"

echo -e "${BLUE}Next Steps:${NC}"
echo -e "1. Test credentials:"
echo -e "   ${YELLOW}python3 scripts/test_credentials.py${NC}\n"
echo -e "2. Start the application:"
echo -e "   ${YELLOW}python3 web/app.py${NC}\n"
echo -e "3. Visit: ${YELLOW}http://localhost:8080${NC}\n"

echo -e "${YELLOW}⚠️  Security reminder:${NC}"
echo -e "   - Never commit ${KEY_FILE} to git"
echo -e "   - Never commit .env to git"
echo -e "   - Both are already in .gitignore\n"

