# ⚡ RoleRadar

A zero-dependency, lightweight job and internship application tracking pipeline built to manage software engineering roles, enforce valid status state machine transitions, and generate live spending and recruitment analytics.

---

## 🚀 Key Features

- **Application Pipeline Tracking:** Store and manage job postings, company names, application dates, and tracking links.
- **State Machine Enforcement:** Prevents illegal application state jumps (e.g., transitioning directly from `APPLIED` to `OFFER` without intermediate interview stages).
- **Aggregated Analytics Engine:** Uses native SQL aggregate queries to compute total applications, active interview counts, and offer conversion stats.
- **Zero-Dependency Architecture:** Engineered 100% with native Python standard libraries (`http.server`, `sqlite3`, `json`) to run smoothly across any environment without external packages.
- **Modern Responsive UI:** Features light-mode dashboard styling with color-gradient stat cards and dynamic fetch calls.

---

## 🛠️ Tech Stack

- **Backend:** Python 3 (Native `http.server` REST API)
- **Database:** SQLite3
- **Frontend:** HTML5, CSS3, Vanilla JavaScript (ES6+ `fetch` API)
- **Version Control:** Git, GitHub

---

## 📁 Repository Structure

```text
RoleRadar/
├── app/
│   ├── __init__.py      # Package indicator
│   ├── database.py    # Native SQLite database schema & connection
│   ├── logic.py       # State machine rules & input validation
│   └── main.py        # Native HTTP server & REST endpoint routes
├── static/
│   ├── index.html     # Dashboard layout
│   ├── style.css      # Light theme & color gradient cards
│   └── app.js         # Frontend state & API integration
├── .gitignore         # Git tracking rules
└── README.md          # Project documentation
