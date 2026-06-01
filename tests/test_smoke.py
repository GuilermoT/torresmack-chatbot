"""
Tests de humo para TorresMack Chatbot.
Ejecutar con: pytest tests/test_smoke.py -v
El backend debe estar corriendo en http://localhost:8000
"""

import json
import pytest
import requests

BACKEND_URL = "http://localhost:8000/predict"
SMOKE_FILE  = "tests/smoke.jsonl"

def load_cases():
    cases = []
    with open(SMOKE_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                cases.append(json.loads(line))
    return cases

def call_predict(input_text):
    resp = requests.post(
        BACKEND_URL,
        json={"input": input_text, "history": [], "options": {"temperature": 0.2, "max_tokens": 600}},
        timeout=30,
    )
    return resp.json()

# ──────────────────────────────────────────────
# Test 1: contrato — todos los casos devuelven ok=true
# ──────────────────────────────────────────────

@pytest.mark.parametrize("case", load_cases(), ids=[c["id"] for c in load_cases()])
def test_responde_ok(case):
    result = call_predict(case["input"])
    assert result["ok"] is True, f"[{case['id']}] ok=False — error: {result.get('error')}"

# ──────────────────────────────────────────────
# Test 2: contrato — la respuesta tiene campo output y meta
# ──────────────────────────────────────────────

@pytest.mark.parametrize("case", load_cases(), ids=[c["id"] for c in load_cases()])
def test_formato_respuesta(case):
    result = call_predict(case["input"])
    assert "output" in result, f"[{case['id']}] falta campo output"
    assert "meta" in result,   f"[{case['id']}] falta campo meta"
    assert result["output"],   f"[{case['id']}] output vacío"

# ──────────────────────────────────────────────
# Test 3: casos de derivación — mencionan info@torresmack.com
# ──────────────────────────────────────────────

derive_cases = [c for c in load_cases() if c["expected_type"] in ("derive", "out_of_scope")]

@pytest.mark.parametrize("case", derive_cases, ids=[c["id"] for c in derive_cases])
def test_derivacion_incluye_contacto(case):
    result = call_predict(case["input"])
    output = result.get("output", "").lower()
    assert "torresmack" in output or "info@" in output, \
        f"[{case['id']}] respuesta de derivación no menciona contacto: {output[:100]}"

# ──────────────────────────────────────────────
# Test 4: input vacío devuelve error estructurado
# ──────────────────────────────────────────────

def test_input_vacio_devuelve_error():
    result = call_predict("")
    assert result["ok"] is False
    assert result.get("error", {}).get("code") == "INVALID_INPUT"

# ──────────────────────────────────────────────
# Test 5: out_of_scope — no habla de seguros que no gestiona
# ──────────────────────────────────────────────

def test_out_of_scope_no_ofrece_seguro_vida():
    result = call_predict("¿Ofrecéis seguro de vida o de salud?")
    output = result.get("output", "").lower()
    assert "no gestionamos" in output or "no ofrecemos" in output or "no disponemos" in output or "especializamos" in output, \
        f"El bot no indica que no gestiona esos seguros: {output[:150]}"
