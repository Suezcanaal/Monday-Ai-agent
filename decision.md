# Project Report: Monday.com Enterprise BI Agent

**Developer:** Maralingeshwar
**Project Date:** February 2026
**Status:** Production Ready

---

## 1. Executive Summary
This project involved the end-to-end development of a **Business Intelligence (BI) Agent** designed for executive-level oversight of Monday.com operational and financial boards. The system bridges the gap between raw, fragmented data and high-level leadership decision-making.

### Technical Achievements
* **Multi-Board Intelligence:** Engineered a routing system to distinguish between **Sales Pipelines** and **Work Orders** based on natural language intent.
* **Automated Data Cleaning:** Developed a resilient pipeline to standardize inconsistent European/ISO date formats and currency strings.
* **Time-Aware Analysis:** Built a custom logic engine to calculate bottlenecks and overdue items by comparing target dates against current timestamps.
* **Robust Connectivity:** Implemented a **Persistent Session Manager** featuring connection pooling and exponential backoff for API rate-limit handling.



---

## 2. Decision Log

### Trade-offs Chosen and Why
* **Ad-Hoc Analysis vs. Static Reporting:** I chose an ad-hoc engine. While static reports are faster, ad-hoc analysis allows leadership to ask unique questions without requiring manual report building.
* **Streamlit Framework:** I chose Streamlit for the interface. The trade-off was highly customized UI design in exchange for rapid deployment and native integration with data science libraries.
* **Explicit Mapping Config:** I opted for a manual mapping file. While AI could "guess" columns, manual mapping ensures 100% financial accuracy, which is critical for leadership reporting.

### What I'd Do Differently with More Time
* **Cross-Board Joins:** Implement features to link boards (e.g., showing Work Orders linked to specific High-Value Deals).
* **Proactive Alerts:** Build a background worker to push Slack/Email notifications when deals exceed a 90-day delay threshold.

---

## 3. Quality Assurance: 20 Test Queries

The following queries were used to verify the system's robustness in Routing, Analytics, and Data Health.

### Sales & Revenue (Deals Board)
1. "Show me the **pipeline summary**."
2. "What is the total **revenue by Sector**?"
3. "How many **deals** are in the **Mining** sector?"
4. "Show me **revenue by Stage**."
5. "Which **Owner** has the most **deals**?"
6. "List all deals with **High probability**."
7. "Show me a breakdown of **deals by Status**."

### Operations (Work Orders Board)
8. "Show me all **work orders**."
9. "What is the **execution status** of projects?"
10. "Total **value of work orders** by Sector."
11. "How many projects are **Completed**?"
12. "Show me **work orders** handled by **OWNER_003**."
13. "Break down projects by **Nature of Work**."
14. "Show me the **budget** for **Powerline** projects."

### Time & Risk Analysis
15. "How many deals are **delayed** more than **60 days**?"
16. "Show me **overdue items**."
17. "Which deals are **late**?"
18. "List items **delayed by 30 days**."

### Data Quality & Search
19. "Who is working on **Scooby-Doo**?"
20. "Show me **unknown** owners."

---

## 4. Leadership Updates & Interpretation
I interpreted "Leadership Updates" as the requirement for **Summarization and Significance**.
* **Summarization:** Leaders require totals (e.g., "Revenue is $4.8M") rather than individual line items.
* **Significance:** I added "Contextual Insights" to identify top performers, providing the relative position of numbers within the business.
* **Actionability:** Every response is designed to lead to a clear business action, such as addressing a specific "Delay Alert."