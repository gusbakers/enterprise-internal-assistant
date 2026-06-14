"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRESTLINE TECHNOLOGIES — SQL TOOL
Role: Backend Engineer
Block: 2 — RAG Core
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Handles: sales, employees, campaigns, metrics
Source: data/crestline.db (SQLite)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import sqlite3
import re

DB_PATH = "./data/crestline.db"


class SQLTool:
    def __init__(self):
        self.db_path = DB_PATH

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _detect_table(self, query: str) -> str:
        """Detect which table to query based on keywords."""
        q = query.lower()

        sales_keywords = [
            "sold", "sales", "units", "revenue", "product",
            "market", "quarter", "q1", "q2", "q3", "q4",
            "crestline x", "crestline pro", "crestline watch",
            "crestline os", "crestline cloud", "laptop", "phone",
            "watch", "smartphone", "computer",
        ]
        employee_keywords = [
            "employee", "employees", "staff", "headcount", "people",
            "engineer", "manager", "department", "salary", "hired",
            "team", "who works", "how many people", "role",
        ]
        campaign_keywords = [
            "campaign", "marketing", "budget", "channel", "impression",
            "click", "conversion", "ctr", "launch", "advertis",
            "instagram", "linkedin", "youtube", "google ads",
        ]
        metrics_keywords = [
            "mrr", "revenue", "churn", "active users", "customers",
            "nps", "monthly", "kpi", "growth", "retention", "metric",
        ]

        scores = {
            "sales":     sum(1 for k in sales_keywords if k in q),
            "employees": sum(1 for k in employee_keywords if k in q),
            "campaigns": sum(1 for k in campaign_keywords if k in q),
            "metrics":   sum(1 for k in metrics_keywords if k in q),
        }

        return max(scores, key=scores.get)

    def _extract_quarter(self, query: str) -> str | None:
        match = re.search(r'\b(q[1-4])\b', query.lower())
        return match.group(1).upper() if match else None

    def _extract_product(self, query: str) -> str | None:
        products = [
            "Crestline X", "Crestline Pro",
            "Crestline Watch", "Crestline OS", "Crestline Cloud",
        ]
        for p in products:
            if p.lower() in query.lower():
                return p
        # Common aliases
        if "phone" in query.lower() or "smartphone" in query.lower():
            return "Crestline X"
        if "laptop" in query.lower() or "computer" in query.lower():
            return "Crestline Pro"
        if "watch" in query.lower() or "smartwatch" in query.lower():
            return "Crestline Watch"
        if "cloud" in query.lower():
            return "Crestline Cloud"
        if "os" in query.lower() or "software" in query.lower():
            return "Crestline OS"
        return None

    def _extract_department(self, query: str) -> str | None:
        departments = [
            "Engineering", "Product", "Marketing",
            "Sales", "HR", "Finance",
        ]
        for dept in departments:
            if dept.lower() in query.lower():
                return dept
        return None

    # ── Queries ────────────────────────────────────────────────────

    def _query_sales(self, query: str) -> list[dict]:
        conn = self._connect()
        product  = self._extract_product(query)
        quarter  = self._extract_quarter(query)
        q = query.lower()

        if "top" in q or "best" in q or "highest" in q:
            sql = """
                SELECT product, SUM(units_sold) AS total_units,
                       ROUND(SUM(revenue), 2) AS total_revenue
                FROM sales
                GROUP BY product
                ORDER BY total_revenue DESC
            """
            rows = conn.execute(sql).fetchall()

        elif product and quarter:
            sql = """
                SELECT product, quarter, SUM(units_sold) AS units,
                       ROUND(SUM(revenue), 2) AS revenue, market
                FROM sales
                WHERE product = ? AND quarter = ?
                GROUP BY product, quarter
            """
            rows = conn.execute(sql, (product, quarter)).fetchall()

        elif product:
            sql = """
                SELECT product, month, year, units_sold, revenue, market
                FROM sales
                WHERE product = ?
                ORDER BY year, month
            """
            rows = conn.execute(sql, (product,)).fetchall()

        elif quarter:
            sql = """
                SELECT product, quarter,
                       SUM(units_sold) AS units,
                       ROUND(SUM(revenue), 2) AS revenue
                FROM sales
                WHERE quarter = ?
                GROUP BY product
                ORDER BY revenue DESC
            """
            rows = conn.execute(sql, (quarter,)).fetchall()

        else:
            sql = """
                SELECT product,
                       SUM(units_sold) AS total_units,
                       ROUND(SUM(revenue), 2) AS total_revenue
                FROM sales
                GROUP BY product
                ORDER BY total_revenue DESC
            """
            rows = conn.execute(sql).fetchall()

        conn.close()
        return [dict(r) for r in rows]

    def _query_employees(self, query: str) -> list[dict]:
        conn  = self._connect()
        dept  = self._extract_department(query)
        q     = query.lower()

        if "how many" in q or "count" in q or "headcount" in q:
            if dept:
                sql  = "SELECT department, COUNT(*) AS count FROM employees WHERE department = ? GROUP BY department"
                rows = conn.execute(sql, (dept,)).fetchall()
            else:
                sql  = "SELECT department, COUNT(*) AS count FROM employees GROUP BY department ORDER BY count DESC"
                rows = conn.execute(sql).fetchall()

        elif "salary" in q or "paid" in q or "earn" in q:
            if dept:
                sql  = """
                    SELECT department,
                           ROUND(AVG(salary), 0) AS avg_salary,
                           MIN(salary) AS min_salary,
                           MAX(salary) AS max_salary
                    FROM employees WHERE department = ?
                    GROUP BY department
                """
                rows = conn.execute(sql, (dept,)).fetchall()
            else:
                sql  = """
                    SELECT department,
                           ROUND(AVG(salary), 0) AS avg_salary,
                           MIN(salary) AS min_salary,
                           MAX(salary) AS max_salary
                    FROM employees GROUP BY department
                    ORDER BY avg_salary DESC
                """
                rows = conn.execute(sql).fetchall()

        elif dept:
            sql  = "SELECT name, role, department, salary, location FROM employees WHERE department = ? LIMIT 10"
            rows = conn.execute(sql, (dept,)).fetchall()

        else:
            sql  = "SELECT department, COUNT(*) AS count FROM employees GROUP BY department ORDER BY count DESC"
            rows = conn.execute(sql).fetchall()

        conn.close()
        return [dict(r) for r in rows]

    def _query_campaigns(self, query: str) -> list[dict]:
        conn    = self._connect()
        product = self._extract_product(query)
        quarter = self._extract_quarter(query)

        if product and quarter:
            sql  = "SELECT * FROM campaigns WHERE product = ? AND quarter = ?"
            rows = conn.execute(sql, (product, quarter)).fetchall()
        elif product:
            sql  = "SELECT * FROM campaigns WHERE product = ? ORDER BY year, quarter"
            rows = conn.execute(sql, (product,)).fetchall()
        elif quarter:
            sql  = "SELECT * FROM campaigns WHERE quarter = ? ORDER BY budget DESC"
            rows = conn.execute(sql, (quarter,)).fetchall()
        else:
            sql  = """
                SELECT product, SUM(budget) AS total_budget,
                       SUM(impressions) AS total_impressions,
                       ROUND(AVG(ctr), 2) AS avg_ctr
                FROM campaigns GROUP BY product
                ORDER BY total_budget DESC
            """
            rows = conn.execute(sql).fetchall()

        conn.close()
        return [dict(r) for r in rows]

    def _query_metrics(self, query: str) -> list[dict]:
        conn = self._connect()
        q    = query.lower()

        if "latest" in q or "last" in q or "recent" in q:
            sql  = "SELECT * FROM metrics ORDER BY year DESC, month DESC LIMIT 3"
            rows = conn.execute(sql).fetchall()
        elif "best" in q or "highest" in q or "peak" in q:
            sql  = "SELECT * FROM metrics ORDER BY mrr DESC LIMIT 3"
            rows = conn.execute(sql).fetchall()
        elif "churn" in q:
            sql  = "SELECT month, year, churn_rate FROM metrics ORDER BY churn_rate ASC"
            rows = conn.execute(sql).fetchall()
        elif "nps" in q:
            sql  = "SELECT month, year, nps_score FROM metrics ORDER BY nps_score DESC"
            rows = conn.execute(sql).fetchall()
        else:
            sql  = "SELECT * FROM metrics ORDER BY year, month"
            rows = conn.execute(sql).fetchall()

        conn.close()
        return [dict(r) for r in rows]

    # ── Public interface ───────────────────────────────────────────

    def run(self, query: str) -> str:
        table = self._detect_table(query)

        try:
            if table == "sales":
                rows = self._query_sales(query)
            elif table == "employees":
                rows = self._query_employees(query)
            elif table == "campaigns":
                rows = self._query_campaigns(query)
            else:
                rows = self._query_metrics(query)

            if not rows:
                return f"No data found for: {query}"

            # Format as readable text
            lines = [f"📊 SQL Results from table [{table}]:"]
            for row in rows[:10]:  # cap at 10 rows
                lines.append("  " + " | ".join(f"{k}: {v}" for k, v in row.items()))

            return "\n".join(lines)

        except Exception as e:
            return f"SQL error: {str(e)}"


