import calendar
import json
import re
import time

from crestline.answers import concise_evidence
from crestline.gemini import Gemini
from crestline.models import Evidence, Result
from crestline.retrieval import retrieve
from crestline.routing import blocked, normalize, resolve_followup, route, spanish
from crestline.sql import plan


class Assistant:
    def __init__(self, db, llm=None):
        self.db = db
        self.llm = llm or Gemini()

    def ask(self, question, history=None):
        start=time.monotonic()
        if not question.strip() or len(question)>1500:
            return Result("Please enter a question between 1 and 1,500 characters.","unknown",mode="needs clarification")
        resolved = resolve_followup(question, history or [])
        domain = route(resolved)
        result=Result("",domain,resolved_question=resolved)
        language = "Spanish" if spanish(question) else "English"
        if blocked(question):
            result.answer="I can answer questions about the demo documents and aggregate business data. I cannot reveal credentials or execute instructions to modify data."
            result.mode="out of scope"
        elif domain == "unknown":
            result.answer="I don't have evidence for that question. Ask about Crestline's PTO, remote work, campaigns, product documentation, or 2024 business metrics."
            result.mode="out of scope"
        elif domain == "sql":
            query=plan(resolved)
            if query.error:
                result.answer=query.error; result.mode="needs clarification"
            else:
                rows=self.db.read(query.sql,query.params)
                result.rows=rows; result.sql=query.sql; result.parameters=query.params
                if not rows or all(v is None for row in rows for v in row.values()):
                    result.answer="No matching records are available for those filters."; result.mode="no evidence"
                else:
                    result.evidence=[Evidence("S1",f"PostgreSQL · {query.table}",json.dumps({"scope":query.note,"rows":rows},default=str))]
                    display_rows=rows[:3]
                    if not re.search(r'revenue|ingresos|recaud',normalize(resolved)) and any('units_sold' in row for row in display_rows):
                        display_rows=[{k:v for k,v in row.items() if k!='revenue'} for row in display_rows]
                    result.answer=self.format_rows(display_rows)+" [S1]"
                    if len(rows)>3:
                        result.answer+="\n\nMore results are available in Data."
        else:
            q=normalize(resolved)
            if re.search(r"headcount.*increase|request.*headcount|stock price|share price|precio.*accion|ceo.*salary", q):
                result.evidence=[]
            else:
                result.evidence=retrieve(self.db,resolved,domain)
            if result.evidence:
                result.answer=concise_evidence(resolved,result.evidence)
                result.mode="source excerpts"
            else:
                result.answer="I couldn't find sufficient evidence in the available documents to answer that. Please clarify the topic or product."
                result.mode="no evidence"
        if result.evidence:
            answer,notice=self.llm.answer(resolved,result.evidence,language)
            result.notice=notice
            if answer:
                result.answer=answer; result.mode="Gemini + verified sources"
        result.elapsed_ms=round((time.monotonic()-start)*1000)
        return result

    @staticmethod
    def format_rows(rows):
        def number(value, key):
            if key=="year": return str(int(value))
            if key=="month" and 1<=int(value)<=12: return calendar.month_name[int(value)]
            if isinstance(value,(int,float)) or type(value).__name__=="Decimal":
                return f"{value:,.2f}" if float(value)%1 else f"{int(value):,}"
            return str(value)
        return "\n".join("- "+" · ".join(f"{key.replace('_',' ').title()}: **{number(value,key)}**" for key,value in row.items()) for row in rows)
