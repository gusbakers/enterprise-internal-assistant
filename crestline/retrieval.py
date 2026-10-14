import re

from crestline.embeddings import embed, vector_literal
from crestline.models import Evidence
from crestline.routing import normalize, product_in


def retrieve(db, question, domain, limit=3):
    query_vector = vector_literal(embed([question])[0])
    # Exact cosine search is intentional for this small corpus; no approximate recall loss.
    dense = db.read("SELECT id,source,section,content,1-(embedding <=> %s::vector) AS similarity "
                    "FROM crestline.chunks WHERE domain=%s ORDER BY embedding <=> %s::vector LIMIT 12",
                    (query_vector, domain, query_vector))
    lexical = db.read("SELECT id,source,section,content,ts_rank_cd(to_tsvector('english',content), "
                      "plainto_tsquery('english',%s)) AS rank FROM crestline.chunks WHERE domain=%s "
                      "AND to_tsvector('english',content) @@ plainto_tsquery('english',%s) ORDER BY rank DESC LIMIT 12",
                      (question, domain, question))
    ranks = {}
    for results in (dense, lexical):
        for index, item in enumerate(results):
            ranks[item["id"]] = ranks.get(item["id"], 0) + 1/(60+index+1)
    q = normalize(question)
    product = product_in(question)
    allowed_source = None
    if domain == "marketing" and product:
        allowed_source = {"Crestline X":"crestline_x_launch", "Crestline Pro":"crestline_pro_campaign", "Crestline Watch":"crestline_watch_campaign"}.get(product)
        if not allowed_source:
            return []
    if domain == "hr":
        if re.search(r"pto|vacation|vacaciones|carryover", q): allowed_source="pto_policy"
        elif re.search(r"remote|remoto|hybrid|hibrido|stipend|subsidio", q): allowed_source="remote_work_policy"
        elif "onboarding" in q: allowed_source="onboarding_guide"
    if domain == "product":
        if "api" in q or "endpoint" in q: allowed_source="cloud_api_docs"
        elif "requirements" in q or "requisitos" in q: allowed_source="system_requirements"
        elif "changelog" in q or re.search(r"\bv3\.|\bversion|changed|cambio", q): allowed_source="crestline_os_changelog"
    filtered = [item for item in dense if item["similarity"] >= .30 and (not allowed_source or allowed_source in item["source"])]
    filtered.sort(key=lambda x:ranks[x["id"]], reverse=True)
    return [Evidence(f"S{i}", item["source"]+" — "+item["section"], item["content"], round(item["similarity"],4)) for i,item in enumerate(filtered[:limit],1)]
