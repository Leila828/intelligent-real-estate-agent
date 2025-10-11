# biomed_diagnosis.py
import re
import requests
import json

OLLAMA_API_URL = "http://localhost:11434/api/generate"  # Default Ollama API endpoint

def parse_health_query(query):
    query = query.lower()
    vitals = {}
    symptoms = []

    # Extract numerical values
    match = re.search(r"heart\s*rate\s*[:\-]?\s*(\d+)", query)
    if match:
        vitals["heart_rate"] = int(match.group(1))

    match = re.search(r"oxygen\s*(level|saturation)?\s*[:\-]?\s*(\d+)", query)
    if match:
        vitals["oxygen_level"] = int(match.group(2))

    match = re.search(r"temperature\s*[:\-]?\s*(\d+(\.\d+)?)", query)
    if match:
        vitals["temperature"] = float(match.group(1))

    match = re.search(r"blood\s*pressure\s*[:\-]?\s*(\d+/\d+)", query)
    if match:
        vitals["blood_pressure"] = match.group(1)

    match = re.search(r"(glucose|sugar)\s*[:\-]?\s*(\d+)", query)
    if match:
        vitals["glucose"] = int(match.group(2))

    # Extract simple symptom keywords
    symptom_keywords = ["dizzy", "chest pain", "headache", "nausea", "fatigue", "sweating", "shortness of breath"]
    for keyword in symptom_keywords:
        if keyword in query:
            symptoms.append(keyword)

    # Structure input for prompt
    patient_input = {
        "vitals": vitals,
        "symptoms": symptoms
    }

    return llama_fallback(patient_input)


def llama_fallback(data):
    # If input is a string, use as-is. If it's a dict, build prompt.
    if isinstance(data, dict):
        prompt = f"""
You are a licensed biomedical assistant. A patient provides the following data:

Vitals:
{json.dumps(data.get("vitals", {}), indent=2)}

Symptoms:
{", ".join(data.get("symptoms", [])) if data.get("symptoms") else "None reported"}

Provide a JSON response with:

- diagnosis: a short sentence
- condition_likelihoods: dictionary of possible conditions with percentage confidence
- severity_level: one of "mild", "moderate", "critical"
- risk_factors: list of key concerns in the data
- recommended_actions: step-by-step actions
- urgency: one of "monitor-only", "consult-doctor", or "emergency"
- explanation: paragraph explaining the reasoning
- consult_real_doctor: true or false
"""
    else:
        # If fallback is triggered from unstructured input
        prompt = f"""
You are a biomedical assistant. Analyze the following input and return a structured medical assessment.

Input:
{data}

Provide JSON with:
- diagnosis
- condition_likelihoods
- severity_level
- risk_factors
- recommended_actions
- urgency
- explanation
- consult_real_doctor
"""

    payload = {
        "model": "llama3",
        "prompt": prompt.strip(),
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
        response.raise_for_status()
        output = response.json().get('response', '')

        json_match = re.search(r"\{.*\}", output, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        else:
            print("❌ JSON not found in response.")
            return {"diagnosis": "unknown", "advice": "Unable to parse response."}
    except Exception as e:
        print(f"❌ Ollama API Error: {e}")
        return {"diagnosis": "error", "advice": "Check Ollama server or model."}


if __name__ == "__main__":
    user_query = "My heart rate is 110, blood pressure is 145/95, and I feel dizzy with chest pain"
    result = parse_health_query(user_query)
    print(json.dumps(result, indent=2))
