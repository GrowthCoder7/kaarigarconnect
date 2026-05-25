import json
import google.generativeai as genai
from app.core.config import settings

genai.configure(api_key=settings.gemini_api_key)
model = genai.GenerativeModel("gemini-2.5-flash")

EXTRACTION_PROMPT = """
You are a data extraction agent for an Indian government form filling system.

Extract structured business registration data from the following user profile/conversation.
Map the extracted data to Udyam Registration form fields.

Input profile:
{profile}

Return ONLY valid JSON, no explanation, no markdown:
{{
  "enterprise_name": "",
  "owner_name": "",
  "mobile": "",
  "email": "",
  "social_category": "General|SC|ST|OBC",
  "gender": "Female",
  "physically_handicapped": false,
  "state": "",
  "district": "",
  "pin_code": "",
  "address": "",
  "date_of_incorporation": "",
  "bank_account_number": "",
  "ifsc_code": "",
  "major_activity": "Manufacturing|Services|Trading",
  "nic_code": "",
  "persons_employed": 0,
  "investment_in_plant": 0,
  "turnover": 0
}}

Rules:
- nic_code: map craft type to correct NIC code (textiles=13111, pottery=23930, jewellery=32111, food=10890)
- Leave unknown fields as empty string, not null
- persons_employed default to 1 if not mentioned
- gender always Female for this platform
"""

async def extract_form_data(profile: dict) -> dict:
    """Extract structured Udyam form data from artisan profile."""
    try:
        prompt = EXTRACTION_PROMPT.format(profile=json.dumps(profile, indent=2))
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                max_output_tokens=1000,
            ),
            request_options={"timeout": 30}
        )
        text = response.text.strip()
        
        # Strip markdown if model adds it
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        
        return json.loads(text.strip())
    
    except json.JSONDecodeError:
        # Fallback: return demo data
        return _demo_form_data(profile)
    except Exception as e:
        print(f"[FormFillAgent] Gemini failed: {e}")
        return _demo_form_data(profile)


def _demo_form_data(profile: dict) -> dict:
    """Safe fallback for demo mode."""
    return {
        "enterprise_name": profile.get("business_name", "Sunita Handlooms"),
        "owner_name": profile.get("full_name", "Sunita Devi"),
        "mobile": profile.get("mobile", "9876543210"),
        "email": profile.get("email", "sunita@example.com"),
        "social_category": "General",
        "gender": "Female",
        "physically_handicapped": False,
        "state": profile.get("state", "Madhya Pradesh"),
        "district": profile.get("district", "Chanderi"),
        "pin_code": profile.get("pin_code", "473446"),
        "address": profile.get("address", "Village Chanderi, MP"),
        "date_of_incorporation": "2020-01-01",
        "bank_account_number": "",
        "ifsc_code": "",
        "major_activity": "Manufacturing",
        "nic_code": "13111",
        "persons_employed": 1,
        "investment_in_plant": 50000,
        "turnover": 200000
    }