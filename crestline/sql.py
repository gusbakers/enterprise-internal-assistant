"""Validated, parameterized analytics. No user or LLM SQL is ever executed."""
import re
from dataclasses import dataclass, field

from crestline.routing import normalize, product_in, PRODUCTS


@dataclass
class Query:
    sql: str = ""
    params: list = field(default_factory=list)
    note: str = ""
    error: str = ""
    table: str = "sales"


def plan(question):
    q = normalize(question)
    if sum(bool(re.search(r"\b"+re.escape(p.lower())+r"\b",q)) for p in PRODUCTS)>1:
        return Query(error="Please ask for one product at a time, or ask for a ranking across all products.")
    if re.search(r"customer|cliente|purchase volume|sales.*channel|ventas.*canal", q):
        return Query(error="The dataset has no customer-level purchases or sales channels. I cannot calculate that breakdown.")
    if re.search(r"last quarter|past year|last year|ultimo trimestre|ano pasado|today|hoy|current|actual", q):
        return Query(error="The business dataset covers 2024. Please specify a quarter such as Q4 2024; relative dates could refer to a period with no data.")
    years = list(dict.fromkeys(re.findall(r"\b20\d{2}\b", q)))
    if len(years) > 1 or (years and years[0] != "2024"):
        return Query(error="Only 2024 business records are available. I cannot report results for other years.")
    quarters = list(dict.fromkeys(re.findall(r"\bq[1-4]\b", q)))
    if len(quarters) > 1 or re.search(r"compare|comparison|versus|compar|\bvs\b", q):
        return Query(error="Please ask for one product and one period at a time. Cross-period comparisons are not implemented.")
    if re.search(r"request|solicitar|increase|aumentar", q) and "headcount" in q:
        return Query(error="The available documents do not describe the headcount-increase approval process.")
    if re.search(r"employee|headcount|salary|salaries|empleado|salario|how many.*(engineering|department)|cuantos.*ingenier", q):
        params = []
        where = ""
        departments = {"engineering": "Engineering", "ingenieria": "Engineering", "marketing": "Marketing", "product": "Product", "sales": "Sales", "finance": "Finance", "hr": "HR"}
        dept = next((v for k,v in departments.items() if re.search(r"\b"+k+r"\b", q)), None)
        if dept:
            where = " WHERE department = %s"
            params.append(dept)
        if re.search(r"salary|salaries|salario", q):
            if not re.search(r"average|avg|promedio|department|departamento", q):
                return Query(error="This public demo provides aggregate salary statistics only, not individual employee compensation.")
            select = "department, ROUND(SUM(average_salary*employee_count)/SUM(employee_count),2) AS average_salary"
            group = " GROUP BY department ORDER BY department"
        elif re.search(r"how many|count|headcount|cuantos|cuantas|cantidad", q):
            select = "SUM(employee_count) AS employee_count"
            group = ""
            if re.search(r"by department|por departamento", q):
                select = "department, SUM(employee_count) AS employee_count"
                group = " GROUP BY department ORDER BY employee_count DESC, department"
        else:
            return Query(error="Ask for employee counts or average salary by department. Individual employee records are not exposed.")
        return Query("SELECT "+select+" FROM crestline.employees"+where+group, params, "Employee snapshot in the demo dataset.", table="employees")

    where, params = ["year = %s"], [2024]
    product = product_in(question)
    if product:
        where.append("product = %s"); params.append(product)
    if quarters:
        where.append("quarter = %s"); params.append(quarters[0].upper())
    months = {"january":1,"enero":1,"february":2,"febrero":2,"march":3,"marzo":3,
              "april":4,"abril":4,"may":5,"mayo":5,"june":6,"junio":6,"july":7,"julio":7,
              "august":8,"agosto":8,"september":9,"septiembre":9,"october":10,"octubre":10,
              "november":11,"noviembre":11,"december":12,"diciembre":12}
    month_values = set(v for k,v in months.items() if re.search(r"\b"+k+r"\b",q))
    if len(month_values)>1:
        return Query(error="Please specify one month or a quarter. Custom month ranges are not implemented.")
    if month_values:
        where.append("month = %s"); params.append(next(iter(month_values)))
    markets = {"usa":"USA", "united states":"USA", "estados unidos":"USA", "canada":"Canada", "uk":"UK", "united kingdom":"UK"}
    for alias, value in markets.items():
        if re.search(r"\b"+alias+r"\b", q):
            where.append("market = %s"); params.append(value); break
    clause = " WHERE " + " AND ".join(where)
    if re.search(r"campaign|campana", q):
        if month_values:
            return Query(error="Campaign data is quarterly. Please specify Q1, Q2, Q3 or Q4 2024.")
        if any("market" in x for x in where):
            return Query(error="Campaign records do not include geographic markets.")
        return Query("SELECT product, quarter, year, SUM(budget) AS budget, SUM(impressions) AS impressions, "
                     "SUM(clicks) AS clicks, SUM(conversions) AS conversions, "
                     "ROUND(100.0*SUM(clicks)/NULLIF(SUM(impressions),0),2) AS ctr_percent "
                     "FROM crestline.campaigns"+clause+" GROUP BY product,quarter,year ORDER BY year,quarter,product", params,
                     "Recorded campaign metrics; campaign briefs contain planned budgets and targets.", table="campaigns")
    if re.search(r"\b(mrr|churn|nps|active users|usuarios activos)\b", q):
        if product or quarters or any("market" in x for x in where):
            return Query(error="Monthly company metrics are not broken down by product, market, or quarter. Ask for monthly MRR, churn, or NPS in 2024.")
        return Query("SELECT month,year,mrr,churn_rate,nps_score,active_users FROM crestline.metrics WHERE year=%s ORDER BY year,month", [2024], "Monthly company-wide metrics; churn is a percentage.", table="metrics")
    revenue = bool(re.search(r"revenue|ingresos", q))
    rank = "revenue" if revenue else "units_sold"
    grouping = ""
    if re.search(r"month|monthly|\bmes\b|mensual", q):
        grouping = "year, month"
    elif re.search(r"region|market|mercado", q):
        # A single named market is a filter; a breakdown is a grouping.
        grouping = "market"
    elif re.search(r"top|best|highest|ranking|mejor|mayor|mas vendido|by product|por producto", q):
        grouping = "product"
    select = (grouping + ", " if grouping else "") + "SUM(units_sold) AS units_sold, ROUND(SUM(revenue),2) AS revenue"
    sql = "SELECT "+select+" FROM crestline.sales"+clause
    if grouping:
        sql += " GROUP BY "+grouping
        if re.search(r"top|best|highest|mejor|mayor|mas vendido", q):
            sql += f" ORDER BY {rank} DESC, {grouping}"
            n = re.search(r"\btop\s+(\d+)\b", q)
            limit = min(int(n.group(1)), 20) if n else 1
            sql += " LIMIT %s"; params.append(limit)
        else:
            sql += " ORDER BY "+grouping
    return Query(sql, params, "Period: " + (quarters[0].upper()+" " if quarters else "") + "2024. Revenue is USD; units are units sold.")
