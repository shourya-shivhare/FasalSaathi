# FasalSaathi — User Guide 🌾

> **FasalSaathi** (फसल साथी) — Your AI farming companion.  
> This guide will help you get the most out of every section of the app.

---

## Getting Started

### 1. Sign Up & Login

Open FasalSaathi and create your account with your name, email, and phone number. Once registered, you'll be asked to complete a short onboarding.

### 2. Onboarding — Tell Us About Your Farm

During onboarding, you'll fill in:

- **State & District** — so we can give you location-specific advice
- **Land Size** (in acres)
- **Crops You Grow** — e.g., Wheat, Rice, Mustard
- **Age & Gender** — helps us find government schemes you're eligible for

> 💡 The more accurate your profile, the better our AI recommendations will be.

---

## App Sections

### 🏠 Dashboard

This is your home screen. At a glance, you can see:

- **Greeting & Weather** — Current temperature and weather condition for your area, displayed right at the top.
- **Farm Stats** — How many crops you're monitoring, pests detected in the last 30 days, total scans done, and total land area.
- **Quick Actions** — Two big buttons:
  - **Scan Your Crop** — Jump straight to pest detection.
  - **Gov Schemes** — Find government schemes you may be eligible for.
- **Weather Card** — Detailed weather info including humidity and wind.
- **Soil Health** — If you've added field data, see your soil's Nitrogen, Phosphorus, Potassium levels, and pH.
- **Alerts** — The app automatically generates alerts based on your data — weather warnings, low nutrient levels, or recent pest detections. If everything looks good, you'll see an "All Clear" message.

---

### 🔍 Pest Scanner (Scan Your Crop)

This is one of the most powerful features. Here's how to use it:

1. **Upload a Photo** — Take a clear photo of the affected part of your crop (leaf, stem, fruit). You can drag-and-drop, click to upload, or use your phone camera directly.
2. **Tap "Scan for Pests"** — Our AI (YOLOv8 model) analyzes the image instantly.
3. **See Results** — You'll get:
   - **Pest name** and how many were detected
   - **Severity level** — High, Medium, or Low
   - **Treatment Recommendations** — Step-by-step advice on what spray or remedy to use
4. **Chat with AI Expert** — After scanning, tap this button to ask follow-up questions. The AI already knows what pest was found, so it can give personalized advice without you having to explain again.

> 📸 **Tips:** Take photos in good natural light, focus on the affected leaves, and avoid blurry images for best results.

Your scan history is saved automatically. You can always see your recent scans on the right side panel.

---

### 💬 AI Chat (FasalSaathi AI)

Think of this as having a farming expert in your pocket. You can ask anything:

- "Mere gehun mein peele patte kyon aa rahe hain?" (Why are my wheat leaves turning yellow?)
- "Kab paani dena chahiye?" (When should I irrigate?)
- "Market prices today?"
- "What spray should I use for aphids?"
- "Subsidy info chahiye" (I need subsidy information)

**How it works:**
- Type your question or tap one of the quick suggestion buttons at the bottom.
- The AI understands **Hindi, English, and Hinglish** — write in whatever language is comfortable.
- If you've recently scanned a crop for pests, the AI already has that context and will refer to it in its answers.
- If you've run crop recommendations or scheme searches, the chat AI knows about those results too and can answer follow-ups.

**Special command:**
- Type `/analyze <your question>` to trigger a full AI pipeline that runs crop and scheme recommendations together and gives you a comprehensive summary.

---

### 🌱 Crop Suggestions

Get AI-recommended crops based on your specific conditions:

1. **Your Farm Details** are auto-filled from your profile (state, district, land size, past crops). You can edit any field to try different scenarios.
2. **Select your soil type** (Loamy, Alluvial, Clayey, Sandy, etc.)
3. **Choose the season** — Kharif (monsoon), Rabi (winter), or Zaid (summer)
4. **Set water availability** — Low, Moderate, High, or Irrigated
5. **Tap "Get Crop Recommendations"**

Results show:
- **Crop name** with a confidence score (e.g., Wheat — 92% Highly Recommended)
- **Why this crop** is good for you — the AI explains the reasoning
- **Estimated yield per acre** and **water requirement**
- If you had a pest detected earlier, the AI avoids recommending crops that are vulnerable to that pest

---

### 🏛️ Government Schemes

Find government subsidies, loans, and insurance you're eligible for:

1. **Your profile is auto-filled** — state, district, age, gender, income, crops.
2. **Tap "Find Eligible Schemes"**
3. **Results show** each matched scheme with:
   - **Eligibility Score** — How well you match (e.g., 85% Highly Eligible)
   - **Why recommended** — Personalized explanation
   - **Expand for details** — Benefits, category tags, and a direct link to apply

> The AI matches your profile (age, income, state, crops, farmer category) against 25+ central and state government schemes.

---

### 📊 Market Prices

Stay updated on mandi prices so you can sell at the right time:

- **Current Mandi Price** — The latest price of your crop at your nearest mandi, compared against the government MSP (Minimum Support Price).
- **Price Trend Chart** — See how prices have moved over 7, 30, or 90 days.
- **MSP Reference Table** — Compare MSP vs. market price for all major crops (Wheat, Rice, Soybean, Cotton, Maize, Mustard, Gram, Sunflower).
- **Market Insights** — AI-generated tips like "Best sell window: next 2 weeks before harvest season."

---

### 👤 Profile

Manage your farming profile and personal details:

- Update your **name, phone, email**
- Change your **state, district, land size, crops grown**
- Modify **farmer category** (marginal, small, medium, large)
- Update **age, gender, annual income** — these improve scheme matching accuracy

---

## Tips for Getting the Best Results

1. **Complete your profile** — The more details you provide (state, district, land size, crops, income), the more personalized the AI recommendations will be.
2. **Scan regularly** — Scan your crops every 1-2 weeks during growing season. Early pest detection saves crops.
3. **Use chat after scanning** — The AI expert already knows your pest detection results and can give targeted follow-up advice.
4. **Check schemes periodically** — New government schemes are added regularly. Re-check eligibility after updating your profile.
5. **Monitor market prices** — Check the Market page before selling to maximize your returns.
6. **Try both languages** — The AI understands Hindi and English equally well, so ask in whichever feels natural.

---

## Quick Reference

| I want to... | Go to... |
|---|---|
| Check my crop for pests | Pest Scanner (🔍) |
| Ask a farming question | AI Chat (💬) |
| Know what to grow this season | Crop Suggestions (🌱) |
| Find government subsidies | Government Schemes (🏛️) |
| Check mandi prices before selling | Market Prices (📊) |
| Update my farm details | Profile (👤) |
