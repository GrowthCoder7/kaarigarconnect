# import os
# import asyncio
# import edge_tts
# from groq import AsyncGroq
# import google.generativeai as genai
# from app.core.config import settings

# # Initialize Free Clients
# groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
# genai.configure(api_key=settings.gemini_api_key)
# text_model = genai.GenerativeModel("gemini-2.5-flash")

# # The Onboarding System Prompt
# SYSTEM_PROMPT = """
# You are a helpful, empathetic onboarding assistant for Indian artisans.
# Keep your responses very short (1-2 sentences max). 
# Ask one question at a time to gather their: Name, Age, Craft, and Location.
# """

# async def process_audio_chunk(audio_bytes: bytes, chat_history: list) -> dict:
#     """
#     Takes user audio -> Text -> LLM Response -> System Audio
#     """
#     # 1. Save bytes temporarily for Groq
#     temp_filename = "temp_user_audio.webm"
#     with open(temp_filename, "wb") as f:
#         f.write(audio_bytes)

#     try:
#         # 2. STT: Transcribe with Groq Whisper
#         with open(temp_filename, "rb") as file:
#             transcription = await groq_client.audio.transcriptions.create(
#                 file=(temp_filename, file.read()),
#                 model="whisper-large-v3",
#                 prompt="Transcribe Indian English and Hindi context.",
#                 language="en"
#             )
#         user_text = transcription.text
        
#         # 3. LLM: Generate Next Question
#         prompt = f"{SYSTEM_PROMPT}\n\nHistory: {chat_history}\nUser says: {user_text}\n\nWhat is your next question?"
#         response = text_model.generate_content(prompt)
#         ai_text = response.text.strip()

#         # 4. TTS: Generate Audio Reply with Edge TTS (Using a natural Indian English female voice)
#         voice = "en-IN-NeerjaNeural"
#         output_audio_file = "temp_ai_reply.mp3"
#         communicate = edge_tts.Communicate(ai_text, voice)
#         await communicate.save(output_audio_file)

#         # 5. Read the generated audio bytes
#         with open(output_audio_file, "rb") as f:
#             ai_audio_bytes = f.read()

#         return {
#             "user_text": user_text,
#             "ai_text": ai_text,
#             "ai_audio_bytes": ai_audio_bytes
#         }

#     finally:
#         # Cleanup temp files
#         if os.path.exists(temp_filename):
#             os.remove(temp_filename)
#         if os.path.exists("temp_ai_reply.mp3"):
#             os.remove("temp_ai_reply.mp3")

# import os
# import json
# import asyncio
# import edge_tts
# from groq import AsyncGroq
# from app.core.config import settings

# # Initialize a single Groq client for both STT and LLM
# groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

# # Map 2-letter language codes to highly realistic native Edge TTS voices
# VOICE_MAP = {
#     "en": "en-IN-NeerjaNeural",    
#     "hi": "hi-IN-SwaraNeural",     
#     "ta": "ta-IN-PallaviNeural",   
#     "te": "te-IN-ShrutiNeural",    
#     "mr": "mr-IN-AarohiNeural",    
#     "bn": "bn-IN-TanishaaNeural",  
#     "gu": "gu-IN-DhwaniNeural",    
#     "kn": "kn-IN-SapnaNeural",     
#     "ml": "ml-IN-SobhanaNeural"    
# }

# SYSTEM_PROMPT = """
# You are an empathetic onboarding assistant for Indian artisans.
# Your goal is to gather: Name, Age, Craft, and Location. Ask one short question at a time.

# CRITICAL INSTRUCTIONS:
# 1. Detect the language the user is speaking based on their input.
# 2. Reply in that EXACT SAME language and native script.
# 3. You MUST return ONLY valid JSON in this format:
# {
#   "language_code": "hi", 
#   "ai_text": "आपका नाम क्या है?" 
# }
# """

# async def process_audio_chunk(audio_bytes: bytes, chat_history: list) -> dict | None:
#     """
#     Groq-Exclusive Pipeline: Whisper Auto-Detect -> Llama 3 JSON Router -> Edge TTS
#     """
#     temp_filename = "temp_user_audio.webm"
#     with open(temp_filename, "wb") as f:
#         f.write(audio_bytes)

#     try:
#         # 1. STT: Groq Whisper (Auto-Detect Language)
#         with open(temp_filename, "rb") as file:
#             transcription = await groq_client.audio.transcriptions.create(
#                 file=(temp_filename, file.read()),
#                 model="whisper-large-v3",
#                 prompt="Transcribe accurately in the native language and script."
#             )
        
#         user_text = transcription.text
#         if not user_text.strip():
#             return None

#         # 2. LLM: Groq Llama 3 (JSON Mode)
#         # Using llama-3.3-70b-versatile for high intelligence and instant response times
#         chat_completion = await groq_client.chat.completions.create(
#             messages=[
#                 {
#                     "role": "system",
#                     "content": SYSTEM_PROMPT
#                 },
#                 {
#                     "role": "user",
#                     "content": f"History: {chat_history}\nUser says: {user_text}"
#                 }
#             ],
#             model="openai/gpt-oss-120b",
#             response_format={"type": "json_object"},
#             temperature=0.2,
#         )
        
#         # Parse the routing data from Llama 3
#         raw_json = chat_completion.choices[0].message.content
#         ai_data = json.loads(raw_json)
        
#         ai_text = ai_data.get("ai_text", "I did not understand.")
#         lang_code = ai_data.get("language_code", "en").lower()

#         # 3. TTS: Dynamic Voice Routing
#         voice = VOICE_MAP.get(lang_code, "en-IN-NeerjaNeural") 
#         output_audio_file = "temp_ai_reply.mp3"
        
#         communicate = edge_tts.Communicate(ai_text, voice)
#         await communicate.save(output_audio_file)

#         # 4. Read the generated audio bytes
#         with open(output_audio_file, "rb") as f:
#             ai_audio_bytes = f.read()

#         return {
#             "user_text": user_text,
#             "ai_text": ai_text,
#             "ai_audio_bytes": ai_audio_bytes
#         }

#     except Exception as e:
#         print(f"[Voice Worker] Fatal pipeline error: {e}")
#         return None
        
#     finally:
#         # Cleanup temp files
#         if os.path.exists(temp_filename):
#             os.remove(temp_filename)
#         if os.path.exists("temp_ai_reply.mp3"):
#             os.remove("temp_ai_reply.mp3")

# import os
# import json
# import asyncio
# import edge_tts
# from groq import AsyncGroq
# from deep_translator import GoogleTranslator

# # 1. Initialize Groq (Handles STT and Text Generation)
# groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

# # Map 2-letter language codes to Edge TTS voices
# VOICE_MAP = {
#     "en": "en-IN-NeerjaNeural",
#     "hi": "hi-IN-SwaraNeural",
#     "ta": "ta-IN-PallaviNeural",   # Tamil
#     "te": "te-IN-ShrutiNeural",    # Telugu
#     "mr": "mr-IN-AarohiNeural",    # Marathi
#     "bn": "bn-IN-TanishaaNeural",  # Bengali
#     "gu": "gu-IN-DhwaniNeural",    # Gujarati
#     "kn": "kn-IN-SapnaNeural",     # Kannada
#     "ml": "ml-IN-SobhanaNeural",   # Malayalam
#     "or": "en-IN-NeerjaNeural"     # Odia fallback
# }

# SYSTEM_PROMPT = """
# You are an onboarding assistant for Indian artisans. 
# The user is speaking to you in an Indian regional language.

# CRITICAL INSTRUCTIONS:
# 1. Read the user's text and identify the language.
# 2. Decide the next logical onboarding question (Name, Age, Craft, or Location).
# 3. Write your response ONLY in ENGLISH. (We will translate it later).
# 4. You MUST return ONLY valid JSON in this exact format:
# {
#   "language_code": "gu", // The 2-letter ISO code of the USER's language (hi, ta, gu, mr, etc.)
#   "english_reply": "What type of craft do you make?"
# }
# """

# async def process_audio_chunk(audio_bytes: bytes, chat_history: list) -> dict | None:
#     temp_filename = "temp_user_audio.webm"
#     with open(temp_filename, "wb") as f:
#         f.write(audio_bytes)

#     try:
#         # STEP 1: Listen (Groq Whisper)
#         with open(temp_filename, "rb") as file:
#             transcription = await groq_client.audio.transcriptions.create(
#                 file=(temp_filename, file.read()),
#                 model="whisper-large-v3",
#                 prompt="Transcribe accurately in the native script."
#             )
        
#         user_text = transcription.text
#         if not user_text.strip():
#             return None

#         # Format history for Llama 3
#         messages = [{"role": "system", "content": SYSTEM_PROMPT}]
#         for turn in chat_history:
#             if "user" in turn: messages.append({"role": "user", "content": turn["user"]})
#             if "ai" in turn: messages.append({"role": "assistant", "content": turn["ai"]}) # AI history is stored in English
#         messages.append({"role": "user", "content": user_text})

#         # STEP 2: Think in English (Groq Llama-3-70B)
#         chat_completion = await groq_client.chat.completions.create(
#             messages=messages,
#             model="openai/gpt-oss-120b",
#             temperature=0.1,
#             response_format={"type": "json_object"}
#         )
        
#         ai_data = json.loads(chat_completion.choices[0].message.content)
#         lang_code = ai_data.get("language_code", "en").lower()
#         english_reply = ai_data.get("english_reply", "Could you repeat that?")

#         # STEP 3: Translate to Native Language (Deep Translator)
#         if lang_code != "en":
#             try:
#                 native_reply = GoogleTranslator(source='en', target=lang_code).translate(english_reply)
#             except Exception as trans_err:
#                 print(f"[Translation Fallback] {trans_err}")
#                 native_reply = english_reply
#                 lang_code = "en"
#         else:
#             native_reply = english_reply

#         # STEP 4: Speak (Edge TTS)
#         voice = VOICE_MAP.get(lang_code, "en-IN-NeerjaNeural") 
#         output_audio_file = "temp_ai_reply.mp3"
        
#         communicate = edge_tts.Communicate(native_reply, voice)
#         await communicate.save(output_audio_file)

#         with open(output_audio_file, "rb") as f:
#             ai_audio_bytes = f.read()

#         return {
#             "user_text": user_text,       # Show native text on screen
#             "ai_text": english_reply,     # Save English in backend history for Llama's context
#             "ai_audio_bytes": ai_audio_bytes
#         }

#     except Exception as e:
#         print(f"[Voice Worker] Fatal pipeline error: {e}")
#         return None
        
#     finally:
#         if os.path.exists(temp_filename): os.remove(temp_filename)
#         if os.path.exists("temp_ai_reply.mp3"): os.remove("temp_ai_reply.mp3")

import os
import json
import asyncio
import edge_tts
from groq import AsyncGroq
from deep_translator import GoogleTranslator

# Initialize Groq
groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

VOICE_MAP = {
    "en": "en-IN-NeerjaNeural",
    "hi": "hi-IN-SwaraNeural",
    "ta": "ta-IN-PallaviNeural",   
    "te": "te-IN-ShrutiNeural",    
    "bn": "bn-IN-TanishaaNeural",  
    "kn": "kn-IN-SapnaNeural",     
    "mr": "mr-IN-AarohiNeural",    
    "gu": "gu-IN-DhwaniNeural",    
    "ml": "ml-IN-SobhanaNeural",   
    "or": "en-IN-NeerjaNeural"     
}

# The State Machine Prompt
SYSTEM_PROMPT = """
You are an onboarding assistant for Indian businesses and artisans. 
The user is speaking to you in an Indian regional language.

YOUR MISSION:
You must collect the following 9 fields in order. Do not ask for multiple fields at once.
1. fullName
2. mobileNumber
3. preferredLanguage
4. state
5. businessStage
6. businessCategory
7. annualRevenue
8. needCategory
9. existingRegistrations

CRITICAL INSTRUCTIONS:
1. Identify the user's language.
2. Acknowledge their previous answer briefly, then ask the next missing question from the list.
3. Write your conversational response ONLY in ENGLISH. (It will be translated later).
4. Extract any valid data they provided into the "extracted_data" object.
5. You MUST return ONLY valid JSON in this exact format:
{
  "language_code": "ta", 
  "extracted_data": {
    "fullName": "Prince",
    "businessCategory": "Handicrafts"
  },
  "english_reply": "Got it, Prince. What is your approximate annual revenue?"
}
"""

async def process_audio_chunk(audio_bytes: bytes, chat_history: list,current_language: str = "en") -> dict | None:
    temp_filename = "temp_user_audio.webm"
    with open(temp_filename, "wb") as f:
        f.write(audio_bytes)

    try:
        # STEP 1: Listen (Groq Whisper)
        with open(temp_filename, "rb") as file:
            transcription = await groq_client.audio.transcriptions.create(
                file=(temp_filename, file.read()),
                model="whisper-large-v3",
                prompt="Transcribe accurately in the native script.",
                language=current_language
            )
        
        user_text = transcription.text
        if not user_text.strip():
            print("[Voice Worker] Whisper returned empty text.")
            return None

        # Format history for Llama 3
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for turn in chat_history:
            if "user" in turn: messages.append({"role": "user", "content": turn["user"]})
            if "ai" in turn: messages.append({"role": "assistant", "content": turn["ai"]})
        messages.append({"role": "user", "content": user_text})

        # STEP 2: Think & Extract in English (Groq Llama-3-70B)
        chat_completion = await groq_client.chat.completions.create(
            messages=messages,
            model="openai/gpt-oss-120b",
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        ai_data = json.loads(chat_completion.choices[0].message.content)
        lang_code = ai_data.get("language_code", "en").lower()
        english_reply = ai_data.get("english_reply", "Could you repeat that?")
        extracted_data = ai_data.get("extracted_data", {})

        # STEP 3: Translate to Native Language (Deep Translator)
        if lang_code != "en":
            try:
                native_reply = GoogleTranslator(source='en', target=lang_code).translate(english_reply)
            except Exception as trans_err:
                print(f"[Translation Fallback] {trans_err}")
                native_reply = english_reply
                lang_code = "en"
        else:
            native_reply = english_reply

        # STEP 4: Speak (Edge TTS)
        voice = VOICE_MAP.get(lang_code, "en-IN-NeerjaNeural") 
        output_audio_file = "temp_ai_reply.mp3"
        
        communicate = edge_tts.Communicate(native_reply, voice)
        await communicate.save(output_audio_file)

        with open(output_audio_file, "rb") as f:
            ai_audio_bytes = f.read()

        return {
            "user_text": user_text,       
            "ai_text": english_reply,     # Save English for context history
            "ai_audio_bytes": ai_audio_bytes,
            "extracted_data": extracted_data, # Pass this back to the UI!
            "language_code": lang_code
        }

    except Exception as e:
        print(f"[Voice Worker] Fatal pipeline error: {e}")
        return None
        
    finally:
        if os.path.exists(temp_filename): os.remove(temp_filename)
        if os.path.exists("temp_ai_reply.mp3"): os.remove("temp_ai_reply.mp3")