import json
import asyncio
import threading
from datetime import datetime
from typing import Callable
from app.core.config import settings

# Targeting local mock, but treating it like a real external server
DEMO_URL = "http://localhost:8080/static/udyam_mock.html"

MOCK_FIELD_MAP = {
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

def _run_in_new_loop(form_data: dict) -> list[dict]:
    """Isolates Playwright in a dedicated thread and event loop."""
    result_holder = []

    def thread_target():
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            events = loop.run_until_complete(_run_playwright_async(form_data))
            result_holder.extend(events)
        finally:
            loop.close()

    t = threading.Thread(target=thread_target)
    t.start()
    t.join(timeout=45)  
    return result_holder


async def _run_playwright_async(form_data: dict) -> list[dict]:
    from playwright.async_api import async_playwright
    events = []

    def evt(type_, **kwargs):
        events.append({"type": type_, "timestamp": _now(), **kwargs})

    try:
        async with async_playwright() as p:
            # Keep headless=True. Change to False if you want to watch the ghost typing during dev.
            browser = await p.chromium.launch(headless=True)
            page    = await browser.new_page()

            evt("FIELD_START", field="system", label="Initializing Sandbox Environment...")
            await page.goto(DEMO_URL, timeout=10000)
            await page.wait_for_load_state("domcontentloaded")
            await asyncio.sleep(1) # Initial loading breath

            for field_key, selector in MOCK_FIELD_MAP.items():
                value = str(form_data.get(field_key, ""))
                if not value: continue

                label = field_key.replace("_", " ").title()
                evt("FIELD_START", field=field_key, label=label)

                try:
                    await page.wait_for_selector(selector, timeout=2000)
                    tag = await page.locator(selector).evaluate("el => el.tagName.toLowerCase()")

                    if tag == "select":
                        try:
                            await page.select_option(selector, label=value)
                        except:
                            await page.select_option(selector, value=value)
                    else:
                        # delay ensures frontend sees distinct typing events
                        await page.locator(selector).fill(value)

                    evt("FIELD_FILLED", field=field_key, value=value)
                    await asyncio.sleep(0.4) # Cinematic typing delay

                except Exception as e:
                    evt("FIELD_ERROR", field=field_key, error=str(e))

            evt("PAGE_SUBMIT")
            await page.locator("#btnSubmit").click()
            await asyncio.sleep(1.5) # Let success modal render
                
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
    Executes actual Playwright automation against the mock DOM.
    """
    loop   = asyncio.get_event_loop()
    events = await loop.run_in_executor(
        None, _run_in_new_loop, form_data
    )
    for event in events:
        await emit(event)
        # Stagger emission to the frontend
        await asyncio.sleep(0.3)


async def replay_mock_events(emit: Callable):
    # This remains intact as your absolute "Layer 2" fallback if Playwright fails entirely.
    pass # (Keep your existing replay_mock_events implementation here)

def _now() -> str:
    return datetime.utcnow().isoformat()