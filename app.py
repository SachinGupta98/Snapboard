import io
import json
import os
import re
import traceback
import uuid
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv
from flask import (Flask, jsonify, redirect, render_template, request,
                   send_file, url_for)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "snapboard-dev-secret-2024")

# In-memory store for dashboards (use Supabase in production for persistence)
dashboards_store: dict = {}

# ─── India Format Helpers ────────────────────────────────────────

# Indian number system thresholds
INR_CRORE = 1_00_00_000   # 10,000,000
INR_LAKH  = 1_00_000      # 100,000
INR_THOU  = 1_000         # 1,000


def format_inr(amount: float) -> str:
    """Format amount in Indian notation with ₹ prefix."""
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return "₹0"
    if amount >= INR_CRORE:
        return f"₹{amount / INR_CRORE:.1f}Cr"
    if amount >= INR_LAKH:
        return f"₹{amount / INR_LAKH:.1f}L"
    if amount >= INR_THOU:
        return f"₹{amount / INR_THOU:.1f}K"
    return f"₹{int(amount):,}"


def indian_number_str(n: int) -> str:
    """Format integer in Indian number system (e.g. 1,00,000)."""
    try:
        n = int(n)
    except (TypeError, ValueError):
        return "0"
    s = str(abs(n))
    if len(s) <= 3:
        return ("-" if n < 0 else "") + s
    result = s[-3:]
    s = s[:-3]
    while len(s) > 2:
        result = s[-2:] + "," + result
        s = s[:-2]
    if s:
        result = s + "," + result
    return ("-" if n < 0 else "") + result


# ─── Hinglish Column Mapping ─────────────────────────────────────

HINGLISH_MAP: dict = {
    "Bill_tareekh": "date",
    "bill_tareekh": "date",
    "BILL_TAREEKH": "date",
    "Daam": "price",
    "daam": "price",
    "DAAM": "price",
    "Cheez": "product",
    "cheez": "product",
    "CHEEZ": "product",
    "Sheher": "city",
    "sheher": "city",
    "SHEHER": "city",
    "Dukaan": "store",
    "dukaan": "store",
    "DUKAAN": "store",
    "Matra": "quantity",
    "matra": "quantity",
    "MATRA": "quantity",
}


def detect_platform(columns: list) -> str:
    """Detect the source platform from column names."""
    cols_lower = [c.lower() for c in columns]
    if "payment_id" in cols_lower or "order_id" in cols_lower:
        return "razorpay"
    if any(c in cols_lower for c in ["invoice number", "balance due"]):
        return "zoho"
    if "financial status" in cols_lower:
        return "shopify"
    return "generic"


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename columns using Hinglish map and snake_case normalisation."""
    rename_map = {}
    for col in df.columns:
        if col in HINGLISH_MAP:
            rename_map[col] = HINGLISH_MAP[col]
        else:
            normalized = re.sub(r"[\s\-]+", "_", col.strip().lower())
            rename_map[col] = normalized
    return df.rename(columns=rename_map)


def find_column(df: pd.DataFrame, candidates: list) -> str | None:
    """Return first column matching any candidate (case-insensitive)."""
    for col in df.columns:
        if col.lower() in [c.lower() for c in candidates]:
            return col
    return None


def coerce_numeric(series: pd.Series) -> pd.Series:
    """Strip ₹, commas, spaces then coerce to numeric."""
    return pd.to_numeric(
        series.astype(str).str.replace(r"[₹,\s]", "", regex=True),
        errors="coerce",
    )


def compute_metrics(df: pd.DataFrame, platform: str = "generic") -> dict:
    """Compute key business metrics from a normalised dataframe."""
    metrics: dict = {}
    df = normalize_columns(df)

    # ── Revenue ──────────────────────────────────────────────────
    rev_col = find_column(
        df,
        ["amount", "total", "revenue", "price", "daam", "sales",
         "gross_total", "net_total", "order_total", "invoice_total"],
    )
    if rev_col:
        df[rev_col] = coerce_numeric(df[rev_col])
        total_revenue = df[rev_col].sum()
        metrics["total_revenue"] = float(total_revenue)
        metrics["total_revenue_fmt"] = format_inr(total_revenue)
        metrics["avg_order_value"] = float(df[rev_col].mean())
        metrics["avg_order_value_fmt"] = format_inr(df[rev_col].mean())

    metrics["total_orders"] = len(df)
    metrics["total_orders_fmt"] = indian_number_str(len(df))

    # ── Date & time series ───────────────────────────────────────
    date_col = find_column(
        df,
        ["date", "created_at", "order_date", "invoice_date",
         "bill_tareekh", "transaction_date", "payment_date"],
    )
    if date_col:
        try:
            df[date_col] = pd.to_datetime(
                df[date_col],
                dayfirst=True,  # India-first: DD/MM/YYYY date format
                errors="coerce",
            )
            df = df.dropna(subset=[date_col])
            df["_month"] = df[date_col].dt.to_period("M").astype(str)
            df["_day"] = df[date_col].dt.strftime("%d/%m/%Y")

            if rev_col:
                monthly = (
                    df.groupby("_month")[rev_col].sum().reset_index()
                )
                metrics["monthly_revenue"] = [
                    {"month": r["_month"], "revenue": float(r[rev_col])}
                    for _, r in monthly.iterrows()
                ]
                if len(monthly) >= 2:
                    last = float(monthly.iloc[-1][rev_col])
                    prev = float(monthly.iloc[-2][rev_col])
                    growth = ((last - prev) / prev * 100) if prev > 0 else 0
                    metrics["mom_growth"] = round(growth, 1)
                    sign = "+" if growth >= 0 else ""
                    metrics["mom_growth_fmt"] = f"{sign}{growth:.1f}%"

                daily = df.groupby("_day")[rev_col].sum().reset_index()
                metrics["daily_revenue"] = [
                    {"day": r["_day"], "revenue": float(r[rev_col])}
                    for _, r in daily.tail(30).iterrows()
                ]
        except Exception:
            pass

    # ── Top products ─────────────────────────────────────────────
    prod_col = find_column(
        df,
        ["product", "cheez", "item", "description", "product_name",
         "item_name", "product_title"],
    )
    if prod_col and rev_col:
        top = df.groupby(prod_col)[rev_col].sum().nlargest(5).reset_index()
        metrics["top_products"] = [
            {"name": str(r[prod_col]), "revenue": float(r[rev_col])}
            for _, r in top.iterrows()
        ]

    # ── Top cities ───────────────────────────────────────────────
    city_col = find_column(
        df, ["city", "sheher", "location", "state", "region", "billing_city"]
    )
    if city_col and rev_col:
        city_data = df.groupby(city_col)[rev_col].sum().nlargest(5).reset_index()
        metrics["top_cities"] = [
            {"city": str(r[city_col]), "revenue": float(r[rev_col])}
            for _, r in city_data.iterrows()
        ]

    return metrics


# ─── GST Calculation ─────────────────────────────────────────────

def calculate_gst_net(gross_amount: float, rate: float = 18.0) -> float:
    """Return net (ex-GST) amount from gross inclusive of GST."""
    return gross_amount / (1 + rate / 100)


# ─── AI Integration ──────────────────────────────────────────────

def detect_intent_gemini(columns: list, sample_data: str, platform: str) -> tuple:
    """Use Gemini 1.5 Flash to detect business intent from data."""
    try:
        import google.generativeai as genai  # noqa: PLC0415

        genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = (
            f"You are analyzing a business CSV from an Indian company.\n"
            f"Platform: {platform}\n"
            f"Columns: {', '.join(columns)}\n"
            f"Sample data (first 3 rows): {sample_data}\n\n"
            "Detect the primary business intent. Reply with ONLY ONE of:\n"
            "- revenue (sales/income tracking)\n"
            "- churn (customer retention/cancellations)\n"
            "- roas (advertising/marketing ROI)\n"
            "- ops (operations/inventory/logistics)\n"
            "- mixed (covers multiple areas)\n\n"
            "Then on the next line, write a 1-sentence description in Indian business context.\n\n"
            "Format:\nINTENT: <intent>\nDESC: <description>"
        )
        response = model.generate_content(prompt)
        intent, desc = "revenue", "Business analytics dashboard"
        for line in response.text.strip().split("\n"):
            if line.startswith("INTENT:"):
                intent = line.replace("INTENT:", "").strip().lower()
            elif line.startswith("DESC:"):
                desc = line.replace("DESC:", "").strip()
        return intent, desc
    except Exception:
        return "revenue", "Business analytics dashboard"


def chat_with_groq(message: str, context: dict) -> dict:
    """Use Groq Llama 3.1 to process natural language chart editing."""
    try:
        from groq import Groq  # noqa: PLC0415

        client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant for SNAPBOARD, an India-first business analytics dashboard.\n"
                        "Help users modify their charts using natural language.\n"
                        "Always respond in JSON:\n"
                        '{"action":"update_chart|add_chart|remove_chart|filter_data|answer",'
                        '"chart_id":"...","chart_type":"bar|line|pie|doughnut",'
                        '"title":"...","filter":{"column":"...","value":"..."},'
                        '"message":"human-readable Hinglish/English response"}\n'
                        "Currency is always ₹ (Indian Rupees). Dates are DD/MM/YYYY."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Dashboard context: {json.dumps(context)}\n\n"
                        f"User request: {message}"
                    ),
                },
            ],
            temperature=0.3,
            max_tokens=500,
        )
        text = completion.choices[0].message.content
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"action": "answer", "message": text}
    except Exception as exc:
        return {
            "action": "answer",
            "message": f"Sorry, could not process that. Please try again. ({str(exc)[:80]})",
        }


# ─── Supabase helper (optional) ──────────────────────────────────

def get_supabase():
    """Return Supabase client if env vars are set, else None."""
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_ANON_KEY", "")
    if url and key and not url.startswith("https://xxxx"):
        try:
            from supabase import create_client  # noqa: PLC0415
            return create_client(url, key)
        except Exception:
            return None
    return None


# ─── Routes ──────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        if not file or not file.filename:
            return jsonify({"error": "No file selected"}), 400

        filename = file.filename
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

        try:
            if ext == "csv":
                df = pd.read_csv(file)
            elif ext in ("xlsx", "xls"):
                df = pd.read_excel(file, engine="openpyxl" if ext == "xlsx" else "xlrd")
            else:
                return jsonify(
                    {"error": "Unsupported file. Please upload CSV or Excel (.xlsx/.xls)."}
                ), 400

            if df.empty:
                return jsonify({"error": "The uploaded file is empty."}), 400

            platform = detect_platform(df.columns.tolist())
            hinglish_detected = {
                col: HINGLISH_MAP[col] for col in df.columns if col in HINGLISH_MAP
            }
            sample_data = df.head(3).fillna("").to_dict("records")
            intent, description = detect_intent_gemini(
                df.columns.tolist(), str(sample_data), platform
            )
            metrics = compute_metrics(df.copy(), platform)

            dashboard_id = str(uuid.uuid4())[:8]
            dashboards_store[dashboard_id] = {
                "id": dashboard_id,
                "filename": filename,
                "platform": platform,
                "intent": intent,
                "description": description,
                "columns": df.columns.tolist(),
                "hinglish_detected": hinglish_detected,
                "metrics": metrics,
                "row_count": len(df),
                "created_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "gst_rate": 18.0,
                "gst_included": False,
            }

            return jsonify(
                {
                    "success": True,
                    "dashboard_id": dashboard_id,
                    "platform": platform,
                    "intent": intent,
                    "description": description,
                    "columns": df.columns.tolist(),
                    "hinglish_detected": hinglish_detected,
                    "row_count": len(df),
                    "preview": df.head(5).fillna("").to_dict("records"),
                }
            )
        except Exception as exc:
            traceback.print_exc()
            return jsonify({"error": f"Error processing file: {exc}"}), 500

    return render_template("upload.html")


@app.route("/dashboard/<dashboard_id>")
def dashboard(dashboard_id):
    data = dashboards_store.get(dashboard_id)
    if not data:
        return render_template("index.html", error="Dashboard not found. Please upload your data again.")
    return render_template("dashboard.html", dashboard=data)


@app.route("/api/dashboard/<dashboard_id>")
def dashboard_data(dashboard_id):
    data = dashboards_store.get(dashboard_id)
    if not data:
        return jsonify({"error": "Dashboard not found"}), 404
    return jsonify(data)


@app.route("/api/chat", methods=["POST"])
def chat():
    body = request.get_json(silent=True) or {}
    message = body.get("message", "")
    dashboard_id = body.get("dashboard_id", "")
    dash = dashboards_store.get(dashboard_id, {})
    context = {
        "intent": dash.get("intent", ""),
        "platform": dash.get("platform", ""),
        "metrics_keys": list(dash.get("metrics", {}).keys()),
        "filename": dash.get("filename", ""),
    }
    return jsonify(chat_with_groq(message, context))


@app.route("/api/gst", methods=["POST"])
def gst_toggle():
    body = request.get_json(silent=True) or {}
    dashboard_id = body.get("dashboard_id", "")
    include_gst = bool(body.get("include_gst", False))
    gst_rate = float(body.get("gst_rate", 18.0))

    dash = dashboards_store.get(dashboard_id)
    if not dash:
        return jsonify({"error": "Dashboard not found"}), 404

    metrics = dash.get("metrics", {})
    gross = metrics.get("total_revenue", 0)

    if include_gst:
        net = calculate_gst_net(gross, gst_rate)
        return jsonify(
            {
                "success": True,
                "net_revenue_fmt": format_inr(net),
                "gross_revenue_fmt": format_inr(gross),
                "gst_amount_fmt": format_inr(gross - net),
                "gst_rate": gst_rate,
            }
        )
    return jsonify(
        {
            "success": True,
            "net_revenue_fmt": format_inr(gross),
            "gross_revenue_fmt": format_inr(gross),
        }
    )


@app.route("/api/export-pdf/<dashboard_id>")
def export_pdf(dashboard_id):
    dash = dashboards_store.get(dashboard_id)
    if not dash:
        return jsonify({"error": "Dashboard not found"}), 404
    try:
        from reportlab.lib import colors as rl_colors  # noqa: PLC0415
        from reportlab.lib.pagesizes import A4  # noqa: PLC0415
        from reportlab.lib.styles import ParagraphStyle  # noqa: PLC0415
        from reportlab.lib.units import cm  # noqa: PLC0415
        from reportlab.platypus import (  # noqa: PLC0415
            HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
        )

        metrics = dash.get("metrics", {})
        pdf_io = io.BytesIO()

        # ── Colours ───────────────────────────────────────────────
        # Defined inside the function because they depend on the lazy
        # rl_colors import (ReportLab is optional; not installed at module load).
        SAFFRON = rl_colors.HexColor("#FF6B35")
        GREY    = rl_colors.HexColor("#888888")
        DARK    = rl_colors.HexColor("#1a1a1a")
        STRIPE  = rl_colors.HexColor("#fafafa")
        BORDER  = rl_colors.HexColor("#e0e0e0")

        # Usable page width after 2.5 cm margins on each side
        PAGE_W = A4[0] - 5 * cm

        doc = SimpleDocTemplate(
            pdf_io,
            pagesize=A4,
            leftMargin=2.5 * cm, rightMargin=2.5 * cm,
            topMargin=2.5 * cm, bottomMargin=2.5 * cm,
            title=f"SNAPBOARD Report — {dash.get('filename', '')}",
            author="SNAPBOARD",
        )

        # ── Paragraph styles ──────────────────────────────────────
        def make_style(name, font="Helvetica", size=10, color=DARK, align=0, leading=None, **kw):
            """Create a ReportLab ParagraphStyle with sensible defaults."""
            return ParagraphStyle(
                name,
                fontName=font,
                fontSize=size,
                textColor=color,
                alignment=align,
                leading=leading or max(size * 1.3, size + 2),
                **kw,
            )

        brand_s   = make_style("brand",   "Helvetica-Bold", 22, SAFFRON)
        sub_s     = make_style("sub",     size=8,  color=GREY)
        meta_s    = make_style("meta",    size=9,  leading=14)
        sec_s     = make_style("sec",     "Helvetica-Bold", 13, SAFFRON)
        kpi_lbl_s = make_style("kl",      size=7,  color=GREY, align=1)
        kpi_val_s = make_style("kv",      "Helvetica-Bold", 16, align=1)
        kpi_chg_s = make_style("kc",      size=8,  align=1)
        th_s      = make_style("th",      "Helvetica-Bold", 9, rl_colors.white)
        td_s      = make_style("td",      size=9)
        hd_s      = make_style("hd",      size=9,  color=GREY, spaceAfter=4)
        hm_s      = make_style("hm",      size=9)
        foot_s    = make_style("foot",    size=7,  color=GREY, align=1)
        desc_s    = make_style("desc",    size=10, color=GREY, leading=14)

        # ── Table style helper ────────────────────────────────────
        def std_table_style():
            return TableStyle([
                ("BACKGROUND",    (0, 0), (-1, 0), SAFFRON),
                ("ROWBACKGROUNDS",(0, 1), (-1, -1), [rl_colors.white, STRIPE]),
                ("GRID",          (0, 0), (-1, -1), 0.5, BORDER),
                ("TOPPADDING",    (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING",   (0, 0), (-1, -1), 8),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
                ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ])

        def section_heading(text):
            story.append(Spacer(1, 0.5 * cm))
            story.append(Paragraph(text, sec_s))
            story.append(HRFlowable(width="100%", thickness=1, color=SAFFRON, spaceAfter=6))

        story = []

        # ── Header: brand + metadata side by side ─────────────────
        meta_lines = [
            f"<b>File:</b> {dash.get('filename', '—')}",
            f"<b>Platform:</b> {dash.get('platform', '—').upper()}",
            f"<b>Intent:</b> {dash.get('intent', '—').upper()}",
            f"<b>Generated:</b> {dash.get('created_at', '—')}",
            f"<b>Rows:</b> {dash.get('row_count', 0)}",
        ]
        header_data = [[
            [Paragraph("SNAPBOARD", brand_s),
             Paragraph("India-First AI Business Analytics", sub_s)],
            [Paragraph("<br/>".join(meta_lines), meta_s)],
        ]]
        header_table = Table(header_data, colWidths=[PAGE_W * 0.55, PAGE_W * 0.45])
        header_table.setStyle(TableStyle([
            ("ALIGN",    (0, 0), (0, 0), "LEFT"),
            ("ALIGN",    (1, 0), (1, 0), "RIGHT"),
            ("VALIGN",   (0, 0), (-1, -1), "TOP"),
            ("LINEBELOW",(0, 0), (-1, 0), 2, SAFFRON),
            ("TOPPADDING",    (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING",   (0, 0), (-1, -1), 0),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ]))
        story.append(header_table)

        if dash.get("description"):
            story.append(Spacer(1, 0.3 * cm))
            story.append(Paragraph(dash["description"], desc_s))

        # ── KPI Cards ─────────────────────────────────────────────
        section_heading("Key Performance Indicators")
        mom_growth = metrics.get("mom_growth", 0)
        mom_fmt    = metrics.get("mom_growth_fmt", "—")
        if mom_growth >= 0:
            mom_text = f'<font color="#16a34a">▲ {mom_fmt} Growing</font>'
        else:
            mom_text = f'<font color="#dc2626">▼ {mom_fmt} Declining</font>'

        col_w = PAGE_W / 4
        kpi_data = [[
            [Paragraph("TOTAL REVENUE",    kpi_lbl_s),
             Paragraph(metrics.get("total_revenue_fmt",    "—"), kpi_val_s)],
            [Paragraph("TOTAL ORDERS",     kpi_lbl_s),
             Paragraph(metrics.get("total_orders_fmt",     "—"), kpi_val_s)],
            [Paragraph("AVG ORDER VALUE",  kpi_lbl_s),
             Paragraph(metrics.get("avg_order_value_fmt",  "—"), kpi_val_s)],
            [Paragraph("MoM GROWTH",       kpi_lbl_s),
             Paragraph(mom_text,                               kpi_chg_s)],
        ]]
        kpi_table = Table(kpi_data, colWidths=[col_w] * 4)
        kpi_table.setStyle(TableStyle([
            ("BOX",           (0, 0), (0, 0), 0.5, BORDER),
            ("BOX",           (1, 0), (1, 0), 0.5, BORDER),
            ("BOX",           (2, 0), (2, 0), 0.5, BORDER),
            ("BOX",           (3, 0), (3, 0), 0.5, BORDER),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",    (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ]))
        story.append(kpi_table)

        # ── Monthly Revenue ────────────────────────────────────────
        monthly = metrics.get("monthly_revenue", [])
        if monthly:
            section_heading("Monthly Revenue")
            rows = [[Paragraph("Month", th_s), Paragraph("Revenue (₹)", th_s)]]
            for r in monthly:
                rows.append([
                    Paragraph(str(r["month"]), td_s),
                    Paragraph(format_inr(r["revenue"]), td_s),
                ])
            t = Table(rows, colWidths=[PAGE_W * 0.5, PAGE_W * 0.5])
            t.setStyle(std_table_style())
            story.append(t)

        # ── Top Products ───────────────────────────────────────────
        products = metrics.get("top_products", [])
        if products:
            section_heading("Top 5 Products by Revenue")
            rows = [[
                Paragraph("#", th_s),
                Paragraph("Product", th_s),
                Paragraph("Revenue (₹)", th_s),
            ]]
            for i, r in enumerate(products, 1):
                rows.append([
                    Paragraph(str(i), td_s),
                    Paragraph(str(r["name"]), td_s),
                    Paragraph(format_inr(r["revenue"]), td_s),
                ])
            t = Table(rows, colWidths=[1.2 * cm, PAGE_W - 1.2 * cm - 4 * cm, 4 * cm])
            t.setStyle(std_table_style())
            story.append(t)

        # ── Top Cities ─────────────────────────────────────────────
        cities = metrics.get("top_cities", [])
        if cities:
            section_heading("Revenue by City")
            rows = [[
                Paragraph("#", th_s),
                Paragraph("City", th_s),
                Paragraph("Revenue (₹)", th_s),
            ]]
            for i, r in enumerate(cities, 1):
                rows.append([
                    Paragraph(str(i), td_s),
                    Paragraph(str(r["city"]), td_s),
                    Paragraph(format_inr(r["revenue"]), td_s),
                ])
            t = Table(rows, colWidths=[1.2 * cm, PAGE_W - 1.2 * cm - 4 * cm, 4 * cm])
            t.setStyle(std_table_style())
            story.append(t)

        # ── Hinglish Column Mapping ────────────────────────────────
        hinglish = dash.get("hinglish_detected", {})
        if hinglish:
            section_heading("Hinglish Column Mapping")
            story.append(Paragraph("The following Hinglish column names were auto-mapped:", hd_s))
            mapping_text = "  ·  ".join(
                f"{orig} → {mapped}" for orig, mapped in hinglish.items()
            )
            story.append(Paragraph(mapping_text, hm_s))

        # ── Footer ─────────────────────────────────────────────────
        story.append(Spacer(1, 1 * cm))
        story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph(
            "Generated by SNAPBOARD — India-First AI Business Analytics  ·  "
            "All amounts in Indian Rupees (₹)  ·  "
            "Numbers in Indian format (Lakh/Crore)  ·  Dates: DD/MM/YYYY",
            foot_s,
        ))

        doc.build(story)
        pdf_io.seek(0)
        return send_file(
            pdf_io,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"snapboard-report-{dashboard_id}.pdf",
        )
    except Exception as exc:
        traceback.print_exc()
        return jsonify({"error": f"PDF generation failed: {exc}"}), 500


@app.route("/api/send-digest", methods=["POST"])
def send_digest():
    body = request.get_json(silent=True) or {}
    phone = body.get("phone", "").strip()
    dashboard_id = body.get("dashboard_id", "")

    if not phone:
        return jsonify({"error": "Phone number is required"}), 400

    dash = dashboards_store.get(dashboard_id)
    if not dash:
        return jsonify({"error": "Dashboard not found"}), 404

    metrics = dash.get("metrics", {})
    mom = metrics.get("mom_growth_fmt", "")
    lines = [
        "📊 *SNAPBOARD Daily Digest*",
        f"🗓️ {datetime.now().strftime('%d/%m/%Y')}",
        "",
        f"💰 *Revenue:* {metrics.get('total_revenue_fmt', 'N/A')}",
        f"📦 *Orders:* {metrics.get('total_orders_fmt', 'N/A')}",
        f"🛒 *Avg Order:* {metrics.get('avg_order_value_fmt', 'N/A')}",
    ]
    if mom:
        lines.append(f"📈 *MoM Growth:* {mom}")
    lines += ["", "_Powered by SNAPBOARD 🚀_"]
    message = "\n".join(lines)

    try:
        from twilio.rest import Client  # noqa: PLC0415

        if not phone.startswith("+"):
            phone = "+91" + phone
        client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
        client.messages.create(
            from_=os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886"),
            to=f"whatsapp:{phone}",
            body=message,
        )
        return jsonify({"success": True, "message": "Digest sent! ✅"})
    except Exception as exc:
        traceback.print_exc()
        return jsonify({"error": f"WhatsApp send failed: {exc}"}), 500


@app.route("/api/share/<dashboard_id>")
def share_dashboard(dashboard_id):
    if dashboard_id not in dashboards_store:
        return jsonify({"error": "Dashboard not found"}), 404
    app_url = os.getenv("APP_URL", request.host_url.rstrip("/"))
    return jsonify({"share_url": f"{app_url}/dashboard/{dashboard_id}"})


# ─── Scheduled WhatsApp Digest (APScheduler) ─────────────────────

def setup_scheduler():
    """Configure APScheduler to send daily 8am WhatsApp digests."""
    try:
        from apscheduler.schedulers.background import BackgroundScheduler  # noqa: PLC0415
        import pytz  # noqa: PLC0415

        tz = pytz.timezone("Asia/Kolkata")
        scheduler = BackgroundScheduler(timezone=tz)

        def send_all_digests():
            # In production, fetch subscriber list from Supabase
            pass

        scheduler.add_job(send_all_digests, "cron", hour=8, minute=0)
        scheduler.start()
    except Exception:
        pass


if __name__ == "__main__":
    setup_scheduler()
    debug_mode = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug_mode, host="0.0.0.0", port=5000)
