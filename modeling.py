
import requests
import re
import os

# ---------------- CONFIG ---------------- #

OPENROUTER_API_KEY = "OPENROUTER_API_KEY"

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

MODEL = "meta-llama/llama-3-8b-instruct"

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost",
    "X-Title": "AI Announcement App"
}

complete_cache = {}
suggest_cache = {}

# ---------------- CORE CALL ---------------- #

def openrouter_call(prompt, max_tokens, temperature):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You write professional internal company announcements and titles."},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    r = requests.post(
        OPENROUTER_URL,
        headers=HEADERS,
        json=payload,
        timeout=20
    )

    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()

# ---------------- CLEAN ---------------- #

def clean_line(text):
    text = re.sub(r"^[\s\d\.\-\)\•]+", "", text)
    return text.replace("*", "").strip()

# ---------------- AUTOCOMPLETE ---------------- #

def generate_completion(text):
    key = text[-120:]
    if key in complete_cache:
        return complete_cache[key]

    prompt = f"""
Predict ONLY the next few words that continue this professional title.

Rules:
- Do not repeat input
- 2 to 6 words only
- Strict Continuation only
- No overlapping of previous words as suggestion

Title so far: {text}
"""

    result = openrouter_call(prompt, 18, 0.15)

    result = result.lstrip(" ,.-")
    if not result.startswith(" "):
        result = " " + result

    complete_cache[key] = result
    return result

# ---------------- SUGGESTIONS ---------------- #

def generate_suggestions(text):
    key = text[-25:]
    if key in suggest_cache:
        return suggest_cache[key]

    prompt = f"""
You are an AI that generates professional internal company announcement titles.
Company name is Arah Infotech

IMPORTANT:
Return ONLY the titles.
Do not write any introduction sentence.
Do not explain anything.

Rules:
- Exactly 5 titles
- One per line
- Short and professional
- No numbering
- No bullet points
- No extra text

Partial title: {text}
"""

    raw = openrouter_call(prompt, 80, 0.3)

    lines = raw.split("\n")

    results = [
        clean_line(line)
        for line in lines
        if clean_line(line)
        and not line.lower().startswith("here")
        and not line.lower().startswith("sure")
    ][:5]

    suggest_cache[key] = results
    return results


# ---------------- GENERATION ---------------- #

def generate_description(title):
    prompt = f"""
You are writing a professional internal company announcement.
Company name is Arah Infotech
Write a clear and meaningful announcement based on the title.

Guidelines:
- No greeting (no Dear Team, Hello, etc.)
- Do not repeat the title exactly
- Keep it professional and natural
- Around 2 short paragraphs and each paragraph only 2-3 lines that's it.
- No special characters or bullet points
- Make the content very much related to the title 
- Do not mention that this is a description
- Make it look like written by a human
- You can use the technical jargon also.
- End with a positive note
Title: {title}
"""

    return openrouter_call(prompt, 220, 0.3)

def chat_reply(messages):
    prompt = """
You are a helpful, professional ChatGPT-style assistant.

How to respond:
- Answer using clear bullet points
- Use a dash (-) for each bullet
- Write ONE short sentence per bullet
- Explain ONE idea per bullet only
- Keep bullets easy to read and well spaced

Formatting:
- Highlight important words or phrases using **bold**
- Do not write paragraphs
- Do not combine multiple ideas in one bullet
- Do not add introductions or conclusions

Style:
- Match ChatGPT’s clean and friendly tone
- Be professional but simple
- Focus on clarity over length
- Limit responses to a maximum of 8 bullets

If the question contains multiple concepts, split them into separate bullets.


"""

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": prompt
            },
            *messages[-10:]
        ],
        "temperature": 0.3,   # lower = more controlled
        "max_tokens": 250
    }

    response = requests.post(
        OPENROUTER_URL,
        headers=HEADERS,
        json=payload,
        timeout=20
    )

    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()


