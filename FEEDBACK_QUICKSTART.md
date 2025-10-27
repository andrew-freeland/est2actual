# Feedback Feature - Quick Start Guide

## What's New?

Your Estimate Insight application now has an intelligent feedback system that allows users to rate AI-generated insights and provide detailed comments. This helps improve the quality of future analyses.

## Where to Find It

### 1. Result Page (Detailed Feedback)

After analyzing a project and seeing the AI-Generated Insight:
- Look for **"Provide Feedback on this Insight"** at the bottom of the insight section
- Click the arrow to expand the feedback form
- Select thumbs up or thumbs down
- Optionally add detailed comments
- Click "Submit Feedback"

### 2. Patterns Page (Quick Feedback)

When viewing historical insights:
- Each project card shows an AI insight summary
- At the bottom of each insight, you'll see "Was this insight helpful?"
- Click thumbs up or thumbs down for quick feedback
- No text needed - just one click!

## Features

✅ **Expandable with Arrow** - Keeps the UI clean, expands when needed  
✅ **Thumbs Up/Down** - Quick, intuitive rating system  
✅ **Optional Text Feedback** - Add detailed comments when you want  
✅ **Acknowledgment** - System confirms when feedback is received  
✅ **No Breaking** - Even if feedback fails, the app continues working  
✅ **Intelligent Storage** - All feedback is saved to Firestore for analysis  

## Testing the Feature

### Quick Visual Test
1. Start the web app: `python web/app.py`
2. Upload a project and submit for analysis
3. On the result page, click the feedback arrow
4. Try giving feedback with and without text
5. Go to `/patterns` and try the simple feedback buttons

### Backend Test
Run the test script to verify Firestore integration:
```bash
python scripts/test_feedback.py
```

This will:
- Create test feedback entries
- Retrieve feedback data
- Calculate statistics
- Display results

## How Feedback is Used

The system stores all feedback intelligently in Firestore:

**Immediate Benefits:**
- Track which insights users find helpful
- Identify patterns in negative feedback
- Monitor overall satisfaction rates

**Future Learning:**
- Adjust AI prompts based on feedback patterns
- Improve insight quality over time
- Personalize insights for different user types

## API Reference

### Submit Feedback Endpoint

**POST** `/submit_feedback`

```json
{
  "insight_id": "project_doc_id",
  "feedback_type": "detailed",
  "rating": "thumbs_up",
  "feedback_text": "Optional detailed feedback",
  "metadata": {
    "page": "result",
    "timestamp": "2025-10-27T12:00:00Z"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Thank you for your feedback! We use it to improve our insights.",
  "feedback_id": "firestore_doc_id"
}
```

### Get Feedback Statistics

**GET** `/feedback_stats?insight_id=project_id`

Returns aggregate statistics about feedback.

## Firestore Structure

Collection: `insight_feedback`

```
insight_feedback/
  └── {feedback_id}/
      ├── insight_id: string
      ├── feedback_type: "detailed" | "summary"
      ├── rating: "thumbs_up" | "thumbs_down"
      ├── feedback_text: string
      ├── metadata: object
      ├── created_at: timestamp
      └── version: string
```

## Troubleshooting

### Feedback button not working?
- Check browser console for JavaScript errors
- Ensure you have network connectivity
- Verify GCP_PROJECT_ID is set correctly

### Feedback not saving?
- Check Firestore permissions
- Verify credentials are configured: `gcloud auth application-default login`
- Run test script to diagnose: `python scripts/test_feedback.py`

### No feedback showing on patterns page?
- Ensure you've enabled "Save to Memory" when analyzing projects
- Check that projects exist in Firestore
- Verify the patterns page is loading project data correctly

## Privacy & Security

- Feedback is tied to insight IDs, not user IDs (privacy-preserving)
- No personally identifiable information is collected
- All data is stored securely in Firestore with proper IAM rules
- Feedback is optional - users can skip it entirely

## Next Steps

### For Users
- Start providing feedback on insights you receive
- Help improve the AI by sharing what works and what doesn't
- Use detailed comments to explain your ratings

### For Developers
- Monitor feedback statistics: `GET /feedback_stats`
- Review negative feedback: `get_negative_feedback_for_review()`
- Analyze patterns to improve prompt engineering
- Consider adding rate limiting for production use

## Questions?

See the full documentation in `FEEDBACK_FEATURE.md` for technical details, implementation notes, and future enhancement plans.

