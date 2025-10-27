# Google Cloud Platform Setup Guide

This guide will help you set up GCP credentials to avoid 505 errors and enable full functionality.

## 🎯 Quick Setup (5 Minutes)

### Option 1: Service Account (Recommended for Production)

#### Step 1: Create a GCP Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a Project" → "New Project"
3. Enter project name (e.g., "estimate-insight")
4. Note your **Project ID** (you'll need this!)

#### Step 2: Enable Required APIs
```bash
# Set your project
gcloud config set project YOUR-PROJECT-ID

# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Enable Firestore API
gcloud services enable firestore.googleapis.com

# Enable Cloud Run (if deploying)
gcloud services enable run.googleapis.com
```

Or enable via console:
- [Enable Vertex AI](https://console.cloud.google.com/apis/library/aiplatform.googleapis.com)
- [Enable Firestore](https://console.cloud.google.com/apis/library/firestore.googleapis.com)

#### Step 3: Create Service Account
```bash
# Create service account
gcloud iam service-accounts create estimate-insight \
    --display-name="Estimate Insight Service Account"

# Grant necessary roles
gcloud projects add-iam-policy-binding YOUR-PROJECT-ID \
    --member="serviceAccount:estimate-insight@YOUR-PROJECT-ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding YOUR-PROJECT-ID \
    --member="serviceAccount:estimate-insight@YOUR-PROJECT-ID.iam.gserviceaccount.com" \
    --role="roles/datastore.user"

# Create and download key
gcloud iam service-accounts keys create ~/estimate-insight-key.json \
    --iam-account=estimate-insight@YOUR-PROJECT-ID.iam.gserviceaccount.com
```

Or via console:
1. Go to [IAM & Admin > Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Click "Create Service Account"
3. Name: `estimate-insight`
4. Grant roles:
   - **Vertex AI User** (`roles/aiplatform.user`)
   - **Cloud Datastore User** (`roles/datastore.user`)
5. Click "Done"
6. Click on the service account → "Keys" tab → "Add Key" → "Create New Key" → JSON
7. Save the JSON file securely (e.g., `~/estimate-insight-key.json`)

#### Step 4: Initialize Firestore
1. Go to [Firestore Console](https://console.cloud.google.com/firestore)
2. Click "Create Database"
3. Choose **"Native Mode"**
4. Select region (recommended: `us-central1`)
5. Start in **Production Mode**

#### Step 5: Configure Your .env File
```bash
# Copy the example
cp .env.example .env

# Edit .env with your details
nano .env  # or use any text editor
```

Set these values:
```bash
GCP_PROJECT_ID=your-actual-project-id
GCP_REGION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/estimate-insight-key.json
```

### Option 2: User Account (Easiest for Local Development)

If you already have `gcloud` CLI installed:

```bash
# Authenticate
gcloud auth application-default login

# Set project
gcloud config set project YOUR-PROJECT-ID

# Enable APIs (see Step 2 above)

# Create .env file
cp .env.example .env
```

Edit `.env`:
```bash
GCP_PROJECT_ID=your-actual-project-id
GCP_REGION=us-central1
# Leave GOOGLE_APPLICATION_CREDENTIALS commented out
```

## ✅ Verify Setup

Test your credentials:

```bash
# Check if authenticated
gcloud auth list

# Check if APIs are enabled
gcloud services list --enabled | grep -E 'aiplatform|firestore'

# Test Vertex AI access
gcloud ai models list --region=us-central1 2>&1 | head
```

## 🚀 Run the Application

```bash
# Make sure .env is configured
cat .env

# Install dependencies (if not done)
pip3 install -r requirements.txt

# Start the server
python3 web/app.py
```

Visit: http://localhost:8080

## 🔧 Troubleshooting

### Error: "Permission denied" or 505

**Cause:** Service account lacks permissions

**Fix:**
```bash
# Grant missing permissions
gcloud projects add-iam-policy-binding YOUR-PROJECT-ID \
    --member="serviceAccount:estimate-insight@YOUR-PROJECT-ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"
```

### Error: "API not enabled"

**Fix:**
```bash
gcloud services enable aiplatform.googleapis.com
gcloud services enable firestore.googleapis.com
```

### Error: "Project not found"

**Fix:**
- Verify `GCP_PROJECT_ID` in `.env` matches exactly (check console)
- Ensure you have access to the project
- Run: `gcloud projects list` to see available projects

### Error: "Could not load default credentials"

**Fix:**
- If using service account: Check `GOOGLE_APPLICATION_CREDENTIALS` path is correct
- If using user auth: Run `gcloud auth application-default login`
- Verify the JSON key file exists and is readable

### Error: "Failed to generate insight with Gemini"

**Fix:**
- Check if Vertex AI API is enabled
- Verify your region supports Gemini (use `us-central1`)
- Test with: `gcloud ai models list --region=us-central1`

## 💰 Cost Estimates

Typical usage costs:
- **Gemini 1.5 Pro**: ~$0.01 per analysis
- **Firestore**: ~$0.0001 per write/read
- **Cloud Run**: Free tier covers most dev usage
- **Total**: ~$0.01-0.02 per analysis

Free tier includes:
- Vertex AI: $300 free credits for 90 days
- Firestore: 1GB storage free, 50k reads/day free
- Cloud Run: 2 million requests/month free

## 🔐 Security Best Practices

1. **Never commit credentials to git**
   ```bash
   # .gitignore already includes:
   .env
   *.json (service account keys)
   ```

2. **Rotate keys regularly**
   ```bash
   # Delete old key
   gcloud iam service-accounts keys delete KEY_ID \
       --iam-account=estimate-insight@YOUR-PROJECT-ID.iam.gserviceaccount.com
   
   # Create new key
   gcloud iam service-accounts keys create ~/new-key.json \
       --iam-account=estimate-insight@YOUR-PROJECT-ID.iam.gserviceaccount.com
   ```

3. **Use principle of least privilege**
   - Only grant necessary roles
   - Use separate service accounts for dev/prod

4. **Monitor usage**
   - Set up billing alerts in GCP Console
   - Review IAM permissions regularly

## 📚 Additional Resources

- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Firestore Documentation](https://cloud.google.com/firestore/docs)
- [Service Account Best Practices](https://cloud.google.com/iam/docs/best-practices-service-accounts)
- [GCP Free Tier](https://cloud.google.com/free)

## 🆘 Still Having Issues?

1. Check `PROJECT_LOG.md` for known issues
2. Review error logs: The app prints helpful warnings
3. Test individual components:
   ```bash
   # Test with quick mode (no Gemini)
   python main.py estimate.xlsx actual.xlsx --quick
   ```

---

**Need help?** Open an issue or check the troubleshooting section above.

