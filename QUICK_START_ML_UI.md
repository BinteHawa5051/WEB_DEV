# Quick Start - ML Predictions UI 🚀

## Access the New Design

**URL**: http://localhost:5173/ml-predictions

**Or**: Click "ML Predictions" in the sidebar (Brain icon 🧠)

## What You'll See

### 1. Hero Section (Top)
```
┌─────────────────────────────────────────────┐
│  🧠  AI-Powered Case Analysis               │
│      Get intelligent predictions...         │
│                                             │
│  [95% Accuracy] [<1s Time] [3 AI Models]   │
└─────────────────────────────────────────────┘
```

### 2. Form Section (Left/Top)
- **Case Facts**: Large text area for case description
- **Basic Tab**: Essential fields (parties, witnesses, evidence)
- **Advanced Tab**: Fine-tuning (complexity, win rate sliders)
- **Analyze Button**: Purple gradient button with brain icon

### 3. Results Section (Right/Bottom)
After clicking "Analyze Case":

**Summary Card** (Yellow)
- AI-generated summary of the analysis

**Outcome Prediction** (Circular Progress)
- Large percentage (e.g., 66.8%)
- Color-coded: Green (win), Amber (uncertain), Red (loss)
- Shows plaintiff advantage

**Duration Prediction** (Big Numbers)
- Hours estimate (e.g., 23.5 hours)
- Category badge (Quick/Standard/Extended/Complex)
- Breakdown (minutes, sessions, days)

**Judge Recommendations** (Cards)
- Ranked list (#1, #2, #3)
- "Best Match" badge for top judge
- Similarity scores with progress bars

## How to Use

### Step 1: Enter Case Facts
```
Type or paste case description:
"Contract dispute regarding delayed delivery 
of goods causing financial losses..."
```

### Step 2: Fill Basic Information
- Decision Type: Majority Opinion
- Disposition: Affirmed
- Number of Parties: 4
- Number of Witnesses: 5
- Evidence Pages: 120

### Step 3: (Optional) Advanced Settings
Click "Advanced Parameters" tab:
- Adjust complexity slider (0-100%)
- Set lawyer win rate (0-100%)
- Fine-tune other parameters

### Step 4: Analyze
Click the purple "Analyze Case" button

### Step 5: Review Results
- Read the AI summary
- Check outcome probability
- Review duration estimate
- See recommended judges

## Key Features

### 🎨 Visual Design
- Purple gradient theme
- Smooth animations
- Card-based layout
- Professional icons

### 📱 Responsive
- Desktop: Side-by-side layout
- Tablet: Stacked layout
- Mobile: Optimized for touch

### ✨ Interactions
- Hover effects on cards
- Animated progress bars
- Loading spinner
- Toast notifications

### 🎯 Smart Defaults
- Pre-filled with reasonable values
- Sliders show live percentages
- Helpful hints below inputs
- Validation prevents errors

## Tips

### For Best Results
1. **Be Detailed**: More case facts = better predictions
2. **Use Advanced Tab**: Fine-tune for complex cases
3. **Check All Metrics**: Review outcome, duration, and judges
4. **Read Summary**: AI provides context

### Mobile Users
- Use portrait mode for best experience
- Tap to expand sections
- Scroll smoothly through results
- All features available

### Desktop Users
- See form and results side-by-side
- Hover over cards for effects
- Use keyboard shortcuts (Tab, Enter)
- Print-friendly layout

## Color Guide

**Green** = Positive (High win probability, best match)
**Amber** = Moderate (Uncertain outcome, extended duration)
**Red** = Negative (Low win probability, complex case)
**Purple** = Primary (Branding, buttons, accents)
**Blue** = Info (Standard metrics, information)

## Example Workflow

### Simple Case
```
1. Enter: "Property boundary dispute"
2. Parties: 2
3. Witnesses: 2
4. Evidence: 20 pages
5. Click Analyze
6. Result: Quick duration, moderate outcome
```

### Complex Case
```
1. Enter: "Multi-party corporate fraud case..."
2. Parties: 8
3. Witnesses: 15
4. Evidence: 500 pages
5. Advanced: Complexity 90%, Win Rate 75%
6. Click Analyze
7. Result: Extended duration, high outcome probability
```

## Troubleshooting

### No Results?
- Check case facts are filled
- Ensure all required fields have values
- Look for error toast messages

### Slow Loading?
- Check internet connection
- Backend must be running (port 8000)
- Refresh page if needed

### Layout Issues?
- Try different browser
- Clear cache
- Check screen size/zoom

## Browser Support

✅ Chrome/Edge (Recommended)
✅ Firefox
✅ Safari
✅ Mobile browsers

## Need Help?

**API Documentation**: http://localhost:8000/docs
**Backend Status**: Check if port 8000 is running
**Frontend Status**: Check if port 5173 is running

## Summary

The new ML Predictions UI provides:
- Professional, modern design
- Easy-to-use interface
- Beautiful visualizations
- Accurate AI predictions
- Fully responsive layout

**Ready to use! Start analyzing cases now! 🚀**
