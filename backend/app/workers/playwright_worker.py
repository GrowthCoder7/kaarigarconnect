import json
import asyncio
import threading
from datetime import datetime
from typing import Callable
from app.core.config import settings

UDYAM_URL = "https://udyamregistration.gov.in/UdyamRegistration.aspx"
DEMO_URL   = "http://localhost:8080/static/udyam_mock.html"

FIELD_MAP = {
    "owner_name":       "#txtOwnerName",
    "mobile":           "#txtMobile",
    "enterprise_name":  "#txtEnterpriseName",
    "state":            "#ddlState",
    "district":         "#ddlDistrict",
    "address":          "#txtAddress",
    "pin_code":         "#txtPinCode",
    "nic_code":         "#txtNICCode",
    "persons_employed": "#txtPersonsEmployed",
    "turnover":         "#txtTurnover",
}


def _run_in_new_loop(form_data: dict, demo_mode: bool) -> list[dict]:
    """
    Playwright requires its own clean event loop on Windows.
    Run in a brand new thread with a fresh event loop.
    """
    result_holder = []

    def thread_target():
        # Create fresh event loop for this thread
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            events = loop.run_until_complete(
                _run_playwright_async(form_data, demo_mode)
            )
            result_holder.extend(events)
        finally:
            loop.close()

    t = threading.Thread(target=thread_target)
    t.start()
    t.join(timeout=60)  # max 60s for form fill
    return result_holder


async def _run_playwright_async(form_data: dict, demo_mode: bool) -> list[dict]:
    """Async Playwright running in its own dedicated event loop."""
    from playwright.async_api import async_playwright

    events = []
    url = DEMO_URL if demo_mode else UDYAM_URL

    def evt(type_, **kwargs):
        events.append({"type": type_, "timestamp": _now(), **kwargs})

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page    = await browser.new_page()
            await page.goto(url, timeout=30000)
            await page.wait_for_load_state("domcontentloaded")

            for field_key, selector in FIELD_MAP.items():
                value = str(form_data.get(field_key, ""))
                if not value:
                    continue

                label = field_key.replace("_", " ").title()
                evt("FIELD_START", field=field_key, label=label)

                try:
                    await page.wait_for_selector(selector, timeout=3000)
                    tag = await page.locator(selector).evaluate(
                        "el => el.tagName.toLowerCase()"
                    )

                    if tag == "select":
                        try:
                            await page.select_option(selector, label=value)
                        except Exception:
                            await page.select_option(selector, value=value)
                    else:
                        await page.fill(selector, value)

                    evt("FIELD_FILLED", field=field_key, value=value)

                except Exception as e:
                    evt("FIELD_ERROR", field=field_key, error=str(e))

            evt("PAGE_SUBMIT")
            await browser.close()
            evt("COMPLETE", certificate_url="/demo/udyam-certificate.pdf")

    except Exception as e:
        import traceback
        msg = traceback.format_exc()
        print(f"[Playwright FATAL] {msg}")
        events.append({"type": "FATAL_ERROR", "message": msg, "timestamp": _now()})

    return events


async def fill_udyam_form(form_data: dict, emit: Callable, demo_mode: bool = True):
    """
    Offloads Playwright to a new thread+loop, then streams events via WebSocket.
    """
    loop   = asyncio.get_event_loop()
    events = await loop.run_in_executor(
        None, _run_in_new_loop, form_data, demo_mode
    )
    for event in events:
        await emit(event)
        await asyncio.sleep(0.6)


async def replay_mock_events(emit: Callable):
    """Fallback: replay hardcoded mock events — no file dependency."""
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
        {"type": "FIELD_START",  "field": "nic_code",         "label": "Nic Code"},
        {"type": "FIELD_FILLED", "field": "nic_code",         "value": "13111"},
        {"type": "FIELD_START",  "field": "persons_employed", "label": "Persons Employed"},
        {"type": "FIELD_FILLED", "field": "persons_employed", "value": "1"},
        {"type": "PAGE_SUBMIT",  "field": None,               "label": None},
        {"type": "COMPLETE",     "certificate_url": "/demo/udyam-certificate.pdf"},
    ]
    for event in mock_events:
        event["timestamp"] = _now()
        await emit(event)
        await asyncio.sleep(0.6)


def _now() -> str:
    return datetime.utcnow().isoformat()