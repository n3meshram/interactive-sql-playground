# Interactive SQL Learning & Revision Playground

An interactive, offline-first client-side learning platform that compiles a WebAssembly-powered SQLite database engine directly in the browser. Practice and master SQL anywhere with zero local configuration!

👉 **Playground Dashboard File:** [`sql.html`](./sql.html) (Simply download and double-click to open in any browser).

---

## 🚀 Key Features

* **In-Browser WebAssembly SQL Engine**: Uses `sql.js` (WebAssembly-compiled SQLite) client-side. Executes queries instantly without connecting to external servers or databases.
* **36 Hands-on Practice Labs**: 12 core SQL topics, each featuring **3 progressive labs** (Lab 1: Easy, Lab 2: Medium, Lab 3: Hard) to practice query writing daily.
* **Visual Kid-Friendly Revision Guides**: Clear, metaphorical breakdowns modeled after everyday analogies (e.g. JOINs as *matching socks*, EXISTS checks as *doorbells*, NULLs as *ghosts*) to build an intuitive mental model.
* **ETL & Data Engineering Context**: Injects production pro-tips tailored for Data Engineering workflows—detailing Slowly Changing Dimensions (SCD Type 1/2), CDC timelines, join explosions, and PySpark equivalents.
* **Real-time Query Verification**: Automatically compares the columns, data types, and values of your queries against the target solutions, triggering confetti celebrations on success.
* **Offline Persistence**: Synced progress indicators and editor code templates are persisted directly inside the browser's `localStorage`.

---

## 🗄️ Pre-seeded Datasets

The playground is pre-populated with 5 relational tables to simulate ETL environments:
1. `customers`: customer lists, active statuses, regions, and cities.
2. `orders`: transaction history, date timestamps, order amounts, and duplicate version updates.
3. `employees`: employee rosters, salaries, departments, and manager-hierarchy chains.
4. `departments`: corporate departments (Engineering, Sales, HR, Marketing).
5. `sales`: regional sales performance records.

Detailed column structures and row counts are browsable live via the slide-out **Schema Explorer** drawer.

---

## 📁 Repository Structure

* [`sql.html`](./sql.html): The final compiled single-page visual learning playground.
* [`parse_sql_playground.py`](./parse_sql_playground.py): The Python compiler script that parses revision notes and constructs the WebAssembly portal template.
* [`validate_html.py`](./validate_html.py): A structure validator script that scans the compiled document for nested tag balance.
* [`sql.txt`](./sql.txt): The raw markdown study notes.

---

## 💻 How to Use

1. Clone or download this repository.
2. Open [`sql.html`](./sql.html) in Chrome, Edge, Safari, or Firefox.
3. Browse the **Revision Notes** to review kid-friendly theory analogies.
4. Switch to the **Playground** tab of any topic to start writing queries.
5. Click **Run Query** (or press `Ctrl+Enter`) to test outputs, click **Verify Answer** to check correctness, and use **Show Solution 💡** if you get stuck.
