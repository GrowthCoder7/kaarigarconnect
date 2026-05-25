import asyncio
from datetime import datetime
from typing import Callable
# from core.config import settings

# ── URLs ──────────────────────────────────────────────────────────────────────
UDYAM_URL = "https://udyamregistration.gov.in/UdyamRegistration.aspx"
DEMO_URL   = "http://localhost:8080/static/udyam_mock.html" 
# DEMO_URL = settings.demo_url  # FIX: was 8080

# ── Field map: form_data key → CSS selector ───────────────────────────────────
# Each entry: (selector, interaction_type)
# interaction_type: "input" | "select_label" | "select_value" | "js_fill"
FIELD_MAP = [
    ("owner_name",       "#txtOwnerName",             "input"),
    ("mobile",           "#txtMobile",                "input"),
    ("enterprise_name",  "#txtEnterpriseName",        "input"),
    ("state",            "#ddlState",                 "select_label"),
    ("district",         "#ddlDistrict",              "select_label"),   # FIX: was input, now select
    ("pin_code",         "#txtPinCode",               "input"),
    ("nic_code",         "#txtNICCode",               "input"),
    ("persons_employed", "#txtPersonsEmployed",       "input"),
    ("turnover",         "#txtTurnover",              "input"),
]

# Fields that trigger JS hooks on the page for visual feedback
JS_HOOK_FIELDS = {
    "txtOwnerName", "txtMobile", "txtEnterpriseName",
    "txtNICCode", "txtPinCode", "txtPersonsEmployed"
}


def _now() -> str:
    return datetime.utcnow().isoformat()

def _run_playwright_sync(form_data: dict, demo_mode: bool) -> list[dict]:
    from playwright.sync_api import sync_playwright

    events = []
    url = DEMO_URL if demo_mode else UDYAM_URL

    def evt(type_: str, **kwargs):
        e = {"type": type_, "timestamp": _now(), **kwargs}
        events.append(e)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )
            page = browser.new_page()

            try:
                page.goto(url, timeout=30000, wait_until="domcontentloaded")
            except Exception as e:
                evt("FATAL_ERROR", message=f"Could not load form: {e}")
                browser.close()
                return events

            import time
            time.sleep(0.5)

            for field_key, selector, interaction in FIELD_MAP:
                value = str(form_data.get(field_key, "")).strip()
                if not value:
                    continue

                label = field_key.replace("_", " ").title()
                evt("FIELD_START", field=field_key, label=label)

                field_id = selector.lstrip("#")
                if field_id in JS_HOOK_FIELDS:
                    page.evaluate(f"window.fieldStart && window.fieldStart('{field_id}')")

                try:
                    page.wait_for_selector(selector, timeout=5000)

                    if interaction == "input":
                        page.fill(selector, value)
                    elif interaction == "select_label":
                        try:
                            page.select_option(selector, label=value)
                        except Exception:
                            try:
                                page.select_option(selector, value=value)
                            except Exception:
                                page.evaluate(f"""
                                    (function() {{
                                        const sel = document.querySelector('{selector}');
                                        if (!sel) return;
                                        const opts = Array.from(sel.options);
                                        const match = opts.find(o =>
                                            o.text.toLowerCase().includes('{value.lower()}') ||
                                            o.value.toLowerCase().includes('{value.lower()}')
                                        );
                                        if (match) sel.value = match.value;
                                    }})()
                                """)
                    elif interaction == "js_fill":
                        page.evaluate(f"document.querySelector('{selector}').value = '{value}'")

                    time.sleep(0.3)

                    if field_id in JS_HOOK_FIELDS:
                        page.evaluate(f"window.fieldFilled && window.fieldFilled('{field_id}', '{value}')")

                    evt("FIELD_FILLED", field=field_key, value=value)

                except Exception as e:
                    error_msg = str(e)[:200]
                    if field_id in JS_HOOK_FIELDS:
                        page.evaluate(f"window.fieldError && window.fieldError('{field_id}', '{error_msg[:50]}')")
                    evt("FIELD_ERROR", field=field_key, error=error_msg)

            evt("PAGE_SUBMIT")

            if demo_mode:
                page.evaluate("window.submitForm && window.submitForm()")
                time.sleep(1.0)
            else:
                try:
                    page.click("#btnSubmit, input[type=submit], button[type=submit]", timeout=5000)
                    page.wait_for_load_state("networkidle", timeout=15000)
                except Exception as e:
                    evt("FIELD_ERROR", field="submit", error=str(e))

            evt("COMPLETE", certificate_url="/static/demo/udyam-certificate.pdf")
            browser.close()

    except Exception as e:
        import traceback
        print(f"[Playwright FATAL]\n{traceback.format_exc()}", flush=True)
        evt("FATAL_ERROR", message=f"Automation failed: {str(e)[:300]}")

    return events


async def fill_udyam_form(form_data: dict, emit: Callable, demo_mode: bool = True):
    loop = asyncio.get_event_loop()

    try:
        events = await loop.run_in_executor(
            None, _run_playwright_sync, form_data, demo_mode
        )
    except Exception as e:
        events = [{"type": "FATAL_ERROR", "message": str(e), "timestamp": _now()}]

    for event in events:
        await emit(event)
        if event["type"] in ("FIELD_START", "FIELD_FILLED"):
            await asyncio.sleep(0.7)
        elif event["type"] == "PAGE_SUBMIT":
            await asyncio.sleep(1.2)
        else:
            await asyncio.sleep(0.3)


async def replay_mock_events(emit: Callable):
    """
    Fallback: replay hardcoded events — no Playwright, no browser.
    Used when demo_mode=True or on Windows without headless support.
    """
    mock_events = [
        {"type": "FIELD_START",  "field": "owner_name",       "label": "Owner Name"},
        {"type": "FIELD_FILLED", "field": "owner_name",       "value": "Sunita Devi"},
        {"type": "FIELD_START",  "field": "mobile",           "label": "Mobile"},
        {"type": "FIELD_FILLED", "field": "mobile",           "value": "9876543210"},
        {"type": "FIELD_START",  "field": "enterprise_name",  "label": "Enterprise Name"},
        {"type": "FIELD_FILLED", "field": "enterprise_name",  "value": "Sunita Handlooms"},
        {"type": "FIELD_START",  "field": "state",            "label": "State"},
        {"type": "FIELD_FILLED", "field": "state",            "value": "Madhya Pradesh"},
        {"type": "FIELD_START",  "field": "district",         "label": "District"},
        {"type": "FIELD_FILLED", "field": "district",         "value": "Chanderi"},
        {"type": "FIELD_START",  "field": "pin_code",         "label": "Pin Code"},
        {"type": "FIELD_FILLED", "field": "pin_code",         "value": "473446"},
        {"type": "FIELD_START",  "field": "nic_code",         "label": "NIC Code"},
        {"type": "FIELD_FILLED", "field": "nic_code",         "value": "13111"},
        {"type": "FIELD_START",  "field": "persons_employed", "label": "Persons Employed"},
        {"type": "FIELD_FILLED", "field": "persons_employed", "value": "1"},
        {"type": "PAGE_SUBMIT",  "field": None,               "label": None},
        {"type": "COMPLETE",     "certificate_url": "/static/demo/udyam-certificate.pdf"},
    ]
    for event in mock_events:
        event["timestamp"] = _now()
        await emit(event)
        if event["type"] in ("FIELD_START", "FIELD_FILLED"):
            await asyncio.sleep(0.7)
        elif event["type"] == "PAGE_SUBMIT":
            await asyncio.sleep(1.2)
        else:
            await asyncio.sleep(0.3)