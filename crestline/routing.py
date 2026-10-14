import re
import unicodedata

PRODUCTS = ("Crestline X", "Crestline Pro", "Crestline Watch", "Crestline OS", "Crestline Cloud")


def normalize(text):
    return "".join(c for c in unicodedata.normalize("NFKD", text.lower()) if not unicodedata.combining(c))


def spanish(text):
    return bool(re.search(r"[¿¡]|\b(cual|cuantos|cuantas|como|politica|vacaciones|ventas|ingresos|empleados|resumen|campana|trimestre|mes|para)\b", normalize(text)))


def product_in(text):
    q = normalize(text)
    for product in PRODUCTS:
        if re.search(r"\b" + re.escape(product.lower()) + r"\b", q):
            return product
    aliases = {"phone": "Crestline X", "telefono": "Crestline X", "laptop": "Crestline Pro", "reloj": "Crestline Watch"}
    return next((v for k, v in aliases.items() if re.search(r"\b"+k+r"s?\b", q)), None)


def resolve_followup(question, history):
    """Carry over only the previous user's subject for explicitly elliptical follow-ups."""
    if not history or not re.match(r"^(and\b|what about\b|how about\b|y\b|¿?y\b|ahora\b)", question.strip(), re.I):
        return question
    previous = history[-1].get("resolved_question") or history[-1].get("question", "")
    if product_in(question):
        for product in PRODUCTS:
            previous = re.sub(re.escape(product), "", previous, flags=re.I)
    if re.search(r"\bq[1-4]\b", question, re.I):
        previous = re.sub(r"\bq[1-4]\b", "", previous, flags=re.I)
    if re.search(r"\b20\d{2}\b", question):
        previous = re.sub(r"\b20\d{2}\b", "", previous)
    return f"{previous} {question}"[-1500:]


def blocked(question):
    return bool(re.search(r"ignore (all |the )?(previous|instructions)|system prompt|api.?key|password|contrase[nñ]a|clave secreta|\b(drop|truncate|insert|delete|update)\s+(table|from|into|crestline)|ignora.*instruccion", normalize(question)))


def route(question):
    q = normalize(question)
    if blocked(q):
        return "unknown"
    # Policy questions about headcount are not counts of employees.
    if re.search(r"(request|increase|approval|solicitar|aumentar).*(headcount|staff|plantilla)", q):
        return "hr"
    if re.search(r"\b(sold|sales|revenue|units|headcount|salary|salaries|mrr|churn|nps|ventas|vendieron|vendidos|ingresos|salario|salarios)\b", q):
        return "sql"
    if re.search(r"(how many|count|cuantos|cuantas).*(employee|people|engineering|department|empleado|ingenier|marketing|sales|finance)", q):
        return "sql"
    if re.search(r"(campaign|campana).*(budget|ctr|click|impression|conversion|presupuesto)|(?:budget|ctr|click|impression|conversion|presupuesto).*(campaign|campana)", q):
        return "sql"
    if re.search(r"\b(pto|vacation|vacaciones|onboarding|remote|remoto|hybrid|hibrido|benefits|beneficios|carryover|stipend|subsidio|hr)\b", q):
        return "hr"
    if re.search(r"campaign|campana|marketing|launch|lanzamiento|target audience|publico objetivo|brand", q):
        return "marketing"
    if re.search(r"\b(api|os|cloud|product|producto|requirements|requisitos|changelog|version|features|funciones|endpoints)\b", q):
        return "product"
    return "unknown"
