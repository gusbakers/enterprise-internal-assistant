import re

from crestline.embeddings import embed, vector_literal
from crestline.models import Evidence
from crestline.routing import normalize, product_in


def retrieve(db, question, domain, limit=3):
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
    # Expand vocabulary, never evidence: facts still come only from stored chunks.
    retrieval_question = question
    translations = {"vacaciones": "paid time off PTO policy", "remoto": "remote work", "requisitos": "system requirements", "publico objetivo": "target audience", "onboarding": "new employee onboarding required documents"}
    for phrase, expansion in translations.items():
        if phrase in q:
            retrieval_question += " " + expansion
    query_vector = vector_literal(embed([retrieval_question])[0])
    source_pattern = "%" + (allowed_source or "") + "%"
    # Filter before ranking, so unrelated sources cannot crowd out the right document.
    dense = db.read("SELECT id,source,section,content,1-(embedding <=> %s::vector) AS similarity "
                    "FROM crestline.chunks WHERE domain=%s AND source LIKE %s "
                    "ORDER BY embedding <=> %s::vector LIMIT 12",
                    (query_vector, domain, source_pattern, query_vector))
    lexical = db.read("SELECT id,source,section,content,1-(embedding <=> %s::vector) AS similarity, "
                      "ts_rank_cd(to_tsvector('english',content),plainto_tsquery('english',%s)) AS rank "
                      "FROM crestline.chunks WHERE domain=%s AND source LIKE %s "
                      "AND to_tsvector('english',content) @@ plainto_tsquery('english',%s) "
                      "ORDER BY rank DESC LIMIT 12",
                      (query_vector, question, domain, source_pattern, question))
    ranks, candidates = {}, {}
    for results in (dense, lexical):
        for index, item in enumerate(results):
            ranks[item["id"]] = ranks.get(item["id"], 0) + 1/(60+index+1)
            candidates[item["id"]] = item
    lexical_ids = {item["id"] for item in lexical}
    filtered = [item for item in candidates.values() if item["similarity"] >= .30 or item["id"] in lexical_ids]
    filtered.sort(key=lambda x:ranks[x["id"]], reverse=True)
    return [Evidence(f"S{i}", item["source"]+" — "+item["section"], item["content"], round(item["similarity"],4)) for i,item in enumerate(filtered[:limit],1)]
