import asyncio
import platform
import sys
sys.path.insert(0, '.')

async def main():
    from app.workers.playwright_worker import _run_playwright_async
    
    form_data = {
        "owner_name":       "Sunita Devi",
        "mobile":           "9876543210",
        "enterprise_name":  "Sunita Handlooms",
        "state":            "Madhya Pradesh",
        "district":         "Chanderi",
        "pin_code":         "473446",
        "nic_code":         "13111",
        "persons_employed": "1",
        "turnover":         "200000",
    }

    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    events = await _run_playwright_async(form_data, demo_mode=True)
    for e in events:
        print(f"  [{e['type']}]", e)

if __name__ == "__main__":
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())