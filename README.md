<div align="center">

<h1>
  📊 SNAPBOARD
</h1>

<p><strong>India-First AI Business Analytics Dashboard</strong></p>

<p>
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/Flask-3.0-black?style=for-the-badge&logo=flask" />
  <img src="https://img.shields.io/badge/AI-Gemini%20%2B%20Groq-orange?style=for-the-badge&logo=google" />
  <img src="https://img.shields.io/badge/Made%20for-Bharat%20🇮🇳-FF6B35?style=for-the-badge" />
</p>

<p>
  Upload your Razorpay / Zoho / Shopify CSV → AI detects your business intent →<br/>
  Live dashboard in ₹ &amp; Indian format → WhatsApp digest → Investor-ready PDF.<br/>
  Ready in under 30 seconds.
</p>

</div>

---

## Table of Contents

1. [What is SNAPBOARD?](#-what-is-snapboard)
2. [Features](#-features)
3. [Who Can Use It](#-who-can-use-it)
4. [What It Can't Do](#-what-it-cant-do)
5. [Unique Selling Points](#-unique-selling-points)
6. [Tech Stack](#-tech-stack)
7. [Local Setup — From Scratch](#-local-setup--from-scratch)
8. [Supabase Setup (Database & Auth)](#-supabase-setup-database--auth)
9. [API Keys Setup](#-api-keys-setup)
10. [Environment Variables Reference](#-environment-variables-reference)
11. [Running the App](#-running-the-app)
12. [Sample CSV Files to Test With](#-sample-csv-files-to-test-with)
13. [Project Structure](#-project-structure)
14. [UI/UX Design Philosophy](#-uiux-design-philosophy)

---

## 🇮🇳 What is SNAPBOARD?

SNAPBOARD is a **Flask + Vanilla JS** web application built exclusively for Indian founders, SMEs, and D2C brands. It turns raw business CSVs (exported from Razorpay, Zoho, Shopify, or any generic spreadsheet) into a live, interactive analytics dashboard — with no code, no BI tools, and no data science background required.

All numbers are in **₹ (Indian Rupees)**, displayed in the **Lakh/Crore** system (e.g. ₹2.3Cr, ₹50L), dates are always **DD/MM/YYYY**, and the app understands **Hinglish column names** (like `Bill_tareekh`, `Daam`, `Cheez`, `Sheher`).

---

## ✨ Features

### 📤 Data Ingestion
- Upload **CSV** or **Excel (.xlsx / .xls)** files
- Auto-detects source platform: **Razorpay**, **Zoho**, **Shopify**, or **Generic**
- Auto-maps **Hinglish column names** to English equivalents
- Handles messy data: strips ₹ symbols, commas, spaces from numeric columns

### 🤖 AI-Powered Analysis
- **Gemini 1.5 Flash** detects your business intent (Revenue / Churn / ROAS / Ops / Mixed)
- Generates a one-sentence business context description in Indian startup language
- **Groq Llama 3.1** powers a natural-language chat editor — type "show top 5 cities" or "pie chart for products"

### 📊 Live Dashboard
- **KPI Cards**: Total Revenue, Total Orders, Average Order Value, Month-on-Month Growth
- **Charts** (powered by Chart.js 4):
  - Monthly Revenue bar/line chart with toggle
  - Daily Revenue trend (last 30 days)
  - Top 5 Products by Revenue (horizontal bar)
  - Top 5 Cities by Revenue (doughnut)
- All charts switch type (bar ↔ line) with one click

### 🧾 GST Toggle
- Toggle between **gross** and **net (ex-GST)** revenue on the fly
- Supports Indian GST slabs: **5%, 12%, 18%, 28%**
- Shows GST amount separated out

### 📄 Investor PDF Export
- One-click export of the full dashboard as a **professional A4 PDF**
- Built with **ReportLab** (no external system dependencies)
- Includes: brand header, KPI cards, monthly revenue table, top products, top cities, Hinglish mapping, footer

### 📲 WhatsApp Digest
- Send an instant **Hinglish WhatsApp summary** to any Indian mobile number
- Powered by **Twilio WhatsApp API**
- Includes Revenue, Orders, Avg Order Value, MoM Growth — all in ₹

### 🗓️ Scheduled Daily Digest
- **APScheduler** fires at **8:00 AM IST** every day
- Hooks into Supabase subscriber list (ready for production wiring)

### 🔗 Shareable Dashboard Links
- Every dashboard gets a unique URL (`/dashboard/<id>`)
- One-click copy-to-clipboard share button

### 💬 Natural Language Chart Editing
- Type in plain English or Hinglish to modify your dashboard
- AI understands: filter by date range, change chart type, highlight specific products/cities

---

## 👥 Who Can Use It

| User | Use Case |
|------|----------|
| **D2C Founders** | Track Razorpay revenue, top products, city-wise sales |
| **Shopify Store Owners** | Analyse order trends, MoM growth, city performance |
| **CA / Finance Teams** | Export investor-ready PDFs with GST-adjusted numbers |
| **Zoho Users** | Drop in Zoho invoice CSVs for instant analytics |
| **Early-stage Startups** | No BI tool budget? Use SNAPBOARD free, self-hosted |
| **Operations Managers** | Track daily dispatch, inventory patterns (generic CSV) |
| **WhatsApp-native founders** | Get a daily digest on WhatsApp without opening any app |

---

## 🚫 What It Can't Do

- ❌ **Real-time data sync** — it does not connect live to your Razorpay / Shopify / Zoho API; you need to export and upload a CSV manually
- ❌ **Multi-user authentication** — there is no login/signup system; dashboards live in-memory (lost on server restart unless Supabase persistence is wired)
- ❌ **Advanced BI features** — no cohort analysis, funnel tracking, attribution modelling, or SQL querying
- ❌ **Chart customisation beyond presets** — you can switch bar/line/pie via chat, but you cannot drag-resize or build fully custom charts
- ❌ **Automated WhatsApp digest delivery** — the scheduled job runs but the Supabase subscriber lookup is a no-op stub; requires your own production wiring
- ❌ **Large files** — very large CSVs (>100k rows) may be slow; no streaming or background processing
- ❌ **Multi-currency** — designed exclusively for ₹ INR; no USD, EUR, or crypto support
- ❌ **Historical comparison** — compares only the last two months (MoM growth); no YoY or custom period comparison

---

## 💎 Unique Selling Points

1. **Hinglish-native** — the only analytics tool that understands `Bill_tareekh`, `Daam`, `Cheez`, `Sheher` out of the box
2. **India-number system first** — ₹2.3Cr, ₹50L, ₹10K — never "2,300,000" Western format
3. **DD/MM/YYYY dates everywhere** — no configuration, no ambiguity for Indian users
4. **Dual AI engines** — Gemini for intent detection, Groq for conversational chart editing
5. **Platform auto-detection** — recognises Razorpay, Zoho, and Shopify exports automatically
6. **GST-aware** — built-in 5/12/18/28% GST toggle, the only analytics dashboard that separates tax natively
7. **Zero-dependency PDF** — professional investor reports with no system libraries (unlike WeasyPrint which needed Cairo/Pango)
8. **WhatsApp-first notifications** — India's preferred messaging channel, not email
9. **No-login, instant use** — upload CSV → get dashboard URL in under 30 seconds, no account required
10. **Dark, mobile-first UI** — works perfectly on a phone at 375px; designed for founders on the go

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+, Flask 3.0 |
| Data processing | Pandas 2.1, OpenPyXL, xlrd |
| AI — Intent | Google Gemini 1.5 Flash (`google-generativeai`) |
| AI — Chat | Groq Llama 3.1 8B Instant (`groq`) |
| PDF generation | ReportLab 4 (Platypus engine) |
| WhatsApp | Twilio WhatsApp API |
| Scheduler | APScheduler 3 (IST timezone via pytz) |
| Database (optional) | Supabase (PostgreSQL + Auth) |
| Frontend | Vanilla JS, Chart.js 4.4 |
| Styling | Plain CSS (custom properties, mobile-first) |
| Server | Gunicorn (production) / Flask dev server (local) |

---

## 💻 Local Setup — From Scratch

### Prerequisites

Make sure the following are installed on your machine:

```bash
# Check Python version (need 3.10 or higher)
python3 --version

# Check pip
pip3 --version

# Check Git
git --version
```

If Python is not installed, download it from [python.org/downloads](https://www.python.org/downloads/) (choose 3.10+).

---

### Step 1 — Clone the Repository

```bash
git clone https://github.com/SachinGupta98/Snapboard.git
cd Snapboard
```

---

### Step 2 — Create a Virtual Environment

```bash
# Create a virtual environment named .venv
python3 -m venv .venv

# Activate it
# On macOS / Linux:
source .venv/bin/activate

# On Windows (Command Prompt):
.venv\Scripts\activate.bat

# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
```

You should see `(.venv)` in your terminal prompt.

---

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

This installs Flask, Pandas, Gemini, Groq, Twilio, ReportLab, Supabase, APScheduler, and all other dependencies.

---

### Step 4 — Create Your `.env` File

```bash
cp .env.example .env
```

Now open `.env` in your editor and fill in your keys (see [API Keys Setup](#-api-keys-setup) and [Supabase Setup](#-supabase-setup-database--auth) sections below):

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...
GEMINI_API_KEY=AIza...
GROQ_API_KEY=gsk_...
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
SECRET_KEY=any-random-32-char-string
APP_URL=http://localhost:5000
```

> **Tip:** SNAPBOARD works without Supabase, Twilio, Gemini, and Groq in minimal mode — file upload and basic metrics will still work. The app gracefully degrades: AI falls back to `"revenue"` intent, WhatsApp shows an error, PDF still works.

---

### Step 5 — Run the App

```bash
python app.py
```

You should see:

```
 * Running on http://0.0.0.0:5000
 * Debug mode: off
```

Open your browser at **http://localhost:5000** 🎉

To enable debug/auto-reload mode:

```bash
FLASK_DEBUG=1 python app.py
```

---

## 🗄 Supabase Setup (Database & Auth)

Supabase is **optional** for local development — the app stores dashboards in-memory without it. For production or persistence, follow these steps.

### Step 1 — Create a Supabase Account

1. Go to [supabase.com](https://supabase.com) and click **Start your project**
2. Sign up with GitHub or email
3. Click **New project**
4. Fill in:
   - **Project name**: `snapboard`
   - **Database password**: choose a strong password (save it!)
   - **Region**: `ap-south-1` (Mumbai — closest to India)
5. Click **Create new project** and wait ~2 minutes for provisioning

---

### Step 2 — Get Your API Keys

1. In your Supabase dashboard, go to **Settings → API**
2. Copy the following and paste into your `.env`:

| `.env` variable | Where to find it |
|----------------|-----------------|
| `SUPABASE_URL` | "Project URL" (e.g. `https://abcxyz.supabase.co`) |
| `SUPABASE_ANON_KEY` | "anon / public" key under "Project API keys" |
| `SUPABASE_SERVICE_KEY` | "service_role / secret" key under "Project API keys" |

> ⚠️ Never commit `SUPABASE_SERVICE_KEY` to Git — it has admin access to your database.

---

### Step 3 — Create Database Tables

In your Supabase dashboard, go to **SQL Editor** and run the following SQL:

```sql
-- Dashboards table (for persisting uploaded dashboard data)
create table public.dashboards (
  id           text primary key,
  filename     text,
  platform     text,
  intent       text,
  description  text,
  metrics      jsonb,
  row_count    integer,
  created_at   timestamptz default now(),
  gst_rate     numeric default 18,
  gst_included boolean default false
);

-- Digest subscribers table (for scheduled WhatsApp digest)
create table public.digest_subscribers (
  id           uuid primary key default gen_random_uuid(),
  phone        text not null unique,
  dashboard_id text references public.dashboards(id),
  active       boolean default true,
  created_at   timestamptz default now()
);

-- Enable Row Level Security
alter table public.dashboards enable row level security;
alter table public.digest_subscribers enable row level security;

-- Allow anonymous read/write (adjust for production)
create policy "Allow all" on public.dashboards for all using (true);
create policy "Allow all" on public.digest_subscribers for all using (true);
```

Click **Run** to execute.

---

### Step 4 — (Optional) Enable Supabase Auth

If you want to add login/signup to SNAPBOARD in the future:

1. Go to **Authentication → Providers** in your Supabase dashboard
2. Enable **Email** (already on by default)
3. Optionally enable **Google** or **GitHub** OAuth:
   - For Google: go to [console.cloud.google.com](https://console.cloud.google.com), create OAuth credentials, paste Client ID + Secret into Supabase
   - For GitHub: go to [github.com/settings/developers](https://github.com/settings/developers), create an OAuth App, paste Client ID + Secret
4. Set your **Site URL** to `http://localhost:5000` (local) or your deployed URL
5. Under **Authentication → URL Configuration**, add `http://localhost:5000/**` to "Redirect URLs"

> **Note:** Authentication is not currently wired into `app.py` — these steps prepare Supabase for when you add it.

---

### Step 5 — Verify Connection

Start the app and check the terminal — if Supabase env vars are set correctly, no errors will appear. You can also test in Python:

```python
from supabase import create_client
client = create_client("https://your-project.supabase.co", "your-anon-key")
print(client.table("dashboards").select("*").execute())
```

---

## 🔑 API Keys Setup

### Google Gemini (AI Intent Detection)

1. Go to [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Click **Create API key**
3. Copy and paste into `.env` as `GEMINI_API_KEY=AIza...`
4. Free tier: 15 requests/minute, 1 million tokens/day — more than enough for development

### Groq (AI Chat — Natural Language Chart Editing)

1. Go to [console.groq.com](https://console.groq.com) and sign up
2. Navigate to **API Keys → Create API Key**
3. Copy and paste into `.env` as `GROQ_API_KEY=gsk_...`
4. Free tier: 14,400 requests/day with Llama 3.1 8B — very generous

### Twilio (WhatsApp Digest)

1. Go to [twilio.com](https://www.twilio.com) and create a free account
2. From the **Console Dashboard**, copy:
   - `Account SID` → `TWILIO_ACCOUNT_SID`
   - `Auth Token` → `TWILIO_AUTH_TOKEN`
3. For **WhatsApp Sandbox** (free, for testing):
   - Go to **Messaging → Try it out → Send a WhatsApp message**
   - Note the sandbox number (e.g. `whatsapp:+14155238886`) → `TWILIO_WHATSAPP_FROM`
   - Follow the on-screen instructions to join the sandbox from your own WhatsApp
4. For production: you need a WhatsApp Business Account approved by Meta through Twilio

> **Tip:** If you don't set up Twilio, the WhatsApp button will show an error but the rest of the app works perfectly.

---

## 📋 Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | Optional | Your Supabase project URL |
| `SUPABASE_ANON_KEY` | Optional | Supabase anonymous/public key |
| `SUPABASE_SERVICE_KEY` | Optional | Supabase service role key (admin) |
| `GEMINI_API_KEY` | Optional | Google Gemini API key for intent detection |
| `GROQ_API_KEY` | Optional | Groq API key for chat (natural language editing) |
| `TWILIO_ACCOUNT_SID` | Optional | Twilio account SID for WhatsApp |
| `TWILIO_AUTH_TOKEN` | Optional | Twilio auth token |
| `TWILIO_WHATSAPP_FROM` | Optional | Twilio WhatsApp sender number |
| `SECRET_KEY` | Recommended | Flask session secret key (any random string) |
| `APP_URL` | Optional | Your app's public URL (used for share links) |
| `FLASK_DEBUG` | Dev only | Set to `1` to enable debug/auto-reload mode |

> All API keys are **optional** in local mode. The app degrades gracefully — upload and basic metrics always work.

---

## ▶️ Running the App

### Development (local)

```bash
# Activate virtual environment first
source .venv/bin/activate   # macOS/Linux
.venv\Scripts\activate      # Windows

# Run with auto-reload
FLASK_DEBUG=1 python app.py
```

Visit: **http://localhost:5000**

### Production (Gunicorn)

```bash
gunicorn -w 2 -b 0.0.0.0:8000 app:app
```

For deployment on **Railway**, **Render**, or **Heroku**, set the environment variables in their dashboard and use the above Gunicorn command as the start command.

---

## 🧪 Sample CSV Files to Test With

You can create a quick test CSV to verify everything works:

**Razorpay-style CSV** (`test_razorpay.csv`):
```csv
order_id,payment_id,amount,created_at,product,city
ORD001,PAY001,150000,15/03/2024,Wireless Earbuds,Mumbai
ORD002,PAY002,75000,16/03/2024,Phone Case,Delhi
ORD003,PAY003,2500000,17/03/2024,Laptop Stand,Bangalore
ORD004,PAY004,45000,01/04/2024,Wireless Earbuds,Mumbai
ORD005,PAY005,1200000,02/04/2024,Laptop Stand,Chennai
ORD006,PAY006,300000,03/04/2024,Mouse Pad,Pune
```

**Hinglish-style CSV** (`test_hinglish.csv`):
```csv
Bill_tareekh,Daam,Cheez,Sheher,Matra
15/03/2024,50000,Laptop,Mumbai,1
16/03/2024,25000,Phone,Delhi,2
17/03/2024,75000,Tablet,Bangalore,1
01/04/2024,30000,Headphones,Hyderabad,3
```

Upload either file at **http://localhost:5000/upload** and the dashboard will be ready instantly.

---

## 📁 Project Structure

```
Snapboard/
├── app.py                  # Main Flask application (all routes + logic)
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── .env                    # Your local secrets (never commit this!)
├── templates/
│   ├── base.html           # Base layout: navbar, footer, Chart.js CDN
│   ├── index.html          # Landing page (hero, features, platforms)
│   ├── upload.html         # File upload page
│   └── dashboard.html      # Live dashboard (KPIs, charts, chat, GST, PDF)
└── static/
    ├── css/
    │   └── style.css       # All styles (mobile-first, CSS custom properties)
    └── js/
        ├── main.js         # Global JS (navbar, animations, flash messages)
        ├── upload.js       # File upload drag-drop + progress handling
        ├── charts.js       # Chart.js chart initialisation + rendering
        └── dashboard.js    # Dashboard interactions (GST, chat, WhatsApp, share, PDF)
```

### Key functions in `app.py`

| Function | What it does |
|----------|-------------|
| `format_inr(amount)` | Formats number as ₹10L, ₹2.3Cr, ₹50K |
| `indian_number_str(n)` | Formats integer in Indian comma system (1,00,000) |
| `detect_platform(columns)` | Returns `razorpay`, `zoho`, `shopify`, or `generic` |
| `normalize_columns(df)` | Renames Hinglish and messy columns to snake_case |
| `compute_metrics(df, platform)` | Computes all KPIs and chart data |
| `detect_intent_gemini(...)` | Calls Gemini API to detect business intent |
| `chat_with_groq(message, context)` | Calls Groq API for natural language chart editing |
| `calculate_gst_net(gross, rate)` | Strips GST: `gross / (1 + rate/100)` |
| `export_pdf(dashboard_id)` | Builds A4 PDF with ReportLab |
| `send_digest()` | Sends WhatsApp message via Twilio |
| `setup_scheduler()` | Starts APScheduler for 8 AM IST daily digest |

---

## 🎨 UI/UX Design Philosophy

SNAPBOARD's UI is built to feel **premium, dark, and fast** — purpose-built for Indian founders who are used to modern SaaS tools.

### Design Principles

- **Dark-first** — deep navy/charcoal background (`#0A0A0F`) with saffron (`#FF6B35`) as the primary accent; inspired by India's flag colours (saffron + green)
- **Mobile-first** — all layouts are designed at 375px and scale up; tested on iPhone SE and Android budget phones
- **Smooth animations** — CSS transitions on hover, card lift effects (`transform: translateY`), gradient text for hero headlines
- **No-build CSS** — plain CSS custom properties (`--clr-primary`, `--radius-md`, etc.), no Tailwind or SCSS build step required
- **Glassmorphism cards** — KPI cards and chart cards use subtle border + shadow for depth without heavy blur
- **India colour palette** — saffron `#FF6B35`, deep green `#22c55e`, gold `#F7B731`; never cold Western blues
- **Chart.js theming** — all charts use dark backgrounds with saffron/gold data series, matching the app theme
- **Accessible typography** — `Inter` font, `clamp()` fluid sizes, minimum 12pt for readability

### Pages

| Page | Design highlight |
|------|-----------------|
| **Landing (`/`)** | Full-width hero with gradient headline, animated stat pills, feature grid |
| **Upload (`/upload`)** | Drag-and-drop zone with dashed border animation, file type validation |
| **Dashboard (`/dashboard/<id>`)** | KPI card grid, chart grid, inline GST toggle, floating chat panel, WhatsApp modal |

### Responsiveness

The layout uses CSS Grid with `auto-fit` and `minmax()` for fluid card grids — no JavaScript layout calculations. Works at 320px, 375px, 768px, 1024px, and 1440px+.

---

## 🚀 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Make sure your virtual environment is activated: `source .venv/bin/activate` |
| `Invalid API key` for Gemini | Check `GEMINI_API_KEY` in `.env`; ensure no trailing spaces |
| WhatsApp not sending | Join Twilio sandbox first; check phone number format (without +91) |
| PDF download is empty | Ensure `reportlab` is installed: `pip install "reportlab>=4.0.0"` |
| Dashboard not found after restart | Dashboards are in-memory; re-upload your CSV after restarting |
| Port 5000 in use | Change port: `python app.py` uses 5000; try `PORT=8080 python app.py` or edit `app.py` line `port=5000` |
| Supabase connection error | Verify `SUPABASE_URL` does not have a trailing slash and keys are correct |

---

<div align="center">

Made with ❤️ in India &nbsp;·&nbsp; 🇮🇳 India-first analytics

</div>
