import os
import re
import html
import json

# Path configuration
SOURCE_FILE = r"D:\Desktop\sql.txt"
OUTPUT_FILE = r"D:\Desktop\sql.html"

# Category list to distinguish category headings from normal sections
CATEGORIES = [
    "INTRODUCTION",
    "PHASE 1",
    "DAILY REVISION",
    "PENDING SQL TOPICS ROADMAP",
    "CHEAT SHEET",
    "CASE WHEN",
    "FINAL GOAL"
]

# Practice challenges mapped to topic slugs (3 labs per topic)
CHALLENGES = {
    "1-basic-select-filtering": [
        {
            "title": "Lab 1: Select Active Customers",
            "prompt": "Write a query to SELECT the <code>customer_name</code> and <code>city</code> for all active customers in 'Mumbai' from the <code>customers</code> table.",
            "targetQuery": "SELECT customer_name, city FROM customers WHERE status = 'Active' AND city = 'Mumbai'",
            "initialCode": "SELECT customer_name, city\\nFROM customers\\nWHERE status = 'Active' AND city = 'Mumbai';"
        },
        {
            "title": "Lab 2: Select Large Orders",
            "prompt": "Write a query to select the <code>order_id</code> and <code>order_amount</code> for all orders in the <code>orders</code> table where the <code>order_amount</code> is strictly greater than 2000.",
            "targetQuery": "SELECT order_id, order_amount FROM orders WHERE order_amount > 2000",
            "initialCode": "SELECT order_id, order_amount\\nFROM orders\\nWHERE order_amount > 2000;"
        },
        {
            "title": "Lab 3: Filter Regions & Status",
            "prompt": "Select <code>customer_name</code>, <code>city</code>, and <code>region</code> for all active customers located in the 'West' or 'North' region.",
            "targetQuery": "SELECT customer_name, city, region FROM customers WHERE status = 'Active' AND region IN ('West', 'North')",
            "initialCode": "SELECT customer_name, city, region\\nFROM customers\\nWHERE status = 'Active' AND region IN ('West', 'North');"
        }
    ],
    "2-group-by-having": [
        {
            "title": "Lab 1: Customer Count by City",
            "prompt": "Find how many customers are in each city. Select the <code>city</code> and the count of customers as <code>customer_count</code>, grouped by city.",
            "targetQuery": "SELECT city, COUNT(*) as customer_count FROM customers GROUP BY city",
            "initialCode": "SELECT city, COUNT(*) as customer_count\\nFROM customers\\nGROUP BY city;"
        },
        {
            "title": "Lab 2: Average Salary per Department",
            "prompt": "Calculate the average salary for each department. Select <code>department_id</code> and the average salary as <code>avg_salary</code> from the <code>employees</code> table, grouped by department_id.",
            "targetQuery": "SELECT department_id, AVG(salary) as avg_salary FROM employees GROUP BY department_id",
            "initialCode": "SELECT department_id, AVG(salary) as avg_salary\\nFROM employees\\nGROUP BY department_id;"
        },
        {
            "title": "Lab 3: Cities with Multiple Customers",
            "prompt": "Select the <code>city</code> and the count of customers as <code>customer_count</code> for cities that have strictly more than 1 customer.",
            "targetQuery": "SELECT city, COUNT(*) as customer_count FROM customers GROUP BY city HAVING COUNT(*) > 1",
            "initialCode": "SELECT city, COUNT(*) as customer_count\\nFROM customers\\nGROUP BY city\\nHAVING COUNT(*) > 1;"
        }
    ],
    "3-duplicate-detection": [
        {
            "title": "Lab 1: Duplicate Customers in Orders",
            "prompt": "Find the <code>customer_id</code>s who have placed more than 1 order in the <code>orders</code> table, along with their total order count as <code>order_count</code>.",
            "targetQuery": "SELECT customer_id, COUNT(*) as order_count FROM orders GROUP BY customer_id HAVING COUNT(*) > 1",
            "initialCode": "SELECT customer_id, COUNT(*) as order_count\\nFROM orders\\nGROUP BY customer_id\\nHAVING COUNT(*) > 1;"
        },
        {
            "title": "Lab 2: Duplicate Order Dates",
            "prompt": "Find any <code>customer_id</code> and <code>order_date</code> combination that appears more than once in the <code>orders</code> table. Return the <code>customer_id</code>, <code>order_date</code>, and the duplication count as <code>dup_count</code>.",
            "targetQuery": "SELECT customer_id, order_date, COUNT(*) as dup_count FROM orders GROUP BY customer_id, order_date HAVING COUNT(*) > 1",
            "initialCode": "SELECT customer_id, order_date, COUNT(*) as dup_count\\nFROM orders\\nGROUP BY customer_id, order_date\\nHAVING COUNT(*) > 1;"
        },
        {
            "title": "Lab 3: Duplicate Employee Names",
            "prompt": "Find any duplicate names in the <code>employees</code> table. Return the <code>employee_name</code> and the count of occurrences as <code>name_count</code> if the name appears more than once.",
            "targetQuery": "SELECT employee_name, COUNT(*) as name_count FROM employees GROUP BY employee_name HAVING COUNT(*) > 1",
            "initialCode": "SELECT employee_name, COUNT(*) as name_count\\nFROM employees\\nGROUP BY employee_name\\nHAVING COUNT(*) > 1;"
        }
    ],
    "4-null-validation": [
        {
            "title": "Lab 1: Employees Without Managers",
            "prompt": "Select the <code>employee_name</code> for all employees in the <code>employees</code> table who do not report to any manager (<code>manager_id</code> is NULL).",
            "targetQuery": "SELECT employee_name FROM employees WHERE manager_id IS NULL",
            "initialCode": "SELECT employee_name\\nFROM employees\\nWHERE manager_id IS NULL;"
        },
        {
            "title": "Lab 2: Missing Order Dates",
            "prompt": "Select all orders from the <code>orders</code> table where the <code>order_date</code> is NULL. (Note: The pre-seeded database has no null dates, but you should still write the correct validation structure).",
            "targetQuery": "SELECT * FROM orders WHERE order_date IS NULL",
            "initialCode": "SELECT *\\nFROM orders\\nWHERE order_date IS NULL;"
        },
        {
            "title": "Lab 3: Count Null Managers",
            "prompt": "Count the number of employees who do not have a manager. Return the count as <code>null_managers_count</code>.",
            "targetQuery": "SELECT COUNT(*) as null_managers_count FROM employees WHERE manager_id IS NULL",
            "initialCode": "SELECT COUNT(*) as null_managers_count\\nFROM employees\\nWHERE manager_id IS NULL;"
        }
    ],
    "6-row-number": [
        {
            "title": "Lab 1: Rank Salaries inside Department",
            "prompt": "Assign a strict row number to each employee inside their department, sorted by their salary from highest to lowest. Return <code>department_id</code>, <code>employee_name</code>, <code>salary</code>, and the row number as <code>sal_rn</code>.",
            "targetQuery": "SELECT department_id, employee_name, salary, ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) as sal_rn FROM employees",
            "initialCode": "SELECT department_id, employee_name, salary,\\n       ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) as sal_rn\\nFROM employees;"
        },
        {
            "title": "Lab 2: Order Sequence for Customers",
            "prompt": "For each customer in the <code>orders</code> table, number their orders sequentially based on the <code>order_date</code> (oldest first). Return <code>customer_id</code>, <code>order_id</code>, <code>order_date</code>, and the sequence number as <code>order_seq</code>.",
            "targetQuery": "SELECT customer_id, order_id, order_date, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date ASC) as order_seq FROM orders",
            "initialCode": "SELECT customer_id, order_id, order_date,\\n       ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date ASC) as order_seq\\nFROM orders;"
        },
        {
            "title": "Lab 3: Number Regions by Sales",
            "prompt": "Assign a row number to each sale in the <code>sales</code> table, partitioned by <code>region</code> and ordered by <code>sales_amount</code> descending. Return <code>region</code>, <code>sales_amount</code>, and the row number as <code>sale_rn</code>.",
            "targetQuery": "SELECT region, sales_amount, ROW_NUMBER() OVER (PARTITION BY region ORDER BY sales_amount DESC) as sale_rn FROM sales",
            "initialCode": "SELECT region, sales_amount,\\n       ROW_NUMBER() OVER (PARTITION BY region ORDER BY sales_amount DESC) as sale_rn\\nFROM sales;"
        }
    ],
    "7-rank-vs-dense-rank": [
        {
            "title": "Lab 1: Rank Salaries (with Gaps)",
            "prompt": "Rank all employees across the entire company by salary descending using the <code>RANK()</code> function. Return <code>employee_name</code>, <code>salary</code>, and the rank as <code>sal_rank</code>.",
            "targetQuery": "SELECT employee_name, salary, RANK() OVER (ORDER BY salary DESC) as sal_rank FROM employees",
            "initialCode": "SELECT employee_name, salary,\\n       RANK() OVER (ORDER BY salary DESC) as sal_rank\\nFROM employees;"
        },
        {
            "title": "Lab 2: Dense Rank Salaries (no Gaps)",
            "prompt": "Dense rank all employees across the entire company by salary descending using <code>DENSE_RANK()</code>. Return <code>employee_name</code>, <code>salary</code>, and the dense rank as <code>sal_dense_rank</code>.",
            "targetQuery": "SELECT employee_name, salary, DENSE_RANK() OVER (ORDER BY salary DESC) as sal_dense_rank FROM employees",
            "initialCode": "SELECT employee_name, salary,\\n       DENSE_RANK() OVER (ORDER BY salary DESC) as sal_dense_rank\\nFROM employees;"
        },
        {
            "title": "Lab 3: Side-by-Side Comparison",
            "prompt": "Select <code>employee_name</code>, <code>salary</code>, their <code>RANK()</code> as <code>rk</code>, and their <code>DENSE_RANK()</code> as <code>drk</code> side-by-side, ordered by salary DESC. Observe how ties are handled differently.",
            "targetQuery": "SELECT employee_name, salary, RANK() OVER (ORDER BY salary DESC) as rk, DENSE_RANK() OVER (ORDER BY salary DESC) as drk FROM employees ORDER BY salary DESC",
            "initialCode": "SELECT employee_name, salary,\\n       RANK() OVER (ORDER BY salary DESC) as rk,\\n       DENSE_RANK() OVER (ORDER BY salary DESC) as drk\\nFROM employees\\nORDER BY salary DESC;"
        }
    ],
    "8-latest-record-validation": [
        {
            "title": "Lab 1: Latest Order for Customer 1",
            "prompt": "Get the absolute latest order (highest <code>update_time</code>) for customer 1 from the <code>orders</code> table. Return <code>customer_id</code>, <code>order_id</code>, <code>order_amount</code>, and <code>update_time</code>.",
            "targetQuery": "SELECT customer_id, order_id, order_amount, update_time FROM (SELECT customer_id, order_id, order_amount, update_time, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY update_time DESC) as rn FROM orders) WHERE customer_id = 1 AND rn = 1",
            "initialCode": "SELECT customer_id, order_id, order_amount, update_time\\nFROM (\\n  SELECT customer_id, order_id, order_amount, update_time,\\n         ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY update_time DESC) as rn\\n  FROM orders\\n)\\nWHERE customer_id = 1 AND rn = 1;"
        },
        {
            "title": "Lab 2: Latest Order for All Customers",
            "prompt": "Write a query to extract the latest order (highest <code>update_time</code>) for each customer in the <code>orders</code> table. Return <code>customer_id</code>, <code>order_id</code>, <code>order_amount</code>, and <code>update_time</code>.",
            "targetQuery": "SELECT customer_id, order_id, order_amount, update_time FROM (SELECT customer_id, order_id, order_amount, update_time, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY update_time DESC) as rn FROM orders) WHERE rn = 1",
            "initialCode": "SELECT customer_id, order_id, order_amount, update_time\\nFROM (\\n  SELECT customer_id, order_id, order_amount, update_time,\\n         ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY update_time DESC) as rn\\n  FROM orders\\n)\\nWHERE rn = 1;"
        },
        {
            "title": "Lab 3: Highest Paid Employee per Department",
            "prompt": "Find the highest paid employee in each department. Return <code>department_id</code>, <code>employee_name</code>, and <code>salary</code>. (Hint: Use ROW_NUMBER partition by department_id order by salary desc, and filter where rn = 1).",
            "targetQuery": "SELECT department_id, employee_name, salary FROM (SELECT department_id, employee_name, salary, ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) as rn FROM employees) WHERE rn = 1",
            "initialCode": "SELECT department_id, employee_name, salary\\nFROM (\\n  SELECT department_id, employee_name, salary,\\n         ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) as rn\\n  FROM employees\\n)\\nWHERE rn = 1;"
        }
    ],
    "9-inner-join": [
        {
            "title": "Lab 1: Join Employees and Departments",
            "prompt": "Join the <code>employees</code> table and <code>departments</code> table to select <code>employee_name</code>, <code>salary</code>, and their <code>department_name</code>.",
            "targetQuery": "SELECT e.employee_name, e.salary, d.department_name FROM employees e INNER JOIN departments d ON e.department_id = d.department_id",
            "initialCode": "SELECT e.employee_name, e.salary, d.department_name\\nFROM employees e\\nINNER JOIN departments d ON e.department_id = d.department_id;"
        },
        {
            "title": "Lab 2: Join Orders and Customers",
            "prompt": "Join the <code>orders</code> table with the <code>customers</code> table to select <code>order_id</code>, <code>order_amount</code>, and the matching <code>customer_name</code>.",
            "targetQuery": "SELECT o.order_id, o.order_amount, c.customer_name FROM orders o INNER JOIN customers c ON o.customer_id = c.customer_id",
            "initialCode": "SELECT o.order_id, o.order_amount, c.customer_name\\nFROM orders o\\nINNER JOIN customers c ON o.customer_id = c.customer_id;"
        },
        {
            "title": "Lab 3: Join and Filter",
            "prompt": "Select <code>employee_name</code> and <code>department_name</code> for all employees belonging to the 'Engineering' department. Use an INNER JOIN.",
            "targetQuery": "SELECT e.employee_name, d.department_name FROM employees e INNER JOIN departments d ON e.department_id = d.department_id WHERE d.department_name = 'Engineering'",
            "initialCode": "SELECT e.employee_name, d.department_name\\nFROM employees e\\nINNER JOIN departments d ON e.department_id = d.department_id\\nWHERE d.department_name = 'Engineering';"
        }
    ],
    "10-left-join": [
        {
            "title": "Lab 1: Count Employees in Departments",
            "prompt": "Find all departments and the count of employees assigned to them. Include departments with 0 employees. Display <code>department_name</code> and the count as <code>employee_count</code>.",
            "targetQuery": "SELECT d.department_name, COUNT(e.employee_id) as employee_count FROM departments d LEFT JOIN employees e ON d.department_id = e.department_id GROUP BY d.department_name",
            "initialCode": "SELECT d.department_name, COUNT(e.employee_id) as employee_count\\nFROM departments d\\nLEFT JOIN employees e ON d.department_id = e.department_id\\nGROUP BY d.department_name;"
        },
        {
            "title": "Lab 2: Customers and Total Orders",
            "prompt": "Show all customers and their total order amount. Include customers with no orders. Return <code>customer_name</code> and the sum as <code>total_ordered</code>. Group by customer name.",
            "targetQuery": "SELECT c.customer_name, SUM(o.order_amount) as total_ordered FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id GROUP BY c.customer_name",
            "initialCode": "SELECT c.customer_name, SUM(o.order_amount) as total_ordered\\nFROM customers c\\nLEFT JOIN orders o ON c.customer_id = o.customer_id\\nGROUP BY c.customer_name;"
        },
        {
            "title": "Lab 3: Employees and Managers (Self-Join)",
            "prompt": "For each employee, select their <code>employee_name</code> and the name of their manager as <code>manager_name</code>. Use a LEFT JOIN on the <code>employees</code> table with itself to ensure employees with no manager are not dropped.",
            "targetQuery": "SELECT emp.employee_name, mgr.employee_name as manager_name FROM employees emp LEFT JOIN employees mgr ON emp.manager_id = mgr.employee_id",
            "initialCode": "SELECT emp.employee_name, mgr.employee_name as manager_name\\nFROM employees emp\\nLEFT JOIN employees mgr ON emp.manager_id = mgr.employee_id;"
        }
    ],
    "11-missing-record-validation": [
        {
            "title": "Lab 1: Empty Departments",
            "prompt": "Find all departments that do not have any employees assigned to them. Select the <code>department_name</code> using a LEFT JOIN and checking for NULL.",
            "targetQuery": "SELECT d.department_name FROM departments d LEFT JOIN employees e ON d.department_id = e.department_id WHERE e.employee_id IS NULL",
            "initialCode": "SELECT d.department_name\\nFROM departments d\\nLEFT JOIN employees e ON d.department_id = e.department_id\\nWHERE e.employee_id IS NULL;"
        },
        {
            "title": "Lab 2: Customers with Zero Orders",
            "prompt": "Identify customers who have never placed any orders. Return the <code>customer_name</code> using a LEFT JOIN and checking for NULL.",
            "targetQuery": "SELECT c.customer_name FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id WHERE o.order_id IS NULL",
            "initialCode": "SELECT c.customer_name\\nFROM customers c\\nLEFT JOIN orders o ON c.customer_id = o.customer_id\\nWHERE o.order_id IS NULL;"
        },
        {
            "title": "Lab 3: Employees Who Aren't Managers",
            "prompt": "Find all employees who are not managing anyone. Return the manager's <code>employee_name</code> using a LEFT JOIN on manager_id and checking for NULL.",
            "targetQuery": "SELECT mgr.employee_name FROM employees mgr LEFT JOIN employees emp ON mgr.employee_id = emp.manager_id WHERE emp.employee_id IS NULL",
            "initialCode": "SELECT mgr.employee_name\\nFROM employees mgr\\nLEFT JOIN employees emp ON mgr.employee_id = emp.manager_id\\nWHERE emp.employee_id IS NULL;"
        }
    ],
    "4-exists-vs-not-exists": [
        {
            "title": "Lab 1: Find Active Departments",
            "prompt": "Find all departments that have at least one employee using the <code>EXISTS</code> clause. Return <code>department_name</code>.",
            "targetQuery": "SELECT d.department_name FROM departments d WHERE EXISTS (SELECT 1 FROM employees e WHERE e.department_id = d.department_id)",
            "initialCode": "SELECT d.department_name\\nFROM departments d\\nWHERE EXISTS (\\n  SELECT 1 FROM employees e WHERE e.department_id = d.department_id\\n);"
        },
        {
            "title": "Lab 2: Empty Departments using NOT EXISTS",
            "prompt": "Find all departments that do not have any employees using the <code>NOT EXISTS</code> clause. Return <code>department_name</code>.",
            "targetQuery": "SELECT d.department_name FROM departments d WHERE NOT EXISTS (SELECT 1 FROM employees e WHERE e.department_id = d.department_id)",
            "initialCode": "SELECT d.department_name\\nFROM departments d\\nWHERE NOT EXISTS (\\n  SELECT 1 FROM employees e WHERE e.department_id = d.department_id\\n);"
        },
        {
            "title": "Lab 3: Active Buyers using EXISTS",
            "prompt": "Find customers in the <code>customers</code> table who have placed at least one order using <code>EXISTS</code>. Return <code>customer_name</code>.",
            "targetQuery": "SELECT c.customer_name FROM customers c WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id)",
            "initialCode": "SELECT c.customer_name\\nFROM customers c\\nWHERE EXISTS (\\n  SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id\\n);"
        }
    ],
    "9-coalesce": [
        {
            "title": "Lab 1: Clean Manager IDs",
            "prompt": "Select <code>employee_name</code> and their <code>manager_id</code>. If <code>manager_id</code> is NULL, display <code>-1</code> instead. Alias the column as <code>manager_id_clean</code>.",
            "targetQuery": "SELECT employee_name, COALESCE(manager_id, -1) as manager_id_clean FROM employees",
            "initialCode": "SELECT employee_name, COALESCE(manager_id, -1) as manager_id_clean\\nFROM employees;"
        },
        {
            "title": "Lab 2: Default Regions",
            "prompt": "Select <code>customer_name</code> and their <code>region</code>. Default any NULL region to 'Unknown'. Alias the column as <code>region_clean</code>.",
            "targetQuery": "SELECT customer_name, COALESCE(region, 'Unknown') as region_clean FROM customers",
            "initialCode": "SELECT customer_name, COALESCE(region, 'Unknown') as region_clean\\nFROM customers;"
        },
        {
            "title": "Lab 3: Default Order Amounts",
            "prompt": "Select <code>order_id</code> and their <code>order_amount</code>. If the amount is NULL, default it to <code>0.0</code>. Alias the column as <code>amount_clean</code>.",
            "targetQuery": "SELECT order_id, COALESCE(order_amount, 0.0) as amount_clean FROM orders",
            "initialCode": "SELECT order_id, COALESCE(order_amount, 0.0) as amount_clean\\nFROM orders;"
        }
    ],
    "10-merge-upsert-thinking-conceptual": [
        {
            "title": "Lab 1: Identify New Source Records",
            "prompt": "Write a query to identify which <code>customer_id</code>s from the <code>source_customers</code> table are missing in the <code>target_customers</code> table and need to be inserted. Select their <code>customer_id</code>, <code>customer_name</code>, and <code>city</code>.",
            "targetQuery": "SELECT s.customer_id, s.customer_name, s.city FROM source_customers s LEFT JOIN target_customers t ON s.customer_id = t.customer_id WHERE t.customer_id IS NULL",
            "initialCode": "SELECT s.customer_id, s.customer_name, s.city\\nFROM source_customers s\\nLEFT JOIN target_customers t ON s.customer_id = t.customer_id\\nWHERE t.customer_id IS NULL;"
        },
        {
            "title": "Lab 2: Identify Updated Source Records",
            "prompt": "Write a query to find which <code>customer_id</code>s exist in both <code>source_customers</code> and <code>target_customers</code> but have different <code>city</code> values (meaning they require an update). Select <code>customer_id</code>, the new city as <code>source_city</code>, and the old city as <code>target_city</code>.",
            "targetQuery": "SELECT s.customer_id, s.city as source_city, t.city as target_city FROM source_customers s INNER JOIN target_customers t ON s.customer_id = t.customer_id WHERE s.city <> t.city",
            "initialCode": "SELECT s.customer_id, s.city as source_city, t.city as target_city\\nFROM source_customers s\\nINNER JOIN target_customers t ON s.customer_id = t.customer_id\\nWHERE s.city <> t.city;"
        },
        {
            "title": "Lab 3: Generate Unified Upsert State",
            "prompt": "Write a query to simulate the final UPSERT state. Select all records from <code>source_customers</code> (the newest state), plus records from <code>target_customers</code> that are NOT in <code>source_customers</code> (records that were not updated). Return <code>customer_id</code> and <code>city</code>, ordered by <code>customer_id</code>.",
            "targetQuery": "SELECT customer_id, city FROM source_customers UNION SELECT customer_id, city FROM target_customers WHERE customer_id NOT IN (SELECT customer_id FROM source_customers) ORDER BY customer_id",
            "initialCode": "SELECT customer_id, city FROM source_customers\\nUNION\\nSELECT customer_id, city FROM target_customers WHERE customer_id NOT IN (SELECT customer_id FROM source_customers)\\nORDER BY customer_id;"
        }
    ],
    "11-scd-slowly-changing-dimensions-basics": [
        {
            "title": "Lab 1: Identify SCD Type 1 Overwrites",
            "prompt": "Identify employees whose department changed between the target table (<code>scd1_target</code>) and the incoming source table (<code>scd1_source</code>). In SCD Type 1, these will be overwritten. Select <code>emp_id</code>, <code>old_dept</code> (from target), and <code>new_dept</code> (from source) where they differ.",
            "targetQuery": "SELECT s.emp_id, t.dept as old_dept, s.dept as new_dept FROM scd1_source s INNER JOIN scd1_target t ON s.emp_id = t.emp_id WHERE s.dept <> t.dept",
            "initialCode": "SELECT s.emp_id, t.dept as old_dept, s.dept as new_dept\\nFROM scd1_source s\\nINNER JOIN scd1_target t ON s.emp_id = t.emp_id\\nWHERE s.dept <> t.dept;"
        },
        {
            "title": "Lab 2: Fetch Current SCD Type 2 Records",
            "prompt": "For SCD Type 2 history tracking, write a query to fetch the current active department assignments from the historical table <code>scd2_target</code> (where <code>is_current</code> is 'Y'). Select <code>emp_id</code>, <code>emp_name</code>, and <code>dept</code>.",
            "targetQuery": "SELECT emp_id, emp_name, dept FROM scd2_target WHERE is_current = 'Y'",
            "initialCode": "SELECT emp_id, emp_name, dept\\nFROM scd2_target\\nWHERE is_current = 'Y';"
        },
        {
            "title": "Lab 3: Historical Date Range Lookup",
            "prompt": "Find which department employee 101 belonged to on '2026-03-01' using the validity range columns <code>valid_from</code> and <code>valid_to</code> in the <code>scd2_target</code> table. Select <code>emp_id</code>, <code>emp_name</code>, and <code>dept</code>.",
            "targetQuery": "SELECT emp_id, emp_name, dept FROM scd2_target WHERE emp_id = 101 AND '2026-03-01' BETWEEN valid_from AND valid_to",
            "initialCode": "SELECT emp_id, emp_name, dept\\nFROM scd2_target\\nWHERE emp_id = 101 AND '2026-03-01' BETWEEN valid_from AND valid_to;"
        }
    ],
    "12-delete-detection-logic": [
        {
            "title": "Lab 1: Detect Missing Source Records",
            "prompt": "Write a query to identify customer records in the target table (<code>delete_target</code>) that are missing from the source table (<code>delete_source</code>) using a LEFT JOIN. Select <code>cust_id</code> from the target table where the source ID is NULL.",
            "targetQuery": "SELECT t.cust_id FROM delete_target t LEFT JOIN delete_source s ON t.cust_id = s.cust_id WHERE s.cust_id IS NULL",
            "initialCode": "SELECT t.cust_id\\nFROM delete_target t\\nLEFT JOIN delete_source s ON t.cust_id = s.cust_id\\nWHERE s.cust_id IS NULL;"
        },
        {
            "title": "Lab 2: Find Active Target Records for Inactivation",
            "prompt": "Find target customers that are missing from the source table but are STILL marked as active (<code>active_flag = 'Y'</code>) in the target table. These are records that the ETL pipeline needs to mark inactive. Select their <code>cust_id</code>.",
            "targetQuery": "SELECT t.cust_id FROM delete_target t LEFT JOIN delete_source s ON t.cust_id = s.cust_id WHERE s.cust_id IS NULL AND t.active_flag = 'Y'",
            "initialCode": "SELECT t.cust_id\\nFROM delete_target t\\nLEFT JOIN delete_source s ON t.cust_id = s.cust_id\\nWHERE s.cust_id IS NULL AND t.active_flag = 'Y';"
        },
        {
            "title": "Lab 3: Alternative Delete Detection using NOT EXISTS",
            "prompt": "Write a query to perform the same delete detection using the <code>NOT EXISTS</code> clause instead of a LEFT JOIN. Select <code>cust_id</code> from the <code>delete_target</code> table where no match exists in the <code>delete_source</code> table.",
            "targetQuery": "SELECT t.cust_id FROM delete_target t WHERE NOT EXISTS (SELECT 1 FROM delete_source s WHERE s.cust_id = t.cust_id)",
            "initialCode": "SELECT t.cust_id\\nFROM delete_target t\\nWHERE NOT EXISTS (\\n  SELECT 1 FROM delete_source s WHERE s.cust_id = t.cust_id\\n);"
        }
    ],
    "13-audit-columns": [
        {
            "title": "Lab 1: Identify Unmodified Records",
            "prompt": "Select <code>customer_id</code> and <code>city</code> for all customers in the <code>audit_customers</code> table who have never been updated since insertion (meaning <code>updated_date</code> is NULL or equals <code>created_date</code>).",
            "targetQuery": "SELECT customer_id, city FROM audit_customers WHERE updated_date IS NULL OR updated_date = created_date",
            "initialCode": "SELECT customer_id, city\\nFROM audit_customers\\nWHERE updated_date IS NULL OR updated_date = created_date;"
        },
        {
            "title": "Lab 2: Detect Late Modifications",
            "prompt": "Write a query to select the <code>customer_id</code> and the number of days elapsed between creation and update as <code>days_elapsed</code> for customers whose profiles were modified at least 30 days after they were created. (Hint: Use <code>CAST(julianday(updated_date) - julianday(created_date) AS INTEGER)</code>).",
            "targetQuery": "SELECT customer_id, CAST(julianday(updated_date) - julianday(created_date) AS INTEGER) as days_elapsed FROM audit_customers WHERE updated_date IS NOT NULL AND julianday(updated_date) - julianday(created_date) >= 30",
            "initialCode": "SELECT customer_id, CAST(julianday(updated_date) - julianday(created_date) AS INTEGER) as days_elapsed\\nFROM audit_customers\\nWHERE updated_date IS NOT NULL AND julianday(updated_date) - julianday(created_date) >= 30;"
        },
        {
            "title": "Lab 3: Aggregate Daily Audit Counts",
            "prompt": "For the creation date '2026-06-01', count the total records created as <code>created_count</code> and the number of those records that have been updated since then (where <code>updated_date</code> is NOT NULL) as <code>updated_count</code> from the <code>audit_customers</code> table.",
            "targetQuery": "SELECT COUNT(*) as created_count, COUNT(updated_date) as updated_count FROM audit_customers WHERE created_date = '2026-06-01'",
            "initialCode": "SELECT COUNT(*) as created_count, COUNT(updated_date) as updated_count\\nFROM audit_customers\\nWHERE created_date = '2026-06-01';"
        }
    ]
}

# Seeding script to create and populate standard SQLite database
SEED_SQL = """
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name TEXT,
    city TEXT,
    region TEXT,
    status TEXT
);
INSERT INTO customers VALUES (1, 'Alice Smith', 'Mumbai', 'West', 'Active');
INSERT INTO customers VALUES (2, 'Bob Jones', 'Delhi', 'North', 'Active');
INSERT INTO customers VALUES (3, 'Charlie Brown', 'Bangalore', 'South', 'Inactive');
INSERT INTO customers VALUES (4, 'Diana Prince', 'Mumbai', 'West', 'Active');
INSERT INTO customers VALUES (5, 'Evan Wright', 'Kolkata', 'East', 'Active');
INSERT INTO customers VALUES (6, 'Frank Miller', 'Delhi', 'North', 'Inactive');
INSERT INTO customers VALUES (7, 'Grace Lee', 'Bangalore', 'South', 'Active');

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    order_date TEXT,
    order_amount REAL,
    update_time TEXT
);
INSERT INTO orders VALUES (101, 1, '2026-05-10', 1500.00, '2026-05-10 10:00:00');
INSERT INTO orders VALUES (102, 2, '2026-05-11', 2500.00, '2026-05-11 11:00:00');
INSERT INTO orders VALUES (103, 1, '2026-05-12', 3000.00, '2026-05-12 12:00:00');
INSERT INTO orders VALUES (104, 3, '2026-05-12', 500.00, '2026-05-12 09:00:00');
INSERT INTO orders VALUES (105, 4, '2026-05-13', 4500.00, '2026-05-13 14:00:00');
INSERT INTO orders VALUES (106, 2, '2026-05-14', 1200.00, '2026-05-14 15:00:00');
INSERT INTO orders VALUES (107, 1, '2026-05-12', 3000.00, '2026-05-12 12:05:00');
INSERT INTO orders VALUES (108, 5, '2026-05-15', 800.00, '2026-05-15 16:00:00');

CREATE TABLE employees (
    employee_id INTEGER PRIMARY KEY,
    employee_name TEXT,
    department_id INTEGER,
    salary INTEGER,
    manager_id INTEGER
);
INSERT INTO employees VALUES (1, 'Raj Patel', 10, 120000, NULL);
INSERT INTO employees VALUES (2, 'Vikram Singh', 10, 95000, 1);
INSERT INTO employees VALUES (3, 'Amit Sharma', 10, 80000, 1);
INSERT INTO employees VALUES (4, 'Priya Das', 20, 110000, NULL);
INSERT INTO employees VALUES (5, 'Rohan Mehta', 20, 90000, 4);
INSERT INTO employees VALUES (6, 'Neha Gupta', 30, 85000, NULL);
INSERT INTO employees VALUES (7, 'Sanjay Dutt', 30, 75000, 6);

CREATE TABLE departments (
    department_id INTEGER PRIMARY KEY,
    department_name TEXT
);
INSERT INTO departments VALUES (10, 'Engineering');
INSERT INTO departments VALUES (20, 'Sales');
INSERT INTO departments VALUES (30, 'Marketing');
INSERT INTO departments VALUES (40, 'HR');

CREATE TABLE sales (
    sale_id INTEGER PRIMARY KEY,
    region TEXT,
    sales_amount REAL,
    sale_date TEXT
);
INSERT INTO sales VALUES (1, 'North', 15000.00, '2026-05-01');
INSERT INTO sales VALUES (2, 'North', 12000.00, '2026-05-02');
INSERT INTO sales VALUES (3, 'South', 18000.00, '2026-05-01');
INSERT INTO sales VALUES (4, 'East', 9000.00, '2026-05-03');
INSERT INTO sales VALUES (5, 'West', 22000.00, '2026-05-02');
INSERT INTO sales VALUES (6, 'South', 14000.00, '2026-05-04');
INSERT INTO sales VALUES (7, 'West', 16000.00, '2026-05-05');

CREATE TABLE source_customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name TEXT,
    city TEXT,
    email TEXT
);
INSERT INTO source_customers VALUES (101, 'Alice Smith', 'Chennai', 'alice@gmail.com');
INSERT INTO source_customers VALUES (102, 'Bob Jones', 'Delhi', 'bob@gmail.com');
INSERT INTO source_customers VALUES (104, 'Diana Prince', 'Mumbai', 'diana@gmail.com');

CREATE TABLE target_customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name TEXT,
    city TEXT,
    email TEXT
);
INSERT INTO target_customers VALUES (101, 'Alice Smith', 'Pune', 'alice@gmail.com');
INSERT INTO target_customers VALUES (102, 'Bob Jones', 'Delhi', 'bob@gmail.com');
INSERT INTO target_customers VALUES (103, 'Charlie Brown', 'Bangalore', 'charlie@gmail.com');

CREATE TABLE scd1_source (
    emp_id INTEGER PRIMARY KEY,
    emp_name TEXT,
    dept TEXT
);
INSERT INTO scd1_source VALUES (1, 'Raj Patel', 'Engineering');
INSERT INTO scd1_source VALUES (2, 'Vikram Singh', 'Marketing');
INSERT INTO scd1_source VALUES (3, 'Amit Sharma', 'Engineering');

CREATE TABLE scd1_target (
    emp_id INTEGER PRIMARY KEY,
    emp_name TEXT,
    dept TEXT
);
INSERT INTO scd1_target VALUES (1, 'Raj Patel', 'Sales');
INSERT INTO scd1_target VALUES (2, 'Vikram Singh', 'Marketing');
INSERT INTO scd1_target VALUES (3, 'Amit Sharma', 'HR');

CREATE TABLE scd2_target (
    emp_id INTEGER,
    emp_name TEXT,
    dept TEXT,
    valid_from TEXT,
    valid_to TEXT,
    is_current TEXT
);
INSERT INTO scd2_target VALUES (101, 'Alice Smith', 'Marketing', '2026-01-01', '2026-02-28', 'N');
INSERT INTO scd2_target VALUES (101, 'Alice Smith', 'Engineering', '2026-03-01', '2026-05-15', 'N');
INSERT INTO scd2_target VALUES (101, 'Alice Smith', 'Sales', '2026-05-16', '9999-12-31', 'Y');
INSERT INTO scd2_target VALUES (102, 'Bob Jones', 'Sales', '2026-01-01', '9999-12-31', 'Y');

CREATE TABLE delete_source (
    cust_id INTEGER PRIMARY KEY
);
INSERT INTO delete_source VALUES (101);
INSERT INTO delete_source VALUES (102);
INSERT INTO delete_source VALUES (104);

CREATE TABLE delete_target (
    cust_id INTEGER PRIMARY KEY,
    active_flag TEXT
);
INSERT INTO delete_target VALUES (101, 'Y');
INSERT INTO delete_target VALUES (102, 'Y');
INSERT INTO delete_target VALUES (103, 'Y');
INSERT INTO delete_target VALUES (104, 'Y');

CREATE TABLE audit_customers (
    customer_id INTEGER PRIMARY KEY,
    city TEXT,
    created_date TEXT,
    updated_date TEXT
);
INSERT INTO audit_customers VALUES (101, 'Pune', '2026-06-01', NULL);
INSERT INTO audit_customers VALUES (102, 'Delhi', '2026-05-01', '2026-06-01');
INSERT INTO audit_customers VALUES (103, 'Bangalore', '2026-06-01', '2026-06-01');
INSERT INTO audit_customers VALUES (104, 'Mumbai', '2026-04-01', '2026-06-02');
"""

def clean_text(text):
    return text

def make_slug(title):
    slug = title.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug

def parse_inline(text):
    text = html.escape(text)
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`(.*?)`", r"<code>\1</code>", text)
    return text

def get_kid_friendly_revision_notes(topic_id):
    notes = {
        "1-basic-select-filtering": """
<div class="kid-theory-section">
    <p>Before SQL, let's use a real-life example.</p>
    
    <div class="theory-imagine-box">
        <strong>Imagine (Toy Box):</strong>
        <p>A toy box filled with toys:</p>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>toy_name</th><th>color</th><th>type</th></tr>
                </thead>
                <tbody>
                    <tr><td>Teddy Bear</td><td>Brown</td><td>Plush</td></tr>
                    <tr><td>Toy Car</td><td>Red</td><td>Vehicle</td></tr>
                    <tr><td>Lego Block</td><td>Red</td><td>Blocks</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="theory-ask-box">
        <strong>Business asks:</strong>
        <p>Which toys are RED?</p>
    </div>
    
    <div class="theory-block">
        <strong>SELECT + WHERE</strong>
        <p><strong>Think:</strong> "Look inside the toy box (<code>FROM toys</code>), check each toy to see if it is Red (<code>WHERE color = 'Red'</code>), and write down their names (<code>SELECT toy_name</code>)."</p>
    </div>
    
    <div class="code-container">
        <div class="code-header">
            <span class="code-lang">SQL</span>
        </div>
        <pre><code class="language-sql">SELECT toy_name
FROM toys
WHERE color = 'Red';</code></pre>
    </div>
    
    <div class="how-sql-thinks">
        <strong>How SQL Thinks:</strong>
        <ul>
            <li>For Teddy Bear: Color is Brown. Is it Red? <strong>NO</strong> → Discard.</li>
            <li>For Toy Car: Color is Red. Is it Red? <strong>YES</strong> → Keep.</li>
            <li>For Lego Block: Color is Red. Is it Red? <strong>YES</strong> → Keep.</li>
        </ul>
    </div>
    
    <div class="theory-output-box">
        <strong>Output:</strong>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>toy_name</th></tr>
                </thead>
                <tbody>
                    <tr><td>Toy Car</td></tr>
                    <tr><td>Lego Block</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="important-connection">
        <strong>💡 Important Connection:</strong>
        <p>The <code>WHERE</code> clause acts like a physical filter screen. It stops unwanted rows immediately so they don't consume memory in the next steps (like sorting or displaying).</p>
    </div>
    
    <div class="memory-trick">
        <strong>🔑 Easy Memory Trick:</strong>
        <ul>
            <li><strong>SELECT:</strong> Your Eyes 👀 (what columns to look at).</li>
            <li><strong>FROM:</strong> The Toy Chest 🗄️ (which table contains the records).</li>
            <li><strong>WHERE:</strong> The Gatekeeper 👮 (who gets inside).</li>
        </ul>
    </div>
    
    <div class="etl-de-why">
        <strong>🚀 Why Data Engineers Care:</strong>
        <p>In big data pipelines (e.g. Spark / Databricks), filtering early (called "Filter Pushdown") saves millions of gigabytes of network transfer by discarding unused records before they are shuffled across cloud servers.</p>
    </div>
</div>
""",
        "2-group-by-having": """
<div class="kid-theory-section">
    <p>Before SQL, let's use a real-life example.</p>
    
    <div class="theory-imagine-box">
        <strong>Imagine (Candies):</strong>
        <p>A bag of mixed candies:</p>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>candy_name</th><th>status</th></tr>
                </thead>
                <tbody>
                    <tr><td>Snickers</td><td>Fresh</td></tr>
                    <tr><td>KitKat</td><td>Fresh</td></tr>
                    <tr><td>Snickers</td><td>Fresh</td></tr>
                    <tr><td>Skittles</td><td>Expired</td></tr>
                    <tr><td>KitKat</td><td>Fresh</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="theory-ask-box">
        <strong>Business asks:</strong>
        <p>Which fresh candies do we have 2 or more of?</p>
    </div>
    
    <div class="theory-block">
        <strong>GROUP BY vs HAVING</strong>
        <p><strong>Think:</strong> "First, throw away expired candies (<code>WHERE</code>). Second, group identical candies into piles (<code>GROUP BY</code>). Third, count each pile and only keep piles with 2 or more candies (<code>HAVING</code>)."</p>
    </div>
    
    <div class="code-container">
        <div class="code-header">
            <span class="code-lang">SQL</span>
        </div>
        <pre><code class="language-sql">SELECT candy_name, COUNT(*) as qty
FROM candies
WHERE status = 'Fresh'
GROUP BY candy_name
HAVING COUNT(*) >= 2;</code></pre>
    </div>
    
    <div class="how-sql-thinks">
        <strong>How SQL Thinks:</strong>
        <ul>
            <li><strong>Filter (WHERE):</strong> Drop Skittles because it is expired. Remaining candies: Snickers, KitKat, Snickers, KitKat.</li>
            <li><strong>Group (GROUP BY):</strong> Put them in piles:
                <ul>
                    <li>Pile <strong>Snickers</strong>: 2 pieces.</li>
                    <li>Pile <strong>KitKat</strong>: 2 pieces.</li>
                </ul>
            </li>
            <li><strong>Filter Groups (HAVING):</strong> Check pile sizes:
                <ul>
                    <li>Snickers pile has 2 pieces (>= 2)? <strong>YES</strong> → Keep.</li>
                    <li>KitKat pile has 2 pieces (>= 2)? <strong>YES</strong> → Keep.</li>
                </ul>
            </li>
        </ul>
    </div>
    
    <div class="theory-output-box">
        <strong>Output:</strong>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>candy_name</th><th>qty</th></tr>
                </thead>
                <tbody>
                    <tr><td>Snickers</td><td>2</td></tr>
                    <tr><td>KitKat</td><td>2</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="important-connection">
        <strong>💡 Important Connection:</strong>
        <p>You cannot use <code>WHERE</code> to check the size of a group (like <code>WHERE COUNT(*) >= 2</code>) because the database doesn't know the group size until <em>after</em> the grouping is completed. That's why we use <code>HAVING</code>.</p>
    </div>
    
    <div class="memory-trick">
        <strong>🔑 Easy Memory Trick:</strong>
        <ul>
            <li><strong>WHERE:</strong> Filters individual candies <em>before</em> they are put into bowls.</li>
            <li><strong>GROUP BY:</strong> Groups them into bowls.</li>
            <li><strong>HAVING:</strong> Filters the bowls <em>after</em> checking their weights on a scale.</li>
        </ul>
    </div>
    
    <div class="etl-de-why">
        <strong>🚀 Why Data Engineers Care:</strong>
        <p>Putting row-level filters in <code>HAVING</code> (e.g. <code>HAVING status = 'Fresh'</code>) is a performance disaster. It forces the database to group records it should have discarded immediately in <code>WHERE</code>. Keep row filters in <code>WHERE</code>, aggregate filters in <code>HAVING</code>!</p>
    </div>
</div>
""",
        "3-duplicate-detection": """
<div class="kid-theory-section">
    <p>Before SQL, let's use a real-life example.</p>
    
    <div class="theory-imagine-box">
        <strong>Imagine (Logs):</strong>
        <p>An API log capturing customer logins, where API retries caused duplicate logs:</p>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>log_id</th><th>customer_id</th><th>login_time</th></tr>
                </thead>
                <tbody>
                    <tr><td>1</td><td>101</td><td>10:00:00</td></tr>
                    <tr><td>2</td><td>101</td><td>10:00:00</td></tr>
                    <tr><td>3</td><td>102</td><td>10:01:00</td></tr>
                    <tr><td>4</td><td>103</td><td>10:02:00</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="theory-ask-box">
        <strong>Business asks:</strong>
        <p>Which login records are duplicate (same customer and login time)?</p>
    </div>
    
    <div class="theory-block">
        <strong>Deduplication Pattern</strong>
        <p><strong>Think:</strong> "Group by customer_id and login_time. Count the matching records. If the count is greater than 1, we found our duplicates!"</p>
    </div>
    
    <div class="code-container">
        <div class="code-header">
            <span class="code-lang">SQL</span>
        </div>
        <pre><code class="language-sql">SELECT customer_id, login_time, COUNT(*) as occur
FROM login_logs
GROUP BY customer_id, login_time
HAVING COUNT(*) > 1;</code></pre>
    </div>
    
    <div class="how-sql-thinks">
        <strong>How SQL Thinks:</strong>
        <ul>
            <li>Group columns: <code>customer_id</code> and <code>login_time</code>:
                <ul>
                    <li>Pile <strong>(101, 10:00:00)</strong>: Contains log 1 & 2. Count = 2.</li>
                    <li>Pile <strong>(102, 10:01:00)</strong>: Contains log 3. Count = 1.</li>
                    <li>Pile <strong>(103, 10:02:00)</strong>: Contains log 4. Count = 1.</li>
                </ul>
            </li>
            <li>Filter groups having <code>occur > 1</code>:
                <ul>
                    <li>Pile (101, 10:00:00) has count 2 (> 1)? <strong>YES</strong> → Keep.</li>
                    <li>Pile (102, 10:01:00) has count 1 (> 1)? <strong>NO</strong> → Discard.</li>
                </ul>
            </li>
        </ul>
    </div>
    
    <div class="theory-output-box">
        <strong>Output:</strong>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>customer_id</th><th>login_time</th><th>occur</th></tr>
                </thead>
                <tbody>
                    <tr><td>101</td><td>10:00:00</td><td>2</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="important-connection">
        <strong>💡 Important Connection:</strong>
        <p>Duplicates are the main cause of reconciliation failures in ETL. They corrupt sales totals and inflate analytics. Tracking count occurrences per business key is the fundamental rule of data quality pipelines.</p>
    </div>
    
    <div class="memory-trick">
        <strong>🔑 Easy Memory Trick:</strong>
        <p><code>GROUP BY key columns + HAVING COUNT(*) > 1</code> is your <strong>Clone Alarm</strong>. Whenever the alarm count is > 1, you have identical clones in your system!</p>
    </div>
    
    <div class="etl-de-why">
        <strong>🚀 Why Data Engineers Care:</strong>
        <p>In standard data integration pipelines, duplicate detection is run inside staging layers to dump corrupted load records into a "Dead Letter Queue" (DLQ) so developers can debug API errors without stopping the ingestion pipeline.</p>
    </div>
</div>
""",
        "4-null-validation": """
<div class="kid-theory-section">
    <p>Before SQL, let's use a real-life example.</p>
    
    <div class="theory-imagine-box">
        <strong>Imagine (Phones):</strong>
        <p>A classroom list containing student names and their phone numbers. Some kids don't have a phone:</p>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>student_name</th><th>phone_number</th></tr>
                </thead>
                <tbody>
                    <tr><td>Alice</td><td>123-456</td></tr>
                    <tr><td>Bob</td><td>NULL</td></tr>
                    <tr><td>Charlie</td><td>NULL</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="theory-ask-box">
        <strong>Business asks:</strong>
        <p>Which students are missing their phone numbers?</p>
    </div>
    
    <div class="theory-block">
        <strong>The Ghost Operator (IS NULL)</strong>
        <p><strong>Think:</strong> "In databases, <code>NULL</code> represents a <strong>Ghost</strong> (missing/unknown). You can't ask <code>phone = NULL</code> because you cannot compare a phone to a ghost. You must ask <code>phone IS NULL</code>."</p>
    </div>
    
    <div class="code-container">
        <div class="code-header">
            <span class="code-lang">SQL</span>
        </div>
        <pre><code class="language-sql">SELECT student_name
FROM students
WHERE phone_number IS NULL;</code></pre>
    </div>
    
    <div class="how-sql-thinks">
        <strong>How SQL Thinks:</strong>
        <ul>
            <li>For Alice: phone_number is '123-456'. Is it a ghost? <strong>NO</strong> → Discard.</li>
            <li>For Bob: phone_number is NULL. Is it a ghost? <strong>YES</strong> → Keep.</li>
            <li>For Charlie: phone_number is NULL. Is it a ghost? <strong>YES</strong> → Keep.</li>
        </ul>
    </div>
    
    <div class="theory-output-box">
        <strong>Output:</strong>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>student_name</th></tr>
                </thead>
                <tbody>
                    <tr><td>Bob</td></tr>
                    <tr><td>Charlie</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="important-connection">
        <strong>💡 Important Connection:</strong>
        <p>If you write <code>WHERE phone = NULL</code>, SQL returns nothing (0 rows). This is because the database evaluates <code>AnyValue = NULL</code> as UNKNOWN, which evaluates to False. Always use <code>IS NULL</code> or <code>IS NOT NULL</code>.</p>
    </div>
    
    <div class="memory-trick">
        <strong>🔑 Easy Memory Trick:</strong>
        <p><strong>NULL is a Ghost</strong>. You cannot compare a real object to a ghost using equals (<code>=</code>). You must ask: "Is it haunted?" (<code>IS NULL</code>).</p>
    </div>
    
    <div class="etl-de-why">
        <strong>🚀 Why Data Engineers Care:</strong>
        <p>During ETL migrations, missing records or failed joins display as NULL. Counting NULL columns is the most common check in Data Quality frameworks (like Great Expectations) to detect broken upstream schemas.</p>
    </div>
</div>
""",
        "6-row-number": """
<div class="kid-theory-section">
    <p>Before SQL, let's use a real-life example.</p>
    
    <div class="theory-imagine-box">
        <strong>Imagine (Purchases):</strong>
        <p>A grocery store checkout line where customers get ticket numbers grouped by their customer group:</p>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>customer_id</th><th>purchase_time</th><th>amount</th></tr>
                </thead>
                <tbody>
                    <tr><td>101</td><td>09:00:00</td><td>$50</td></tr>
                    <tr><td>101</td><td>10:00:00</td><td>$120</td></tr>
                    <tr><td>102</td><td>09:30:00</td><td>$40</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="theory-ask-box">
        <strong>Business asks:</strong>
        <p>For each customer, number their purchases sequentially from first to last.</p>
    </div>
    
    <div class="theory-block">
        <strong>Windowing - ROW_NUMBER()</strong>
        <p><strong>Think:</strong> "Divide the table into groups for each customer (<code>PARTITION BY customer_id</code>). Inside each group, arrange purchases chronologically (<code>ORDER BY purchase_time ASC</code>). Assign ticket numbers (<code>ROW_NUMBER()</code>)."</p>
    </div>
    
    <div class="code-container">
        <div class="code-header">
            <span class="code-lang">SQL</span>
        </div>
        <pre><code class="language-sql">SELECT customer_id, purchase_time, amount,
       ROW_NUMBER() OVER (
           PARTITION BY customer_id
           ORDER BY purchase_time ASC
       ) as purchase_seq
FROM purchases;</code></pre>
    </div>
    
    <div class="how-sql-thinks">
        <strong>How SQL Thinks:</strong>
        <ul>
            <li><strong>Partition (Split):</strong> Group records by customer_id:
                <ul>
                    <li>Group <strong>101</strong>: Contains purchases at 09:00:00 and 10:00:00.</li>
                    <li>Group <strong>102</strong>: Contains purchase at 09:30:00.</li>
                </ul>
            </li>
            <li><strong>Order & Number:</strong> Number sequentially inside each group:
                <ul>
                    <li>Group 101:
                        <ul>
                            <li>09:00:00 purchase gets row number <strong>1</strong>.</li>
                            <li>10:00:00 purchase gets row number <strong>2</strong>.</li>
                        </ul>
                    </li>
                    <li>Group 102:
                        <ul>
                            <li>09:30:00 purchase gets row number <strong>1</strong>.</li>
                        </ul>
                    </li>
                </ul>
            </li>
        </ul>
    </div>
    
    <div class="theory-output-box">
        <strong>Output:</strong>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>customer_id</th><th>purchase_time</th><th>amount</th><th>purchase_seq</th></tr>
                </thead>
                <tbody>
                    <tr><td>101</td><td>09:00:00</td><td>$50</td><td>1</td></tr>
                    <tr><td>101</td><td>10:00:00</td><td>$120</td><td>2</td></tr>
                    <tr><td>102</td><td>09:30:00</td><td>$40</td><td>1</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="important-connection">
        <strong>💡 Important Connection:</strong>
        <p>Unlike <code>GROUP BY</code>, which squashes the rows together into a single summary row, window functions keep all rows alive. They just add a calculated ticket number to each row.</p>
    </div>
    
    <div class="memory-trick">
        <strong>🔑 Easy Memory Trick:</strong>
        <p><strong>ROW_NUMBER = Bouncer with a Ticket Roll</strong>. The bouncer divides people into separate lines (<code>PARTITION BY</code>), sorts them (<code>ORDER BY</code>), and hands out tickets (<code>1, 2, 3...</code>). No two rows share a ticket.</p>
    </div>
    
    <div class="etl-de-why">
        <strong>🚀 Why Data Engineers Care:</strong>
        <p>ROW_NUMBER() is the primary tool for deduplication in Incremental loads. If API calls resend records, we number duplicates by load time desc and filter for <code>rn = 1</code> to only write the latest record.</p>
    </div>
</div>
""",
        "7-rank-vs-dense-rank": """
<div class="kid-theory-section">
    <p>Before SQL, let's use a real-life example.</p>
    
    <div class="theory-imagine-box">
        <strong>Imagine (Race):</strong>
        <p>A school race where two kids cross the finish line at the exact same second:</p>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>runner_name</th><th>race_time</th></tr>
                </thead>
                <tbody>
                    <tr><td>Alice</td><td>10 seconds</td></tr>
                    <tr><td>Bob</td><td>12 seconds</td></tr>
                    <tr><td>Charlie</td><td>12 seconds</td></tr>
                    <tr><td>David</td><td>13 seconds</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="theory-ask-box">
        <strong>Business asks:</strong>
        <p>Assign rank positions to the runners. Show the differences between gap (RANK) and gapless (DENSE_RANK) positions.</p>
    </div>
    
    <div class="theory-block">
        <strong>Podium Gaps</strong>
        <p><strong>Think:</strong> "If runners tie, how do we rank the runner behind them? In <code>RANK()</code>, we skip numbers (e.g. 1st, 2nd, 2nd, 4th). In <code>DENSE_RANK()</code>, we keep them tight with no gaps (e.g. 1st, 2nd, 2nd, 3rd)."</p>
    </div>
    
    <div class="code-container">
        <div class="code-header">
            <span class="code-lang">SQL</span>
        </div>
        <pre><code class="language-sql">SELECT runner_name, race_time,
       RANK() OVER (ORDER BY race_time ASC) as rk,
       DENSE_RANK() OVER (ORDER BY race_time ASC) as drk
FROM race;</code></pre>
    </div>
    
    <div class="how-sql-thinks">
        <strong>How SQL Thinks:</strong>
        <ul>
            <li><strong>Alice (10s):</strong> The fastest. Gets <strong>RANK 1</strong> and <strong>DENSE_RANK 1</strong>.</li>
            <li><strong>Bob (12s) and Charlie (12s):</strong> A tie! Both get <strong>RANK 2</strong> and <strong>DENSE_RANK 2</strong>.</li>
            <li><strong>David (13s):</strong> The next runner:
                <ul>
                    <li><code>RANK()</code> counts total runners ahead (3). So David gets <strong>RANK 4</strong>. 3rd place is skipped!</li>
                    <li><code>DENSE_RANK()</code> counts unique ranks ahead (2). So David gets <strong>RANK 3</strong>. No podium numbers are skipped!</li>
                </ul>
            </li>
        </ul>
    </div>
    
    <div class="theory-output-box">
        <strong>Output:</strong>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>runner_name</th><th>race_time</th><th>rk</th><th>drk</th></tr>
                </thead>
                <tbody>
                    <tr><td>Alice</td><td>10s</td><td>1</td><td>1</td></tr>
                    <tr><td>Bob</td><td>12s</td><td>2</td><td>2</td></tr>
                    <tr><td>Charlie</td><td>12s</td><td>2</td><td>2</td></tr>
                    <tr><td>David</td><td>13s</td><td>4</td><td>3</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="important-connection">
        <strong>💡 Important Connection:</strong>
        <p>Never use <code>RANK()</code> for deduplicating data logs! If duplicates have identical timestamps, they both receive rank 1. Filtering for <code>WHERE rk = 1</code> will load BOTH duplicates, causing verification failures.</p>
    </div>
    
    <div class="memory-trick">
        <strong>🔑 Easy Memory Trick:</strong>
        <ul>
            <li><strong>RANK:</strong> Skips rankings on ties (Olympics: 1st, 2nd, 2nd, 4th).</li>
            <li><strong>DENSE_RANK:</strong> Densely packed ranks (No gaps: 1st, 2nd, 2nd, 3rd).</li>
        </ul>
    </div>
    
    <div class="etl-de-why">
        <strong>🚀 Why Data Engineers Care:</strong>
        <p>Top-N queries (e.g. "Find the top 3 highest revenue regions") require <code>DENSE_RANK</code> so that if multiple regions tie for second place, we don't skip the next region entirely from our report.</p>
    </div>
</div>
""",
        "8-latest-record-validation": """
<div class="kid-theory-section">
    <p>Before SQL, let's use a real-life example.</p>
    
    <div class="theory-imagine-box">
        <strong>Imagine (Profiles):</strong>
        <p>A profile audit log where users change their email addresses multiple times over the week:</p>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>user_id</th><th>email</th><th>update_time</th></tr>
                </thead>
                <tbody>
                    <tr><td>1</td><td>a@old.com</td><td>10:00:00</td></tr>
                    <tr><td>1</td><td>a@new.com</td><td>15:00:00</td></tr>
                    <tr><td>2</td><td>b@old.com</td><td>09:00:00</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="theory-ask-box">
        <strong>Business asks:</strong>
        <p>What is the CURRENT active email address for each user?</p>
    </div>
    
    <div class="theory-block">
        <strong>CDC Log Rewinding (rn = 1)</strong>
        <p><strong>Think:</strong> "For each user, sort updates from newest to oldest (<code>ORDER BY update_time DESC</code>) inside their group (<code>PARTITION BY user_id</code>). The row numbered <code>1</code> is their latest email."</p>
    </div>
    
    <div class="code-container">
        <div class="code-header">
            <span class="code-lang">SQL</span>
        </div>
        <pre><code class="language-sql">SELECT user_id, email, update_time
FROM (
    SELECT user_id, email, update_time,
           ROW_NUMBER() OVER (
               PARTITION BY user_id
               ORDER BY update_time DESC
           ) as rn
    FROM profile_updates
)
WHERE rn = 1;</code></pre>
    </div>
    
    <div class="how-sql-thinks">
        <strong>How SQL Thinks:</strong>
        <ul>
            <li><strong>Subquery Partitions:</strong> Group updates per user:
                <ul>
                    <li>User 1:
                        <ul>
                            <li>a@new.com (15:00) gets <code>rn = 1</code>.</li>
                            <li>a@old.com (10:00) gets <code>rn = 2</code>.</li>
                        </ul>
                    </li>
                    <li>User 2:
                        <ul>
                            <li>b@old.com (09:00) gets <code>rn = 1</code>.</li>
                        </ul>
                    </li>
                </ul>
            </li>
            <li><strong>Outer Query Filter:</strong> Filters for <code>rn = 1</code>:
                <ul>
                    <li>Keep User 1 (a@new.com) and User 2 (b@old.com).</li>
                </ul>
            </li>
        </ul>
    </div>
    
    <div class="theory-output-box">
        <strong>Output:</strong>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>user_id</th><th>email</th><th>update_time</th></tr>
                </thead>
                <tbody>
                    <tr><td>1</td><td>a@new.com</td><td>15:00:00</td></tr>
                    <tr><td>2</td><td>b@old.com</td><td>09:00:00</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="important-connection">
        <strong>💡 Important Connection:</strong>
        <p>Without an ordering sequence column (like a timestamp, version count, or incremental primary key), extracting the latest state is mathematically impossible. Always design audit logs with sequence markers!</p>
    </div>
    
    <div class="memory-trick">
        <strong>🔑 Easy Memory Trick:</strong>
        <p><strong>The CDC Rewind:</strong> Partition by ID + Order by Time DESC + Filter <code>rn = 1</code> is your magical timeline rewinder. It rewinds history and returns only the final frame.</p>
    </div>
    
    <div class="etl-de-why">
        <strong>🚀 Why Data Engineers Care:</strong>
        <p>This pattern is the core of Change Data Capture (CDC) logic. Systems like Debezium emit logs for every single insert/update. Before loading them to target tables (SCD Type 1), we apply this filter to write only the final state.</p>
    </div>
</div>
""",
        "9-inner-join": """
<div class="kid-theory-section">
    <p>Before SQL, let's use a real-life example.</p>
    
    <div class="theory-imagine-box">
        <strong>Imagine (Left Socks basket):</strong>
        <p>Left socks and Right socks inside separate baskets:</p>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>left_id</th><th>color</th></tr>
                </thead>
                <tbody>
                    <tr><td>1</td><td>Blue</td></tr>
                    <tr><td>2</td><td>Red</td></tr>
                    <tr><td>3</td><td>Green</td></tr>
                </tbody>
            </table>
        </div>
        <p>Right Socks basket:</p>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>right_id</th><th>color</th></tr>
                </thead>
                <tbody>
                    <tr><td>101</td><td>Blue</td></tr>
                    <tr><td>102</td><td>Red</td></tr>
                    <tr><td>103</td><td>Yellow</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="theory-ask-box">
        <strong>Business asks:</strong>
        <p>Match left and right socks to make pairs. What happens to unmatched socks?</p>
    </div>
    
    <div class="theory-block">
        <strong>The Sock Matcher (INNER JOIN)</strong>
        <p><strong>Think:</strong> "Only keep socks that find a matching color in both baskets. If a sock cannot be paired, discard it completely."</p>
    </div>
    
    <div class="code-container">
        <div class="code-header">
            <span class="code-lang">SQL</span>
        </div>
        <pre><code class="language-sql">SELECT l.color as left_sock, r.color as right_sock
FROM left_socks l
INNER JOIN right_socks r
ON l.color = r.color;</code></pre>
    </div>
    
    <div class="how-sql-thinks">
        <strong>How SQL Thinks:</strong>
        <ul>
            <li>Left Blue matches Right Blue? <strong>YES</strong> → Keep pair (Blue, Blue).</li>
            <li>Left Red matches Right Red? <strong>YES</strong> → Keep pair (Red, Red).</li>
            <li>Left Green matches Right Green? <strong>NO</strong> → Throw left Green away.</li>
            <li>Right Yellow matches Left Yellow? <strong>NO</strong> → Throw right Yellow away.</li>
        </ul>
    </div>
    
    <div class="theory-output-box">
        <strong>Output:</strong>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>left_sock</th><th>right_sock</th></tr>
                </thead>
                <tbody>
                    <tr><td>Blue</td><td>Blue</td></tr>
                    <tr><td>Red</td><td>Red</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="important-connection">
        <strong>💡 Important Connection:</strong>
        <p>An INNER JOIN matches like mathematical intersection ($A \\cap B$). If there are duplicates of a key in both baskets (e.g. 2 blue lefts and 2 blue rights), you get $2 \\times 2 = 4$ pairs! This multiplication is called a Join Explosion.</p>
    </div>
    
    <div class="memory-trick">
        <strong>🔑 Easy Memory Trick:</strong>
        <p><strong>Couples Only Club:</strong> INNER JOIN deletes unmatched items on both sides. If you don't have a matching partner on the key columns, you cannot enter the output table.</p>
    </div>
    
    <div class="etl-de-why">
        <strong>🚀 Why Data Engineers Care:</strong>
        <p>If your upstream dimension keys have typos or blank rows, an INNER JOIN will silently drop transaction records from your output tables! Always audit row count before and after joins to detect data loss.</p>
    </div>
</div>
""",
        "10-left-join": """
<div class="kid-theory-section">
    <p>Before SQL, let's use a real-life example.</p>
    
    <div class="theory-imagine-box">
        <strong>Imagine (Birthday Party):</strong>
        <p>A birthday party guest list (Left table) and gift bags (Right table):</p>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>guest_name</th></tr>
                </thead>
                <tbody>
                    <tr><td>Sam</td></tr>
                    <tr><td>Lea</td></tr>
                    <tr><td>Tom</td></tr>
                </tbody>
            </table>
        </div>
        <p>Gift Bags:</p>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>name</th><th>gift</th></tr>
                </thead>
                <tbody>
                    <tr><td>Sam</td><td>Toy Car</td></tr>
                    <tr><td>Lea</td><td>Book</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="theory-ask-box">
        <strong>Business asks:</strong>
        <p>Show every guest on the invitation list and what gift they received.</p>
    </div>
    
    <div class="theory-block">
        <strong>The Guest Shield (LEFT JOIN)</strong>
        <p><strong>Think:</strong> "Protect the guest list (Left table) at all costs. If a guest has no matching gift bag, let them stay, but their gift column is empty (NULL)."</p>
    </div>
    
    <div class="code-container">
        <div class="code-header">
            <span class="code-lang">SQL</span>
        </div>
        <pre><code class="language-sql">SELECT g.guest_name, b.gift
FROM guests g
LEFT JOIN gift_bags b
ON g.guest_name = b.name;</code></pre>
    </div>
    
    <div class="how-sql-thinks">
        <strong>How SQL Thinks:</strong>
        <ul>
            <li>Sam (Guest) matches Sam (Gift: Toy Car) → Output (Sam, Toy Car).</li>
            <li>Lea (Guest) matches Lea (Gift: Book) → Output (Lea, Book).</li>
            <li>Tom (Guest) has no matching gift bag → Protect Tom, set gift to **NULL**. Output (Tom, NULL).</li>
        </ul>
    </div>
    
    <div class="theory-output-box">
        <strong>Output:</strong>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>guest_name</th><th>gift</th></tr>
                </thead>
                <tbody>
                    <tr><td>Sam</td><td>Toy Car</td></tr>
                    <tr><td>Lea</td><td>Book</td></tr>
                    <tr><td>Tom</td><td><span class="null-val">NULL</span></td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="important-connection">
        <strong>💡 Important Connection:</strong>
        <p>Standard pattern in data warehousing: <code>fact_sales LEFT JOIN dim_products</code>. This guarantees that even if a product ID doesn't exist in our lookup table, the financial transaction is never dropped (it just shows NULL columns).</p>
    </div>
    
    <div class="memory-trick">
        <strong>🔑 Easy Memory Trick:</strong>
        <p><strong>The Safe Party:</strong> Left table is the guest list. Guests are protected. If they don't have matching details on the right, they get a ghost (NULL) instead of being kicked out.</p>
    </div>
    
    <div class="etl-de-why">
        <strong>🚀 Why Data Engineers Care:</strong>
        <p>LEFT JOIN is the default tool for enriching transaction data. It prevents data loss and highlights missing dimensions as NULLs, allowing engineers to debug source data issues easily.</p>
    </div>
</div>
""",
        "11-missing-record-validation": """
<div class="kid-theory-section">
    <p>Before SQL, let's use a real-life example.</p>
    
    <div class="theory-imagine-box">
        <strong>Imagine (Source vs Target):</strong>
        <p>A source list of files uploaded (Left table) vs files currently written to storage (Right table):</p>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>file_id</th></tr>
                </thead>
                <tbody>
                    <tr><td>101</td></tr>
                    <tr><td>102</td></tr>
                    <tr><td>103</td></tr>
                </tbody>
            </table>
        </div>
        <p>Storage files target:</p>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>file_id</th></tr>
                </thead>
                <tbody>
                    <tr><td>101</td></tr>
                    <tr><td>102</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="theory-ask-box">
        <strong>Business asks:</strong>
        <p>Identify files that failed to copy over to storage during migration.</p>
    </div>
    
    <div class="theory-block">
        <strong>The Orphan Finder (LEFT JOIN + IS NULL)</strong>
        <p><strong>Think:</strong> "Left join Source to Storage. If a file exists in Source but has no match in Storage, its Storage key will be NULL. Filter for those NULL keys!"</p>
    </div>
    
    <div class="code-container">
        <div class="code-header">
            <span class="code-lang">SQL</span>
        </div>
        <pre><code class="language-sql">SELECT s.file_id
FROM source s
LEFT JOIN storage t
ON s.file_id = t.file_id
WHERE t.file_id IS NULL;</code></pre>
    </div>
    
    <div class="how-sql-thinks">
        <strong>How SQL Thinks:</strong>
        <ul>
            <li>Source file 101 matches Storage file 101 → t.file_id = 101.</li>
            <li>Source file 102 matches Storage file 102 → t.file_id = 102.</li>
            <li>Source file 103 has no Storage match → t.file_id = NULL.</li>
            <li><strong>Filter (WHERE t.file_id IS NULL):</strong> Keep file 103 because its target key is NULL.</li>
        </ul>
    </div>
    
    <div class="theory-output-box">
        <strong>Output:</strong>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>file_id</th></tr>
                </thead>
                <tbody>
                    <tr><td>103</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="important-connection">
        <strong>💡 Important Connection:</strong>
        <p>This performs the same business logic as a <code>NOT EXISTS</code> filter. However, <code>LEFT JOIN</code> evaluates and builds all matching rows in memory first, which can slow down queries compared to EXISTS.</p>
    </div>
    
    <div class="memory-trick">
        <strong>🔑 Easy Memory Trick:</strong>
        <p><strong>LEFT JOIN + NULL Filter = The Orphan Finder</strong>. We list all children, look up their parents, and keep only children whose parent column is a blank ghost (NULL).</p>
    </div>
    
    <div class="etl-de-why">
        <strong>🚀 Why Data Engineers Care:</strong>
        <p>Missing record validation is the primary reconciliation check run after database migrations or CDC loads to ensure 100% data replication integrity.</p>
    </div>
</div>
""",
        "4-exists-vs-not-exists": """
<div class="kid-theory-section">
    <p>Before SQL, let's use a real-life example.</p>
    
    <div class="theory-imagine-box">
        <strong>Imagine (Customers & Orders):</strong>
        <p>Customers table:</p>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>customer_id</th></tr>
                </thead>
                <tbody>
                    <tr><td>101</td></tr>
                    <tr><td>102</td></tr>
                    <tr><td>103</td></tr>
                </tbody>
            </table>
        </div>
        <p>Orders table:</p>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>customer_id</th></tr>
                </thead>
                <tbody>
                    <tr><td>101</td></tr>
                    <tr><td>101</td></tr>
                    <tr><td>102</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="theory-ask-box">
        <strong>Business asks:</strong>
        <p>Which customers have placed at least one order?</p>
    </div>
    
    <div class="theory-block">
        <strong>EXISTS</strong>
        <p><strong>Think:</strong> "Does at least one matching record exist? If YES → keep row."</p>
    </div>
    
    <div class="code-container">
        <div class="code-header">
            <span class="code-lang">SQL</span>
        </div>
        <pre><code class="language-sql">SELECT *
FROM customers c
WHERE EXISTS (
    SELECT 1
    FROM orders o
    WHERE c.customer_id = o.customer_id
);</code></pre>
    </div>
    
    <div class="how-sql-thinks">
        <strong>How SQL Thinks:</strong>
        <ul>
            <li>For customer 101: Does order exist? <strong>YES</strong> → Keep 101.</li>
            <li>For customer 102: Does order exist? <strong>YES</strong> → Keep 102.</li>
            <li>For customer 103: Does order exist? <strong>NO</strong> → Discard 103.</li>
        </ul>
    </div>
    
    <div class="theory-output-box">
        <strong>Output:</strong>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>customer_id</th></tr>
                </thead>
                <tbody>
                    <tr><td>101</td></tr>
                    <tr><td>102</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <hr>
    
    <div class="theory-block">
        <strong>NOT EXISTS</strong>
        <p><strong>Think:</strong> "No matching record should exist. Keep rows that have no match."</p>
    </div>
    
    <div class="code-container">
        <div class="code-header">
            <span class="code-lang">SQL</span>
        </div>
        <pre><code class="language-sql">SELECT *
FROM customers c
WHERE NOT EXISTS (
    SELECT 1
    FROM orders o
    WHERE c.customer_id = o.customer_id
);</code></pre>
    </div>
    
    <div class="how-sql-thinks">
        <strong>SQL Thinking:</strong>
        <ul>
            <li>For 101: Order exists → Reject.</li>
            <li>For 102: Order exists → Reject.</li>
            <li>For 103: No order exists → Keep 103.</li>
        </ul>
    </div>
    
    <div class="theory-output-box">
        <strong>Output:</strong>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>customer_id</th></tr>
                </thead>
                <tbody>
                    <tr><td>103</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="important-connection">
        <strong>💡 Important Connection:</strong>
        <p>You already know this pattern:</p>
        <pre><code class="language-sql">SELECT c.customer_id
FROM customers c
LEFT JOIN orders o
ON c.customer_id = o.customer_id
WHERE o.customer_id IS NULL;</code></pre>
        <p>This also returns customer_id <code>103</code>. Both solve the same business problem but use different SQL styles.</p>
    </div>
    
    <div class="memory-trick">
        <strong>🔑 Easy Memory Trick:</strong>
        <ul>
            <li><strong>LEFT JOIN + NULL:</strong> Find records missing in target (Dumps and filters).</li>
            <li><strong>NOT EXISTS:</strong> Find records that have no match (Alert scanner).</li>
        </ul>
    </div>
    
    <div class="etl-de-why">
        <strong>🚀 Why Data Engineers Use EXISTS:</strong>
        <p>Suppose customer 101 has 1,000,000 orders. <code>EXISTS</code> stops checking after finding the first matching order. It doesn't care if there are 999,999 more! That is why <code>EXISTS</code> is incredibly fast and commonly used for incremental loads, reconciliation checks, duplicate prevention, and validation rules.</p>
    </div>
</div>
""",
        "9-coalesce": """
<div class="kid-theory-section">
    <p>Before SQL, let's use a real-life example.</p>
    
    <div class="theory-imagine-box">
        <strong>Imagine (Contacts):</strong>
        <p>A contact list where kids list their Home Phone, Mobile, or Parent's Phone. Some numbers are missing (NULL):</p>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>student_name</th><th>home_phone</th><th>mobile</th><th>parent_phone</th></tr>
                </thead>
                <tbody>
                    <tr><td>Alice</td><td>555-001</td><td>NULL</td><td>555-999</td></tr>
                    <tr><td>Bob</td><td>NULL</td><td>555-002</td><td>NULL</td></tr>
                    <tr><td>Charlie</td><td>NULL</td><td>NULL</td><td>NULL</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="theory-ask-box">
        <strong>Business asks:</strong>
        <p>Extract the primary contact method for each student. If no phone exists, default to 'No Phone'.</p>
    </div>
    
    <div class="theory-block">
        <strong>The Fallback Chain (COALESCE)</strong>
        <p><strong>Think:</strong> "Scan columns from left to right and return the first value that is NOT a ghost (NULL). If they are all ghosts, return the fallback text."</p>
    </div>
    
    <div class="code-container">
        <div class="code-header">
            <span class="code-lang">SQL</span>
        </div>
        <pre><code class="language-sql">SELECT student_name,
       COALESCE(home_phone, mobile, parent_phone, 'No Phone') as primary_phone
FROM student_contacts;</code></pre>
    </div>
    
    <div class="how-sql-thinks">
        <strong>How SQL Thinks:</strong>
        <ul>
            <li><strong>For Alice:</strong> Check <code>home_phone</code>: '555-001' (Real!) → Stop scanning. Return <strong>'555-001'</strong>.</li>
            <li><strong>For Bob:</strong> Check <code>home_phone</code>: NULL (Ghost) → Scan next. Check <code>mobile</code>: '555-002' (Real!) → Stop scanning. Return <strong>'555-002'</strong>.</li>
            <li><strong>For Charlie:</strong> Check <code>home_phone</code>: NULL (Ghost) → Scan next. Check <code>mobile</code>: NULL (Ghost) → Scan next. Check <code>parent_phone</code>: NULL (Ghost) → Scan next. Check final text: 'No Phone' (Real!) → Return <strong>'No Phone'</strong>.</li>
        </ul>
    </div>
    
    <div class="theory-output-box">
        <strong>Output:</strong>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>student_name</th><th>primary_phone</th></tr>
                </thead>
                <tbody>
                    <tr><td>Alice</td><td>555-001</td></tr>
                    <tr><td>Bob</td><td>555-002</td></tr>
                    <tr><td>Charlie</td><td>No Phone</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="important-connection">
        <strong>💡 Important Connection:</strong>
        <p>Remember that doing math with NULL makes the whole result NULL! E.g. <code>salary + bonus</code> is NULL if bonus is NULL. Use <code>COALESCE(salary, 0) + COALESCE(bonus, 0)</code> to safely add them.</p>
    </div>
    
    <div class="memory-trick">
        <strong>🔑 Easy Memory Trick:</strong>
        <p><strong>The Backup Team:</strong> COALESCE is your phone tree. You try to call home, then mobile, then parent. First one that answers gets picked!</p>
    </div>
    
    <div class="etl-de-why">
        <strong>🚀 Why Data Engineers Care:</strong>
        <p>Essential when cleaning raw ingest data in Silver lakehouse layers. We replace NULL values in keys, regions, or amounts with standard defaults (e.g. -1, 'Unknown', 0.0) to ensure analytics queries don't break.</p>
    </div>
</div>
""",
        "10-merge-upsert-thinking-conceptual": """
<div class="kid-theory-section">
    <p>Before SQL, let's use a real-life example.</p>
    
    <div class="theory-imagine-box">
        <strong>Imagine (The Stencil & Drawing):</strong>
        <p>You have a drawing board (Target) and a new set of shapes (Source):</p>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>shape_id</th><th>color</th></tr>
                </thead>
                <tbody>
                    <tr><td>Circle</td><td>Red (already drawn)</td></tr>
                    <tr><td>Square</td><td>Blue (already drawn)</td></tr>
                </tbody>
            </table>
        </div>
        <p>New incoming sheet (Source):</p>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>shape_id</th><th>color</th></tr>
                </thead>
                <tbody>
                    <tr><td>Circle</td><td>Yellow (update color!)</td></tr>
                    <tr><td>Triangle</td><td>Green (new shape!)</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="theory-ask-box">
        <strong>Business asks:</strong>
        <p>Synchronize the drawing board with the new sheet. How do we apply the changes?</p>
    </div>
    
    <div class="theory-block">
        <strong>MERGE / UPSERT</strong>
        <p><strong>Think:</strong> "If a shape already exists on our board, paint over it with the new color (<code>UPDATE</code>). If it doesn't exist, draw it from scratch (<code>INSERT</code>). That is <strong>UP</strong>date + in<strong>SERT</strong> = <strong>UPSERT</strong>."</p>
    </div>
    
    <div class="code-container">
        <div class="code-header">
            <span class="code-lang">CONCEPTUAL SQL (MERGE)</span>
        </div>
        <pre><code class="language-sql">MERGE INTO target_table t
USING source_table s
ON t.id = s.id
WHEN MATCHED THEN
    UPDATE SET t.color = s.color
WHEN NOT MATCHED THEN
    INSERT (id, color) VALUES (s.id, s.color);</code></pre>
    </div>
    
    <div class="how-sql-thinks">
        <strong>How SQL Thinks:</strong>
        <ul>
            <li>Check <strong>Circle</strong>: Exists in Target? <strong>YES</strong> (Matched) → Update color from Red to Yellow.</li>
            <li>Check <strong>Square</strong>: Exists in Source? <strong>NO</strong> (No incoming changes) → Keep as is (Blue).</li>
            <li>Check <strong>Triangle</strong>: Exists in Target? <strong>NO</strong> (Not matched) → Insert new shape (Triangle, Green).</li>
        </ul>
    </div>
    
    <div class="theory-output-box">
        <strong>Output Target Table:</strong>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>shape_id</th><th>color</th></tr>
                </thead>
                <tbody>
                    <tr><td>Circle</td><td>Yellow</td></tr>
                    <tr><td>Square</td><td>Blue</td></tr>
                    <tr><td>Triangle</td><td>Green</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="important-connection">
        <strong>💡 Important Connection:</strong>
        <p>In standard data warehouses like Delta Lake (Databricks) or Snowflake, running a raw <code>INSERT</code> every day causes duplicate records. A <code>MERGE</code> statement ensures we maintain a single, clean version of truth by comparing key columns.</p>
    </div>
    
    <div class="memory-trick">
        <strong>🔑 Easy Memory Trick:</strong>
        <p><strong>The Smart Clipboard:</strong> Think of a contact list on your phone. If you add a friend who is already there, you edit their profile (UPDATE). If they are new, you create a new contact card (INSERT). That's UPSERT!</p>
    </div>
    
    <div class="etl-de-why">
        <strong>🚀 Why Data Engineers Care:</strong>
        <p>Merge operations are the backbone of incremental load pipelines. Instead of reading and rewriting billions of rows every hour, we only process the tiny stream of updates and merge them in, saving massive cloud compute bills.</p>
    </div>
</div>
""",
        "11-scd-slowly-changing-dimensions-basics": """
<div class="kid-theory-section">
    <p>Slowly Changing Dimensions (SCD) define how we handle changes to master lists (like a customer's city or an employee's department) over time.</p>
    
    <div class="theory-imagine-box">
        <strong>Imagine (Customer moves city):</strong>
        <p>Customer 101 moves from Mumbai to Pune.</p>
        <p><strong>Before:</strong> 101 | Mumbai</p>
        <p><strong>After source update:</strong> 101 | Pune</p>
    </div>
    
    <div class="theory-block">
        <strong>SCD Type 1: Overwrite (No History)</strong>
        <p><strong>Think:</strong> "Erase the old value and write the new one in its place. The history is gone forever."</p>
        <p><strong>Target becomes:</strong> 101 | Pune (Mumbai is lost!)</p>
    </div>

    <div class="theory-block">
        <strong>SCD Type 2: Add New Row (Full History Tracking)</strong>
        <p><strong>Think:</strong> "Keep the old row, mark it as historical, and insert a brand new row with the current value and validity dates."</p>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>cust_id</th><th>city</th><th>valid_from</th><th>valid_to</th><th>is_current</th></tr>
                </thead>
                <tbody>
                    <tr><td>101</td><td>Mumbai</td><td>2026-01-01</td><td>2026-05-31</td><td>N</td></tr>
                    <tr><td>101</td><td>Pune</td><td>2026-06-01</td><td>9999-12-31</td><td>Y</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="how-sql-thinks">
        <strong>Comparing SCD 1 vs SCD 2:</strong>
        <ul>
            <li><strong>SCD Type 1:</strong> Very simple. Uses less storage. Good when we don't care about the past (e.g. fixing a typo in a name).</li>
            <li><strong>SCD Type 2:</strong> Keeps history. Essential for business reports. If Alice bought products in January (when she lived in Mumbai) and in June (living in Pune), we can attribute sales to the correct city at the time of purchase.</li>
        </ul>
    </div>
    
    <div class="important-connection">
        <strong>💡 Important Connection:</strong>
        <p>SCD Type 2 uses date ranges (<code>valid_from</code> and <code>valid_to</code>) so that we can run point-in-time lookups (e.g., <code>WHERE '2026-03-15' BETWEEN valid_from AND valid_to</code>) to see what the state of data was at any exact second in the past.</p>
    </div>
    
    <div class="memory-trick">
        <strong>🔑 Easy Memory Trick:</strong>
        <ul>
            <li><strong>SCD Type 1 (The Whiteboard):</strong> Erase the old name, write the new name. No trace of the past.</li>
            <li><strong>SCD Type 2 (The Photo Album):</strong> Don't throw away your old baby photos when you grow up. Keep them and add a new photo with the new date!</li>
        </ul>
    </div>
    
    <div class="etl-de-why">
        <strong>🚀 Why Data Engineers Care:</strong>
        <p>Data warehousing relies on historical analysis. If you run SCD Type 1 on a customer's location, all past order reports will show their current city, distorting historical regional sales analytics. Type 2 is a MUST for accurate business intelligence.</p>
    </div>
</div>
""",
        "12-delete-detection-logic": """
<div class="kid-theory-section">
    <p>Before SQL, let's use a real-life example.</p>
    
    <div class="theory-imagine-box">
        <strong>Imagine (The Missing Roll Call):</strong>
        <p>Yesterday, the source list had 3 kids. Today, it has 2. Kid 103 disappeared:</p>
        <p><strong>Yesterday Source:</strong> 101, 102, 103</p>
        <p><strong>Today Source:</strong> 101, 102</p>
        <p><strong>Our Target DB (currently has):</strong> 101, 102, 103</p>
    </div>
    
    <div class="theory-ask-box">
        <strong>Business asks:</strong>
        <p>Identify which records were deleted from the source so we can update our target database.</p>
    </div>
    
    <div class="theory-block">
        <strong>Delete Detection Pattern</strong>
        <p><strong>Think:</strong> "If a record exists in our Target but is missing in the incoming Source, it has been deleted. We perform a Target LEFT JOIN Source and keep rows where Source columns are NULL."</p>
    </div>
    
    <div class="code-container">
        <div class="code-header">
            <span class="code-lang">SQL</span>
        </div>
        <pre><code class="language-sql">SELECT t.customer_id
FROM target_table t
LEFT JOIN source_table s
ON t.customer_id = s.customer_id
WHERE s.customer_id IS NULL;</code></pre>
    </div>
    
    <div class="how-sql-thinks">
        <strong>How SQL Thinks:</strong>
        <ul>
            <li>Match Target 101 with Source 101 → Found! (Keep in source list)</li>
            <li>Match Target 102 with Source 102 → Found! (Keep in source list)</li>
            <li>Match Target 103 with Source 103 → <strong>NULL</strong>! (Missing from source)</li>
            <li><strong>Filter (WHERE s.customer_id IS NULL):</strong> Keep 103. This is our deleted record!</li>
        </ul>
    </div>
    
    <div class="important-connection">
        <strong>💡 Important Connection:</strong>
        <p>In production, databases rarely use physical <code>DELETE FROM</code> queries because they erase history. Instead, they run an <code>UPDATE</code> to set a column like <code>active_flag = 'N'</code> or <code>is_deleted = 1</code>. This is called a <strong>Soft Delete</strong>.</p>
    </div>
    
    <div class="memory-trick">
        <strong>🔑 Easy Memory Trick:</strong>
        <ul>
            <li><strong>New Records (Insert):</strong> Source LEFT JOIN Target WHERE Target IS NULL (Source has it, Target doesn't).</li>
            <li><strong>Deleted Records (Delete):</strong> Target LEFT JOIN Source WHERE Source IS NULL (Target has it, Source doesn't).</li>
        </ul>
    </div>
    
    <div class="etl-de-why">
        <strong>🚀 Why Data Engineers Care:</strong>
        <p>A data engineer reports *what the data shows*, not what they assume happened. If a record is missing from the source, we say: 'Record exists in target but is missing from source.' This could mean a delete happened, or it could mean the source extract job failed and missed a record. We report, then investigate!</p>
    </div>
</div>
""",
        "13-audit-columns": """
<div class="kid-theory-section">
    <p>Audit columns are system metadata columns added to every database table to track when records were created and updated. They do not store business values; they store trace history.</p>
    
    <div class="theory-imagine-box">
        <strong>Imagine (Record Birth & Changes):</strong>
        <p>A new customer record is born on June 1st:</p>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>customer_id</th><th>city</th><th>created_date</th><th>updated_date</th></tr>
                </thead>
                <tbody>
                    <tr><td>101</td><td>Pune</td><td>2026-06-01</td><td>NULL (or same as created)</td></tr>
                </tbody>
            </table>
        </div>
        <p>The customer updates their city to Chennai on June 2nd:</p>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>customer_id</th><th>city</th><th>created_date</th><th>updated_date</th></tr>
                </thead>
                <tbody>
                    <tr><td>101</td><td>Chennai</td><td>2026-06-01</td><td>2026-06-02</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="theory-block">
        <strong>Audit Columns Rules</strong>
        <ul>
            <li><code>created_date</code>: Set on the initial insert and **NEVER** changes. It represents the birth date of the record.</li>
            <li><code>updated_date</code>: Set to the current timestamp on every modification. It shows the last time the record was edited.</li>
        </ul>
    </div>
    
    <div class="how-sql-thinks">
        <strong>Real Interview Question:</strong>
        <p><em>"If a customer was created on Jan 1 and updated on Mar 1, what should happen to created_date after the update?"</em></p>
        <p><strong>Answer:</strong> Nothing! <code>created_date</code> remains Jan 1. Only <code>updated_date</code> changes to Mar 1.</p>
    </div>
    
    <div class="important-connection">
        <strong>💡 Important Connection:</strong>
        <p>Audit columns like <code>updated_date</code> are critical for **Incremental Loading**. Instead of reading all 100 million rows, the ETL pipeline queries: <code>WHERE updated_date >= yesterday</code> to only load the changed rows.</p>
    </div>
    
    <div class="memory-trick">
        <strong>🔑 Easy Memory Trick:</strong>
        <ul>
            <li><strong>created_date = Birth Certificate:</strong> Issued once when you are born. Never changes.</li>
            <li><strong>updated_date = Passport Stamps:</strong> Stamped every time you travel. Changes with every action.</li>
        </ul>
    </div>
    
    <div class="etl-de-why">
        <strong>🚀 Why Data Engineers Care:</strong>
        <p>Without audit columns, debugging pipeline failures is a nightmare. Audit columns tell us exactly when a row was modified, which ETL batch created it, and what pipeline run updated it, making data lineage and troubleshooting simple.</p>
    </div>
</div>
"""
    }
    return notes.get(topic_id, None)

def convert_markdown_to_html(lines):
    html_parts = []
    i = 0
    n = len(lines)
    
    while i < n:
        line = lines[i].rstrip()
        
        if not line.strip():
            i += 1
            continue
            
        # Code blocks
        if line.strip().startswith("```"):
            code_lines = []
            lang_match = re.match(r"^```(\w*)", line.strip())
            lang = lang_match.group(1) if lang_match else "sql"
            if not lang:
                lang = "sql"
            i += 1
            while i < n and not lines[i].rstrip().strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            if i < n:
                i += 1
            code_content = "".join(code_lines)
            code_content = html.escape(code_content)
            
            html_parts.append(f'''
<div class="code-container">
    <div class="code-header">
        <span class="code-lang">{lang.upper()}</span>
        <button class="copy-btn" onclick="copyCode(this)">
            <svg class="copy-icon" viewBox="0 0 24 24"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>
            <span>Copy</span>
        </button>
    </div>
    <pre><code class="language-{lang}">{code_content}</code></pre>
</div>
''')
            continue
            
        # Horizontal Rules
        if line.strip() == "---" or line.strip() == "___" or line.strip() == "***":
            html_parts.append("<hr>")
            i += 1
            continue
            
        # Headings (H2, H3)
        if line.startswith("### "):
            title = line[4:].strip()
            html_parts.append(f"<h3>{parse_inline(title)}</h3>")
            i += 1
            continue
        if line.startswith("## "):
            title = line[3:].strip()
            html_parts.append(f"<h2>{parse_inline(title)}</h2>")
            i += 1
            continue
            
        # Tables
        if line.strip().startswith("|"):
            table_lines = []
            while i < n and lines[i].rstrip().strip().startswith("|"):
                table_lines.append(lines[i].rstrip().strip())
                i += 1
            
            if table_lines:
                table_html = ["<div class='table-responsive'><table>"]
                for row_idx, tl in enumerate(table_lines):
                    if re.match(r"^\|?\s*(:?-+:?\s*\|)+\s*(:?-+:?\s*)?$", tl):
                        continue
                    
                    cells = [c.strip() for c in tl.split("|")]
                    if tl.startswith("|"):
                        cells = cells[1:]
                    if tl.endswith("|"):
                        cells = cells[:-1]
                        
                    row_cells = []
                    cell_tag = "th" if row_idx == 0 else "td"
                    for cell in cells:
                        row_cells.append(f"<{cell_tag}>{parse_inline(cell)}</{cell_tag}>")
                    
                    table_html.append(f"<tr>{''.join(row_cells)}</tr>")
                table_html.append("</table></div>")
                html_parts.append("\n".join(table_html))
            continue
            
        # Lists
        if line.strip().startswith("* ") or line.strip().startswith("- "):
            list_lines = []
            while i < n and (lines[i].rstrip().strip().startswith("* ") or lines[i].rstrip().strip().startswith("- ")):
                item_text = lines[i].rstrip().strip()
                if item_text.startswith("* "):
                    item_text = item_text[2:]
                elif item_text.startswith("- "):
                    item_text = item_text[2:]
                list_lines.append(item_text)
                i += 1
            
            list_html = ["<ul>"]
            for item in list_lines:
                list_html.append(f"<li>{parse_inline(item)}</li>")
            list_html.append("</ul>")
            html_parts.append("\n".join(list_html))
            continue
            
        # Paragraphs
        paragraph_lines = []
        while i < n and lines[i].rstrip().strip() and not any(
            lines[i].rstrip().strip().startswith(prefix) for prefix in ["#", "* ", "- ", "```", "|", "---"]
        ):
            paragraph_lines.append(lines[i].rstrip().strip())
            i += 1
            
        if paragraph_lines:
            p_text = " ".join(paragraph_lines)
            html_parts.append(f"<p>{parse_inline(p_text)}</p>")
        else:
            i += 1
            
    return "\n".join(html_parts)

def parse_file(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Source file not found at: {filepath}")
        
    with open(filepath, "r", encoding="windows-1252", errors="replace") as f:
        lines = f.readlines()
        
    categories = []
    current_category = None
    current_topic = None
    topic_lines = []
    
    for raw_line in lines:
        line = raw_line.rstrip()
        clean_ln = clean_text(line)
        
        if clean_ln.startswith("# "):
            title = clean_ln[2:].strip()
            
            is_cat = False
            title_upper = title.upper()
            for cat_keyword in CATEGORIES:
                if cat_keyword in title_upper:
                    is_cat = True
                    break
                    
            if is_cat:
                if current_topic and topic_lines:
                    current_topic["content_html"] = convert_markdown_to_html(topic_lines)
                    topic_lines = []
                    
                current_category = {
                    "title": title,
                    "id": make_slug(title),
                    "topics": []
                }
                categories.append(current_category)
                current_topic = None
            else:
                if current_topic and topic_lines:
                    current_topic["content_html"] = convert_markdown_to_html(topic_lines)
                    topic_lines = []
                    
                if current_category is None:
                    current_category = {
                        "title": "SQL Practice Tracker",
                        "id": "sql-practice-tracker",
                        "topics": []
                    }
                    categories.append(current_category)
                    
                current_topic = {
                    "title": title,
                    "id": make_slug(title),
                    "content_html": ""
                }
                current_category["topics"].append(current_topic)
        else:
            if current_topic is None:
                if current_category is None:
                    current_category = {
                        "title": "Introduction",
                        "id": "introduction",
                        "topics": []
                    }
                    categories.append(current_category)
                
                if clean_ln.strip():
                    current_topic = {
                        "title": "Welcome",
                        "id": "welcome",
                        "content_html": ""
                    }
                    current_category["topics"].append(current_topic)
                    topic_lines.append(clean_ln)
            else:
                topic_lines.append(clean_ln)
                
    if current_topic and topic_lines:
        current_topic["content_html"] = convert_markdown_to_html(topic_lines)
        
    return categories

def build_html(categories):
    # Programmatically override the initialCode in CHALLENGES to be empty templates
    for topic_id, labs in CHALLENGES.items():
        for lab in labs:
            lab["initialCode"] = "-- Write your SQL query here\\n"
            
    sidebar_html = []
    content_html = []
    total_topics = 0
    
    for cat in categories:
        cat_title = cat["title"]
        cat_id = cat["id"]
        topics = cat["topics"]
        
        if not topics:
            continue
            
        sidebar_html.append(f'''
        <div class="nav-group" id="group-{cat_id}">
            <div class="nav-group-header" onclick="toggleGroup('{cat_id}')">
                <span>{cat_title}</span>
            </div>
            <ul class="nav-group-list">
        ''')
        
        for topic in topics:
            total_topics += 1
            topic_title = topic["title"]
            topic_id = topic["id"]
            
            has_ch = topic_id in CHALLENGES
            badge = ' <span class="nav-badge">Playground</span>' if has_ch else ''
            
            sidebar_html.append(f'''
                <li>
                    <a href="#{topic_id}" class="nav-item" id="nav-link-{topic_id}" onclick="navigateToTopic('{topic_id}', event)">
                        <div class="nav-checkbox" id="check-{topic_id}" onclick="toggleCheck('{topic_id}', event)">
                            <svg viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
                        </div>
                        <span class="nav-item-title" id="nav-item-title-{topic_id}" title="{topic_title}">{topic_title}{badge}</span>
                    </a>
                </li>
            ''')
            
            kid_notes = get_kid_friendly_revision_notes(topic_id)
            if kid_notes:
                notes_content = kid_notes
            else:
                notes_content = topic["content_html"]
            
            tabs_html = ''
            playground_html = ''
            if has_ch:
                tabs_html = f'''
                <div class="card-tabs">
                    <button class="tab-btn active" onclick="switchTab('{topic_id}', 'notes')">Revision Notes</button>
                    <button class="tab-btn" onclick="switchTab('{topic_id}', 'playground')">Playground 📝</button>
                </div>
                '''
                playground_html = f'''
                <div class="card-content tab-pane-playground" id="content-{topic_id}-playground" style="display: none;">
                    <div class="playground-container">
                        <!-- Lab Selector -->
                        <div class="lab-selector">
                            <button class="lab-tab-btn active" id="lab-btn-{topic_id}-0" onclick="switchLab('{topic_id}', 0)">Lab 1</button>
                            <button class="lab-tab-btn" id="lab-btn-{topic_id}-1" onclick="switchLab('{topic_id}', 1)">Lab 2</button>
                            <button class="lab-tab-btn" id="lab-btn-{topic_id}-2" onclick="switchLab('{topic_id}', 2)">Lab 3</button>
                        </div>

                        <div class="challenge-box">
                            <div class="challenge-prompt" id="prompt-{topic_id}">
                                <strong>Loading challenge task...</strong>
                            </div>
                        </div>
                        
                        <div class="playground-editor-wrapper">
                            <div class="editor-header">
                                <span id="editor-title-{topic_id}">SQL Query Editor</span>
                                <button class="toggle-schema-btn" onclick="toggleSchemaDrawer()">Open Schema Explorer 🗄️</button>
                            </div>
                            <textarea id="editor-{topic_id}" class="sql-editor" rows="6" placeholder="Write your SQL here..." onkeydown="handleEditorKeys(event, '{topic_id}')"></textarea>
                        </div>
                        
                        <div class="playground-actions">
                            <button class="run-query-btn" onclick="runPlaygroundQuery('{topic_id}')" disabled>Run Query</button>
                            <button class="verify-query-btn" onclick="verifyPlaygroundQuery('{topic_id}')" disabled>Verify Answer ✓</button>
                            <button class="show-solution-btn" onclick="showPlaygroundSolution('{topic_id}')">Show Solution 💡</button>
                            <button class="reset-query-btn" onclick="resetPlaygroundQuery('{topic_id}')">Reset Query</button>
                        </div>
                        
                        <div class="results-container" id="results-{topic_id}">
                            <div class="results-placeholder">Write and execute your query above to verify the result!</div>
                        </div>
                    </div>
                </div>
                '''
            
            content_html.append(f'''
            <article class="topic-card" id="{topic_id}">
                <div class="card-header-bar">
                    <h1>
                        <div class="card-checkbox-container" onclick="toggleCardCheck('{topic_id}')">
                            <div class="nav-checkbox card-check" id="card-check-{topic_id}">
                                <svg viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
                            </div>
                        </div>
                        <span>{topic_title}</span>
                    </h1>
                    {tabs_html}
                </div>
                <div class="card-content tab-pane-notes" id="content-{topic_id}-notes">
                    <div class="card-body">
                        {notes_content}
                    </div>
                </div>
                {playground_html}
            </article>
            ''')
            
        sidebar_html.append('</ul></div>')
        
    challenges_json = json.dumps(CHALLENGES)
    
    html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SQL Practice & Hands-On Learning Portal</title>
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Fira+Code:wght@400;500;600&display=swap" rel="stylesheet">
    <!-- Code Highlight Stylesheet -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet" />
    <style>
        :root {{
            /* Dark Theme variables */
            --bg-primary: #0b0f19;
            --bg-secondary: #161d30;
            --bg-sidebar: #090d16;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --border-color: #242f4c;
            --accent-color: #6366f1;
            --accent-hover: #4f46e5;
            --code-bg: #070a12;
            --card-bg: #111827;
            --success-color: #10b981;
            --progress-bar-color: linear-gradient(90deg, #10b981, #059669);
            --shadow-color: rgba(0, 0, 0, 0.4);
        }}
        
        body.light-theme {{
            /* Light Theme variables */
            --bg-primary: #f8fafc;
            --bg-secondary: #ffffff;
            --bg-sidebar: #f1f5f9;
            --text-primary: #0f172a;
            --text-secondary: #64748b;
            --border-color: #e2e8f0;
            --accent-color: #4f46e5;
            --accent-hover: #4338ca;
            --code-bg: #1e293b;
            --card-bg: #ffffff;
            --success-color: #059669;
            --progress-bar-color: linear-gradient(90deg, #059669, #10b981);
            --shadow-color: rgba(99, 102, 241, 0.05);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            display: flex;
            height: 100vh;
            overflow: hidden;
            transition: background-color 0.3s, color 0.3s, border-color 0.3s;
        }}
        
        /* Sidebar Navigation styling */
        aside {{
            width: 330px;
            background-color: var(--bg-sidebar);
            border-right: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            height: 100%;
            z-index: 10;
            transition: background-color 0.3s, border-color 0.3s;
        }}
        
        .sidebar-header {{
            padding: 1.5rem;
            border-bottom: 1px solid var(--border-color);
        }}
        
        .sidebar-title {{
            font-size: 1.15rem;
            font-weight: 800;
            background: linear-gradient(135deg, var(--accent-color), #a855f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.25rem;
        }}
        
        .sidebar-subtitle {{
            font-size: 0.75rem;
            font-weight: 500;
            color: var(--text-secondary);
            letter-spacing: 0.02em;
        }}
        
        .search-wrapper {{
            padding: 1rem 1.5rem;
            position: relative;
            border-bottom: 1px solid var(--border-color);
        }}
        
        .search-input {{
            width: 100%;
            padding: 0.65rem 1rem 0.65rem 2.25rem;
            background-color: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            color: var(--text-primary);
            font-size: 0.85rem;
            outline: none;
            transition: border-color 0.2s, box-shadow 0.2s, background-color 0.3s;
        }}
        
        .search-input:focus {{
            border-color: var(--accent-color);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
        }}
        
        .search-icon {{
            position: absolute;
            left: 2.15rem;
            top: 50%;
            transform: translateY(-50%);
            width: 0.95rem;
            height: 0.95rem;
            fill: var(--text-secondary);
            pointer-events: none;
        }}
        
        .sidebar-nav {{
            flex: 1;
            overflow-y: auto;
            padding: 1.25rem 1rem;
        }}
        
        .nav-group {{
            margin-bottom: 1.25rem;
        }}
        
        .nav-group-header {{
            font-size: 0.72rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
            padding: 0 0.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            user-select: none;
            transition: color 0.2s;
        }}
        
        .nav-group-header:hover {{
            color: var(--accent-color);
        }}
        
        .nav-group-header::after {{
            content: '';
            display: inline-block;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 5px solid var(--text-secondary);
            transition: transform 0.25s ease;
        }}
        
        .nav-group.collapsed .nav-group-header::after {{
            transform: rotate(-90deg);
        }}
        
        .nav-group.collapsed .nav-group-list {{
            display: none;
        }}
        
        .nav-group-list {{
            list-style: none;
        }}
        
        .nav-item {{
            display: flex;
            align-items: center;
            gap: 0.65rem;
            padding: 0.45rem 0.5rem;
            border-radius: 6px;
            cursor: pointer;
            transition: background-color 0.2s, color 0.2s;
            margin-bottom: 0.15rem;
            text-decoration: none;
            color: var(--text-secondary);
        }}
        
        .nav-item:hover {{
            background-color: rgba(99, 102, 241, 0.06);
            color: var(--text-primary);
        }}
        
        .nav-item.active {{
            background-color: rgba(99, 102, 241, 0.12);
            font-weight: 600;
            color: var(--accent-color);
        }}
        
        .nav-checkbox {{
            width: 1rem;
            height: 1rem;
            border-radius: 4px;
            border: 1.5px solid var(--text-secondary);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            flex-shrink: 0;
            transition: background-color 0.2s, border-color 0.2s;
        }}
        
        .nav-checkbox:hover {{
            border-color: var(--accent-color);
        }}
        
        .nav-checkbox.checked {{
            background-color: var(--success-color);
            border-color: var(--success-color);
        }}
        
        .nav-checkbox svg {{
            width: 0.65rem;
            height: 0.65rem;
            fill: white;
            display: none;
        }}
        
        .nav-checkbox.checked svg {{
            display: block;
        }}
        
        .nav-item-title {{
            font-size: 0.8rem;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            flex: 1;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .nav-badge {{
            font-size: 0.6rem;
            font-weight: 800;
            background-color: rgba(99, 102, 241, 0.15);
            color: var(--accent-color);
            padding: 0.05rem 0.35rem;
            border-radius: 3px;
            text-transform: uppercase;
            letter-spacing: 0.02em;
        }}
        
        .nav-lab-progress {{
            font-size: 0.65rem;
            margin-left: 0.35rem;
        }}

        /* Main Layout styling */
        main {{
            flex: 1;
            height: 100%;
            overflow-y: auto;
            scroll-behavior: smooth;
            display: flex;
            flex-direction: column;
            background-color: var(--bg-primary);
            transition: background-color 0.3s;
        }}
        
        .main-header {{
            position: sticky;
            top: 0;
            background-color: rgba(11, 15, 25, 0.85);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            border-bottom: 1px solid var(--border-color);
            padding: 0.75rem 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            z-index: 5;
            transition: background-color 0.3s, border-color 0.3s;
        }}
        
        body.light-theme .main-header {{
            background-color: rgba(248, 250, 252, 0.85);
        }}
        
        .progress-wrapper {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            flex: 1;
            max-width: 420px;
        }}
        
        .progress-label {{
            font-size: 0.78rem;
            font-weight: 700;
            color: var(--text-secondary);
            white-space: nowrap;
        }}
        
        .progress-bar-track {{
            width: 100%;
            height: 7px;
            background-color: var(--border-color);
            border-radius: 4px;
            overflow: hidden;
            transition: background-color 0.3s;
        }}
        
        .progress-bar-fill {{
            height: 100%;
            width: 0%;
            background: var(--progress-bar-color);
            border-radius: 4px;
            transition: width 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        .header-actions {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        
        .theme-toggle {{
            background: none;
            border: 1px solid var(--border-color);
            padding: 0.45rem;
            border-radius: 6px;
            color: var(--text-primary);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background-color 0.2s, border-color 0.2s;
        }}
        
        .theme-toggle:hover {{
            background-color: rgba(99, 102, 241, 0.08);
            border-color: var(--accent-color);
        }}
        
        .theme-toggle svg {{
            width: 1.05rem;
            height: 1.05rem;
            fill: currentColor;
        }}
        
        .theme-toggle .sun-icon {{
            display: none;
        }}
        
        body.light-theme .theme-toggle .moon-icon {{
            display: none;
        }}
        
        body.light-theme .theme-toggle .sun-icon {{
            display: block;
        }}
        
        .content-container {{
            padding: 2rem;
            max-width: 960px;
            margin: 0 auto;
            width: 100%;
            flex: 1;
        }}
        
        /* Topic Card layout */
        .topic-card {{
            background-color: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 4px 12px var(--shadow-color);
            transition: border-color 0.3s, box-shadow 0.3s, background-color 0.3s;
            scroll-margin-top: 80px;
        }}
        
        .topic-card.hidden {{
            display: none;
        }}
        
        .topic-card:hover {{
            box-shadow: 0 8px 24px var(--shadow-color);
            border-color: rgba(99, 102, 241, 0.25);
        }}
        
        .card-header-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 0.75rem;
            margin-bottom: 1.25rem;
            flex-wrap: wrap;
            gap: 1rem;
        }}

        .topic-card h1 {{
            font-size: 1.35rem;
            font-weight: 800;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}
        
        .card-checkbox-container {{
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .card-check {{
            width: 1.25rem;
            height: 1.25rem;
            border-radius: 5px;
        }}
        
        .card-check svg {{
            width: 0.8rem;
            height: 0.8rem;
        }}
        
        /* Playground tabs */
        .card-tabs {{
            display: flex;
            gap: 0.35rem;
        }}
        .tab-btn {{
            background-color: transparent;
            border: 1px solid var(--border-color);
            color: var(--text-secondary);
            padding: 0.35rem 0.75rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s;
            font-family: inherit;
        }}
        .tab-btn:hover {{
            color: var(--text-primary);
            border-color: var(--accent-color);
        }}
        .tab-btn.active {{
            background-color: var(--accent-color);
            color: white;
            border-color: var(--accent-color);
        }}

        .topic-card h2 {{
            font-size: 1.05rem;
            font-weight: 700;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
            color: var(--accent-color);
            letter-spacing: -0.01em;
        }}
        
        .topic-card h3 {{
            font-size: 0.88rem;
            font-weight: 700;
            margin-top: 1.25rem;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-primary);
        }}
        
        .topic-card p {{
            font-size: 0.88rem;
            line-height: 1.6;
            margin-bottom: 0.75rem;
            color: var(--text-secondary);
        }}
        
        .topic-card strong {{
            color: var(--text-primary);
            font-weight: 600;
        }}
        
        .topic-card ul {{
            margin-bottom: 1.25rem;
            padding-left: 1.25rem;
            list-style-type: disc;
        }}
        
        .topic-card li {{
            font-size: 0.88rem;
            line-height: 1.5;
            margin-bottom: 0.4rem;
            color: var(--text-secondary);
        }}
        
        .topic-card hr {{
            border: 0;
            height: 1px;
            background-color: var(--border-color);
            margin: 2rem 0;
            transition: background-color 0.3s;
        }}
        
        /* Tables styling */
        .table-responsive {{
            overflow-x: auto;
            margin-bottom: 1.25rem;
            border-radius: 6px;
            border: 1px solid var(--border-color);
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.82rem;
            background-color: var(--bg-secondary);
        }}
        
        th, td {{
            padding: 0.65rem 0.85rem;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}
        
        th {{
            background-color: rgba(99, 102, 241, 0.06);
            font-weight: 700;
            color: var(--text-primary);
        }}
        
        tr:last-child td {{
            border-bottom: none;
        }}
        
        tr:nth-child(even) td {{
            background-color: rgba(255, 255, 255, 0.01);
        }}
        
        body.light-theme tr:nth-child(even) td {{
            background-color: rgba(0, 0, 0, 0.015);
        }}
        
        /* Code blocks styling */
        .code-container {{
            border: 1px solid var(--border-color);
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 1.25rem;
            background-color: var(--code-bg);
            transition: border-color 0.3s;
        }}
        
        .code-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.45rem 1rem;
            background-color: rgba(0, 0, 0, 0.3);
            border-bottom: 1px solid var(--border-color);
        }}
        
        .code-lang {{
            font-size: 0.7rem;
            font-weight: 700;
            font-family: 'Fira Code', monospace;
            color: var(--text-secondary);
            letter-spacing: 0.05em;
        }}
        
        .copy-btn {{
            background: none;
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: var(--text-secondary);
            font-size: 0.7rem;
            padding: 0.2rem 0.45rem;
            border-radius: 4px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 0.25rem;
            transition: all 0.2s;
            font-family: inherit;
        }}
        
        .copy-btn:hover {{
            color: var(--text-primary);
            border-color: rgba(255, 255, 255, 0.4);
            background-color: rgba(255, 255, 255, 0.05);
        }}
        
        .copy-icon {{
            width: 0.75rem;
            height: 0.75rem;
            fill: currentColor;
        }}
        
        pre {{
            margin: 0;
            padding: 0.85rem;
            overflow-x: auto;
            background-color: var(--code-bg) !important;
        }}
        
        code {{
            font-family: 'Fira Code', 'Courier New', monospace;
            font-size: 0.8rem;
            line-height: 1.5;
        }}
        
        /* Inline code style */
        :not(pre) > code {{
            background-color: rgba(99, 102, 241, 0.08);
            color: var(--accent-color);
            padding: 0.1rem 0.3rem;
            border-radius: 4px;
            font-size: 0.78rem;
            font-family: 'Fira Code', monospace;
        }}

        /* ETL Pro Tip Box */
        .etl-tip-box {{
            margin-top: 1.75rem;
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.04) 0%, rgba(16, 185, 129, 0.01) 100%);
            border: 1px solid var(--border-color);
            border-left: 4px solid var(--accent-color);
            border-radius: 8px;
            padding: 1.25rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            transition: transform 0.2s, border-color 0.2s;
        }}
        .etl-tip-box:hover {{
            border-color: var(--accent-color);
            transform: translateY(-1px);
        }}
        .etl-tip-header {{
            font-size: 0.82rem;
            font-weight: 800;
            color: var(--accent-color);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.65rem;
            display: flex;
            align-items: center;
            gap: 0.35rem;
        }}
        .etl-tip-content p {{
            font-size: 0.82rem !important;
            line-height: 1.55 !important;
            margin-bottom: 0.55rem !important;
            color: var(--text-primary) !important;
        }}
        .etl-tip-content p:last-child {{
            margin-bottom: 0 !important;
        }}
        .etl-tip-content ul {{
            margin-bottom: 0.65rem !important;
            padding-left: 1.25rem !important;
        }}
        .etl-tip-content li {{
            font-size: 0.82rem !important;
            line-height: 1.5 !important;
            margin-bottom: 0.25rem !important;
            color: var(--text-secondary) !important;
        }}
        .etl-performance {{
            background-color: rgba(245, 158, 11, 0.04);
            border: 1px solid rgba(245, 158, 11, 0.15);
            padding: 0.45rem 0.65rem;
            border-radius: 6px;
            font-size: 0.76rem !important;
            color: #f59e0b !important;
            display: flex;
            align-items: center;
            gap: 0.35rem;
            margin-top: 0.65rem;
            font-weight: 600;
        }}
        body.light-theme .etl-performance {{
            background-color: rgba(217, 119, 6, 0.03);
            border-color: rgba(217, 119, 6, 0.12);
            color: #b45309 !important;
        }}

        /* SQL Playground Interface styling */
        .playground-container {{
            display: flex;
            flex-direction: column;
            gap: 1rem;
            margin-top: 0.5rem;
        }}
        
        /* Lab Selector CSS */
        .lab-selector {{
            display: flex;
            gap: 0.5rem;
            margin-bottom: 0.25rem;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 0.5rem;
        }}
        .lab-tab-btn {{
            background-color: transparent;
            border: 1px solid var(--border-color);
            color: var(--text-secondary);
            padding: 0.3rem 0.65rem;
            border-radius: 4px;
            font-size: 0.72rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s;
            font-family: inherit;
        }}
        .lab-tab-btn:hover {{
            color: var(--text-primary);
            border-color: var(--accent-color);
        }}
        .lab-tab-btn.active {{
            background-color: rgba(99, 102, 241, 0.15);
            color: var(--accent-color);
            border-color: var(--accent-color);
        }}
        
        .challenge-box {{
            background-color: rgba(99, 102, 241, 0.05);
            border-left: 4px solid var(--accent-color);
            padding: 0.85rem;
            border-radius: 4px;
        }}
        .challenge-prompt {{
            font-size: 0.85rem;
            line-height: 1.5;
            color: var(--text-primary);
        }}
        .playground-editor-wrapper {{
            display: flex;
            flex-direction: column;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            overflow: hidden;
            background-color: var(--code-bg);
        }}
        .editor-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.45rem 1rem;
            background-color: rgba(0, 0, 0, 0.2);
            border-bottom: 1px solid var(--border-color);
            font-size: 0.72rem;
            font-weight: 700;
            color: var(--text-secondary);
        }}
        body.light-theme .editor-header {{
            background-color: rgba(0, 0, 0, 0.03);
        }}
        .sql-editor {{
            width: 100%;
            background-color: transparent;
            border: none;
            color: #e2e8f0;
            font-family: 'Fira Code', 'Courier New', monospace;
            font-size: 0.82rem;
            padding: 1rem;
            outline: none;
            resize: vertical;
            line-height: 1.55;
        }}
        body.light-theme .sql-editor {{
            color: #0f172a;
            background-color: #f8fafc;
        }}
        .playground-actions {{
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }}
        .run-query-btn, .verify-query-btn, .reset-query-btn {{
            padding: 0.45rem 0.85rem;
            border-radius: 6px;
            font-size: 0.78rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s;
            font-family: inherit;
        }}
        .run-query-btn {{
            background-color: var(--accent-color);
            color: white;
            border: 1px solid var(--accent-color);
        }}
        .run-query-btn:hover:not(:disabled) {{
            background-color: var(--accent-hover);
        }}
        .verify-query-btn {{
            background-color: transparent;
            color: var(--success-color);
            border: 1px solid var(--success-color);
        }}
        .verify-query-btn:hover:not(:disabled) {{
            background-color: rgba(16, 185, 129, 0.08);
        }}
        .reset-query-btn {{
            background-color: transparent;
            color: var(--text-secondary);
            border: 1px solid var(--border-color);
        }}
        .reset-query-btn:hover {{
            color: var(--text-primary);
            border-color: var(--text-primary);
        }}
        .run-query-btn:disabled, .verify-query-btn:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}
        .results-container {{
            background-color: rgba(0, 0, 0, 0.1);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 1rem;
            min-height: 80px;
        }}
        body.light-theme .results-container {{
            background-color: #f8fafc;
        }}
        .results-placeholder {{
            font-size: 0.8rem;
            color: var(--text-secondary);
            text-align: center;
            line-height: 3rem;
        }}
        .query-success {{
            font-size: 0.78rem;
            font-weight: 700;
            color: var(--success-color);
            margin-bottom: 0.75rem;
        }}
        .query-error {{
            background-color: rgba(239, 68, 68, 0.08);
            border: 1px solid #ef4444;
            color: #f87171;
            padding: 0.65rem;
            border-radius: 6px;
            font-size: 0.8rem;
            font-family: 'Fira Code', monospace;
        }}
        .verification-success {{
            background-color: rgba(16, 185, 129, 0.08);
            border: 1px solid var(--success-color);
            color: var(--text-primary);
            padding: 0.85rem;
            border-radius: 6px;
            display: flex;
            gap: 0.65rem;
            align-items: flex-start;
        }}
        .verification-success svg {{
            width: 1.35rem;
            height: 1.35rem;
            fill: var(--success-color);
            flex-shrink: 0;
        }}
        .verification-success strong {{
            color: var(--success-color);
            font-size: 0.85rem;
        }}
        .verification-success p {{
            font-size: 0.78rem;
            margin-top: 0.15rem;
        }}
        .verification-fail {{
            background-color: rgba(245, 158, 11, 0.08);
            border: 1px solid #f59e0b;
            color: var(--text-primary);
            padding: 0.85rem;
            border-radius: 6px;
            display: flex;
            gap: 0.65rem;
            align-items: flex-start;
        }}
        .verification-fail svg {{
            width: 1.35rem;
            height: 1.35rem;
            fill: #f59e0b;
            flex-shrink: 0;
        }}
        .verification-fail strong {{
            color: #f59e0b;
            font-size: 0.85rem;
        }}
        .verification-fail p {{
            font-size: 0.78rem;
            margin-top: 0.15rem;
        }}
        .mismatch-details {{
            font-size: 0.7rem;
            color: var(--text-secondary);
            font-family: 'Fira Code', monospace;
            display: block;
            margin-top: 0.25rem;
        }}
        .null-val {{
            color: #ef4444;
            font-weight: 700;
            font-size: 0.75rem;
        }}

        /* Schema Explorer Drawer styling */
        .schema-drawer {{
            position: fixed;
            top: 52px;
            right: -320px;
            width: 320px;
            height: calc(100vh - 52px);
            background-color: var(--bg-sidebar);
            border-left: 1px solid var(--border-color);
            box-shadow: -4px 0 16px rgba(0,0,0,0.15);
            z-index: 99;
            transition: right 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            flex-direction: column;
        }}
        .schema-drawer.open {{
            right: 0;
        }}
        .schema-drawer-header {{
            padding: 1rem;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .schema-drawer-title {{
            font-size: 0.85rem;
            font-weight: 800;
            color: var(--text-primary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .close-schema-btn {{
            background: none;
            border: none;
            color: var(--text-secondary);
            font-size: 1.1rem;
            cursor: pointer;
            transition: color 0.2s;
        }}
        .close-schema-btn:hover {{
            color: var(--text-primary);
        }}
        .schema-drawer-content {{
            flex: 1;
            overflow-y: auto;
            padding: 1rem;
        }}
        .schema-table {{
            border: 1px solid var(--border-color);
            border-radius: 6px;
            margin-bottom: 0.75rem;
            overflow: hidden;
            background-color: var(--bg-secondary);
        }}
        .schema-table-name {{
            background-color: rgba(99, 102, 241, 0.05);
            padding: 0.45rem 0.65rem;
            font-size: 0.78rem;
            font-weight: 800;
            cursor: pointer;
            user-select: none;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border-color);
            color: var(--text-primary);
        }}
        .schema-table-count {{
            font-size: 0.65rem;
            color: var(--text-secondary);
            font-weight: 500;
        }}
        .schema-cols {{
            list-style: none;
            padding: 0.45rem 0.65rem;
            display: flex;
            flex-direction: column;
            gap: 0.35rem;
        }}
        .schema-cols li {{
            display: flex;
            justify-content: space-between;
            font-size: 0.72rem;
            align-items: center;
        }}
        .col-name {{
            font-family: 'Fira Code', monospace;
            color: var(--text-primary);
            font-weight: 500;
        }}
        .col-type {{
            color: var(--text-secondary);
            font-size: 0.68rem;
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }}
        .pk-badge {{
            background-color: var(--accent-color);
            color: white;
            font-size: 0.5rem;
            padding: 0.02rem 0.2rem;
            border-radius: 2px;
            font-weight: 800;
        }}
        .toggle-schema-btn {{
            background: none;
            border: 1px solid var(--border-color);
            color: var(--text-secondary);
            padding: 0.25rem 0.45rem;
            border-radius: 4px;
            font-size: 0.68rem;
            cursor: pointer;
            transition: all 0.2s;
            font-weight: 700;
        }}
        .toggle-schema-btn:hover {{
            color: var(--text-primary);
            border-color: var(--accent-color);
            background-color: rgba(99, 102, 241, 0.05);
        }}
        
        /* Empty search overlay */
        .empty-search {{
            display: none;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 3rem;
            text-align: center;
            color: var(--text-secondary);
        }}
        
        .empty-search.visible {{
            display: flex;
        }}
        
        .empty-search svg {{
            width: 2.5rem;
            height: 2.5rem;
            fill: currentColor;
            margin-bottom: 1rem;
            opacity: 0.5;
        }}
        
        /* Floating toast notification */
        .toast {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: var(--bg-secondary);
            border: 1px solid var(--success-color);
            color: var(--text-primary);
            padding: 0.75rem 1.25rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            display: flex;
            align-items: center;
            gap: 0.5rem;
            transform: translateY(100px);
            opacity: 0;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            z-index: 100;
            font-size: 0.82rem;
            font-weight: 600;
        }}
        
        .toast.show {{
            transform: translateY(0);
            opacity: 1;
        }}
        
        .toast.toast-error {{
            border-color: #ef4444;
        }}
        
        .toast svg {{
            width: 1.1rem;
            height: 1.1rem;
            fill: var(--success-color);
        }}
        
        .toast.toast-error svg {{
            fill: #ef4444;
        }}

        /* Kid theory styles */
        .kid-theory-section {{
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
        }}
        .theory-imagine-box, .theory-ask-box, .theory-block, .how-sql-thinks, .theory-output-box, .important-connection, .memory-trick, .etl-de-why {{
            border-radius: 8px;
            padding: 1.25rem;
            border: 1px solid var(--border-color);
            background-color: var(--bg-primary);
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            transition: all 0.2s ease;
        }}
        .theory-imagine-box:hover, .theory-ask-box:hover, .theory-block:hover, .how-sql-thinks:hover, .theory-output-box:hover, .important-connection:hover, .memory-trick:hover, .etl-de-why:hover {{
            transform: translateY(-1px);
            border-color: var(--accent-color);
        }}
        .theory-imagine-box strong, .theory-ask-box strong, .theory-block strong, .how-sql-thinks strong, .theory-output-box strong, .important-connection strong, .memory-trick strong, .etl-de-why strong {{
            display: block;
            font-size: 0.88rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--accent-color);
            margin-bottom: 0.5rem;
        }}
        .theory-ask-box {{
            border-left: 4px solid var(--accent-color);
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(99, 102, 241, 0.01) 100%);
        }}
        .important-connection {{
            border-left: 4px solid var(--success-color);
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, rgba(16, 185, 129, 0.01) 100%);
        }}
        .important-connection strong {{
            color: var(--success-color);
        }}
        .memory-trick {{
            border-left: 4px solid #a855f7;
            background: linear-gradient(135deg, rgba(168, 85, 247, 0.05) 0%, rgba(168, 85, 247, 0.01) 100%);
        }}
        .memory-trick strong {{
            color: #a855f7;
        }}
        .etl-de-why {{
            border-left: 4px solid #f59e0b;
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.05) 0%, rgba(245, 158, 11, 0.01) 100%);
        }}
        .etl-de-why strong {{
            color: #f59e0b;
        }}
        .how-sql-thinks ul {{
            padding-left: 1.2rem;
            margin-top: 0.5rem;
            list-style-type: disc;
        }}
        .how-sql-thinks li {{
            font-size: 0.85rem !important;
            line-height: 1.6 !important;
            margin-bottom: 0.35rem;
            color: var(--text-secondary);
        }}
        .show-solution-btn {{
            background-color: transparent;
            color: #a855f7;
            border: 1px solid #a855f7;
        }}
        .show-solution-btn:hover {{
            background-color: rgba(168, 85, 247, 0.08);
        }}
    </style>
</head>
<body>
    <!-- Sidebar -->
    <aside>
        <div class="sidebar-header">
            <h1 class="sidebar-title">SQL LEARNING LAB</h1>
            <p class="sidebar-subtitle">Interactive Practice & Revision</p>
        </div>
        <div class="search-wrapper">
            <svg class="search-icon" viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
            <input type="text" id="search" class="search-input" placeholder="Search topics, patterns..." oninput="handleSearch()">
        </div>
        <nav class="sidebar-nav">
            {chr(10).join(sidebar_html)}
        </nav>
    </aside>

    <!-- Main Content Area -->
    <main>
        <header class="main-header">
            <div class="progress-wrapper">
                <span class="progress-label" id="progress-text">Progress: 0 / {total_topics} (0%)</span>
                <div class="progress-bar-track">
                    <div class="progress-bar-fill" id="progress-bar"></div>
                </div>
            </div>
            <div class="header-actions">
                <button class="theme-toggle" onclick="toggleTheme()" title="Toggle Dark/Light Mode">
                    <svg class="moon-icon" viewBox="0 0 24 24"><path d="M12.1 22c-5.5 0-10-4.5-10-10 0-4.8 3.5-8.9 8.2-9.8.5-.1 1 .3.9.8-.1.4-.4.8-.4 1.2 0 4.4 3.6 8 8 8 .4 0 .8-.1 1.2-.2.5-.1.9.4.8.9-1 4.7-5.1 8.1-9.7 8.1zm-7.1-10c0 3.9 3.1 7 7 7 2.6 0 4.9-1.4 6.1-3.6-.8.2-1.7.3-2.6.3-5.5 0-10-4.5-10-10 0-.9.1-1.8.3-2.6C5.6 4.3 5 6.6 5 9c0 1.7.7 3.2 1.9 4.3-.6-1.1-1-2.4-1-3.8 0-.4.3-.7.7-.7.4 0 .7.3.7.7 0 2.2 1.8 4 4 4 .4 0 .7-.3.7-.7s-.3-.7-.7-.7c-3 0-5.4-2.4-5.4-5.4 0-.4.3-.7.7-.7.4 0 .7.3.7.7 0 4.4 3.6 8 8 8 .4 0 .7-.3.7-.7s-.3-.7-.7-.7c-5.8 0-10.5-4.7-10.5-10.5 0-.4.3-.7.7-.7.4 0 .7.3.7.7C8 9.2 9.8 11 12 11c.4 0 .7-.3.7-.7s-.3-.7-.7-.7c-4.4 0-8-3.6-8-8 0-.4.3-.7.7-.7.4 0 .7.3.7.7.1 5.5 4.6 10 10.1 10 .4 0 .7-.3.7-.7s-.3-.7-.7-.7z"/></svg>
                    <svg class="sun-icon" viewBox="0 0 24 24"><path d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-1h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.99 4.58c-.39-.39-1.03-.39-1.41 0s-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0s.39-1.03 0-1.41L5.99 4.58zm12.37 12.37c-.39-.39-1.03-.39-1.41 0s-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0s.39-1.03 0-1.41l-1.06-1.06zm1.06-12.37c-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06c.39-.39.39-1.03 0-1.41zm-12.37 12.37c-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06c.39-.39.39-1.03 0-1.41z"/></svg>
                </button>
            </div>
        </header>
        <div class="content-container" id="content-container">
            {chr(10).join(content_html)}
            <div class="empty-search" id="empty-search">
                <svg viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
                <h2>No Topics Found</h2>
                <p>Try refining your search terms.</p>
            </div>
        </div>
    </main>

    <!-- Schema Explorer Drawer -->
    <div id="schema-drawer" class="schema-drawer">
        <div class="schema-drawer-header">
            <span class="schema-drawer-title">Database Schema Reference</span>
            <button class="close-schema-btn" onclick="toggleSchemaDrawer()">×</button>
        </div>
        <div class="schema-drawer-content" id="schema-list">
            <div style="font-size: 0.8rem; color: var(--text-secondary); text-align: center; padding: 2rem;">
                Loading SQLite Engine...
            </div>
        </div>
    </div>

    <!-- Toast Notification -->
    <div id="toast" class="toast">
        <svg id="toast-icon-success" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
        <span id="toast-message">Copied to clipboard!</span>
    </div>

    <!-- Code Highlight scripts -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-core.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/autoloader/prism-autoloader.min.js"></script>
    
    <!-- SQLite WebAssembly Loader -->
    <script src="https://cdn.jsdelivr.net/npm/sql.js@1.8.0/dist/sql-wasm.js"></script>
    
    <!-- Confetti Explosion script -->
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
    
    <script>
        // Seeding database statement script
        const SEED_SQL = `{SEED_SQL.replace("`", "\\`").replace("$", "\\$")}`;

        // Practice challenges mapping
        const challenges = {challenges_json};

        // Progress tracking State
        let progress = {{}};
        
        // Active Lab indices
        let activeLab = {{}};
        
        // SQLite database context
        let db = null;
        let SQL = null;
        
        // Initial Loading
        window.addEventListener('DOMContentLoaded', () => {{
            loadProgress();
            loadTheme();
            setupIntersectionObserver();
            initDatabase();
            
            if (window.location.hash) {{
                const id = window.location.hash.substring(1);
                const el = document.getElementById(id);
                if (el) {{
                    setTimeout(() => {{
                        el.scrollIntoView({{ behavior: 'smooth' }});
                        highlightNav(id);
                    }}, 200);
                }}
            }} else {{
                const firstCard = document.querySelector('.topic-card');
                if (firstCard) {{
                    highlightNav(firstCard.id);
                }}
            }}
        }});
        
        // Initialize SQLite Engine
        async function initDatabase() {{
            try {{
                SQL = await initSqlJs({{
                    locateFile: file => `https://cdn.jsdelivr.net/npm/sql.js@1.8.0/dist/${{file}}`
                }});
                db = new SQL.Database();
                db.run(SEED_SQL);
                
                document.querySelectorAll('.run-query-btn, .verify-query-btn').forEach(btn => {{
                    btn.disabled = false;
                }});
                
                // Initialize default lab tabs
                Object.keys(challenges).forEach(topicId => {{
                    activeLab[topicId] = 0;
                    switchLab(topicId, 0);
                }});
                
                renderSchema();
                updateSidebarUI();
                showToast("Interactive SQLite playground loaded successfully!");
            }} catch (e) {{
                console.error("Failed to load SQLite WebAssembly:", e);
                showToast("Failed to load SQL engine. Online connection is required for playground practice.", true);
            }}
        }}

        // Render DB columns and tables dynamically
        function renderSchema() {{
            if (!db) return;
            try {{
                const tablesResult = db.exec("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name");
                if (tablesResult.length === 0) return;
                
                const tables = tablesResult[0].values.map(v => v[0]);
                let schemaHtml = '';
                
                tables.forEach(tableName => {{
                    const columnsResult = db.exec(`PRAGMA table_info(${{tableName}})`);
                    const columns = columnsResult[0].values;
                    
                    schemaHtml += `
                        <div class="schema-table">
                            <div class="schema-table-name" onclick="toggleSchemaTable('${{tableName}}')">
                                <span>📁 ${{tableName}}</span>
                                <span class="schema-table-count">(${{getTableRowsCount(tableName)}} rows)</span>
                            </div>
                            <ul class="schema-cols" id="schema-cols-${{tableName}}" style="display: none;">
                    `;
                    
                    columns.forEach(col => {{
                        const colName = col[1];
                        const colType = col[2];
                        const isPk = col[5] === 1 ? ' <span class="pk-badge">PK</span>' : '';
                        schemaHtml += `
                            <li>
                                <span class="col-name">${{colName}}</span>
                                <span class="col-type">${{colType.toLowerCase()}}${{isPk}}</span>
                            </li>
                        `;
                    }});
                    
                    schemaHtml += `</ul></div>`;
                }});
                
                document.getElementById('schema-list').innerHTML = schemaHtml;
            }} catch (e) {{
                console.error("Failed to render schema:", e);
            }}
        }}

        function getTableRowsCount(tableName) {{
            try {{
                const res = db.exec(`SELECT COUNT(*) FROM ${{tableName}}`);
                return res[0].values[0][0];
            }} catch (e) {{
                return 0;
            }}
        }}

        function toggleSchemaTable(tableName) {{
            const colsList = document.getElementById('schema-cols-' + tableName);
            if (colsList) {{
                colsList.style.display = colsList.style.display === 'none' ? 'flex' : 'none';
            }}
        }}

        function toggleSchemaDrawer() {{
            document.getElementById('schema-drawer').classList.toggle('open');
        }}

        // Tab Switching logic (Notes vs Playground)
        function switchTab(topicId, tabType) {{
            const card = document.getElementById(topicId);
            const tabButtons = card.querySelectorAll('.tab-btn');
            const tabPanes = card.querySelectorAll('.card-content');
            
            tabButtons.forEach(btn => {{
                if (btn.getAttribute('onclick').includes(`'${{tabType}}'`)) {{
                    btn.classList.add('active');
                }} else {{
                    btn.classList.remove('active');
                }}
            }});
            
            tabPanes.forEach(pane => {{
                if (pane.id === `content-${{topicId}}-${{tabType}}`) {{
                    pane.style.display = 'block';
                }} else {{
                    pane.style.display = 'none';
                }}
            }});
        }}

        // Switch between Lab 1, 2, 3
        function switchLab(topicId, labIdx) {{
            activeLab[topicId] = labIdx;
            
            const card = document.getElementById(topicId);
            const labButtons = card.querySelectorAll('.lab-tab-btn');
            
            labButtons.forEach((btn, idx) => {{
                if (idx === labIdx) {{
                    btn.classList.add('active');
                }} else {{
                    btn.classList.remove('active');
                }}
            }});
            
            const lab = challenges[topicId][labIdx];
            document.getElementById('prompt-' + topicId).innerHTML = `<strong>${{lab.title}}:</strong> ${{lab.prompt}}`;
            document.getElementById('editor-title-' + topicId).innerText = `${{lab.title}} Editor`;
            
            loadLabCode(topicId, labIdx);
        }}

        // Load / Persist SQL in editor
        function loadLabCode(topicId, labIdx) {{
            const key = `sql_playground_code_${{topicId}}_${{labIdx}}`;
            const saved = localStorage.getItem(key);
            const editor = document.getElementById('editor-' + topicId);
            const lab = challenges[topicId][labIdx];
            
            editor.value = saved !== null ? saved : lab.initialCode;
            
            document.getElementById('results-' + topicId).innerHTML = '<div class="results-placeholder">Write and execute your query above to verify the result!</div>';
            
            editor.oninput = () => {{
                localStorage.setItem(key, editor.value);
            }};
        }}

        // Run SQL query in the playground
        function runPlaygroundQuery(topicId) {{
            const editor = document.getElementById('editor-' + topicId);
            const sql = editor.value;
            const resultsContainer = document.getElementById('results-' + topicId);
            
            if (!db) {{
                resultsContainer.innerHTML = '<div class="query-error">SQL engine is not initialized.</div>';
                return;
            }}
            
            try {{
                const startTime = performance.now();
                const results = db.exec(sql);
                const endTime = performance.now();
                const duration = (endTime - startTime).toFixed(1);
                
                if (results.length === 0) {{
                    resultsContainer.innerHTML = `<div class="query-success">Query executed successfully in ${{duration}}ms! No rows returned.</div>`;
                    return;
                }}
                
                const cols = results[0].columns;
                const rows = results[0].values;
                
                let tableHtml = `
                    <div class="query-success">Query executed successfully in ${{duration}}ms! ${{rows.length}} rows returned.</div>
                    <div class="table-responsive">
                        <table>
                            <thead>
                                <tr>
                                    ${{cols.map(c => `<th>${{c}}</th>`).join('')}}
                                </tr>
                            </thead>
                            <tbody>
                                ${{rows.map(row => `
                                    <tr>
                                        ${{row.map(val => `<td>${{val === null ? '<span class="null-val">NULL</span>' : htmlEscape(val.toString())}}</td>`).join('')}}
                                    </tr>
                                `).join('')}}
                            </tbody>
                        </table>
                    </div>
                `;
                resultsContainer.innerHTML = tableHtml;
            }} catch (e) {{
                resultsContainer.innerHTML = `<div class="query-error"><strong>SQL Error:</strong> ${{htmlEscape(e.message)}}</div>`;
            }}
        }}

        // Reset Playground query
        function resetPlaygroundQuery(topicId) {{
            const labIdx = activeLab[topicId] || 0;
            const lab = challenges[topicId][labIdx];
            if (lab) {{
                const key = `sql_playground_code_${{topicId}}_${{labIdx}}`;
                localStorage.removeItem(key);
                document.getElementById('editor-' + topicId).value = lab.initialCode;
                document.getElementById('results-' + topicId).innerHTML = '<div class="results-placeholder">Write and execute your query above to verify the result!</div>';
                showToast("Query reset to template.");
            }}
        }}

        // Show target query solution
        function showPlaygroundSolution(topicId) {{
            const labIdx = activeLab[topicId] || 0;
            const ch = challenges[topicId][labIdx];
            if (ch) {{
                const resultsContainer = document.getElementById('results-' + topicId);
                resultsContainer.innerHTML = `
                    <div style="background-color: rgba(168, 85, 247, 0.08); border: 1px solid #a855f7; padding: 0.85rem; border-radius: 6px; margin-top: 0.5rem; text-align: left;">
                        <strong style="color: #a855f7; font-size: 0.8rem; display: block; margin-bottom: 0.35rem; text-transform: uppercase;">Expected Solution:</strong>
                        <pre style="margin: 0; padding: 0.5rem; background: var(--code-bg); border-radius: 4px; overflow-x: auto;"><code class="language-sql" style="font-size: 0.82rem; font-family: 'Fira Code', monospace; color: #a855f7;">${{htmlEscape(ch.targetQuery)}}</code></pre>
                    </div>
                `;
                showToast("Solution query displayed below!");
            }}
        }}

        // Verify Playground Query Answer
        function verifyPlaygroundQuery(topicId) {{
            const labIdx = activeLab[topicId] || 0;
            const ch = challenges[topicId][labIdx];
            if (!ch) return;
            
            const editor = document.getElementById('editor-' + topicId);
            const userSql = editor.value;
            const resultsContainer = document.getElementById('results-' + topicId);
            
            if (!db) {{
                resultsContainer.innerHTML = '<div class="query-error">SQL engine is not loaded.</div>';
                return;
            }}
            
            try {{
                const userRes = db.exec(userSql);
                const targetRes = db.exec(ch.targetQuery);
                
                const isMatch = compareResults(userRes, targetRes);
                
                if (isMatch) {{
                    resultsContainer.innerHTML = `
                        <div class="verification-success">
                            <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
                            <div>
                                <strong>Lab Completed! ✓</strong>
                                <p>Perfect! Your query output matches the target dataset exactly.</p>
                            </div>
                        </div>
                    `;
                    
                    const progressKey = `${{topicId}}_${{labIdx}}`;
                    if (!progress[progressKey]) {{
                        progress[progressKey] = true;
                        saveProgress();
                        updateSidebarUI();
                    }}
                    triggerConfetti();
                }} else {{
                    const userRowsCount = userRes.length > 0 ? userRes[0].values.length : 0;
                    const targetRowsCount = targetRes[0].values.length;
                    
                    resultsContainer.innerHTML = `
                        <div class="verification-fail">
                            <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
                            <div>
                                <strong>Output Mismatch</strong>
                                <p>Your query ran successfully, but the output rows/columns do not match the expected solution.</p>
                                <span class="mismatch-details">Your output: ${{userRowsCount}} rows. Expected output: ${{targetRowsCount}} rows.</span>
                            </div>
                        </div>
                    `;
                    
                    if (userRes.length > 0) {{
                        const cols = userRes[0].columns;
                        const rows = userRes[0].values;
                        resultsContainer.innerHTML += `
                            <div class="table-responsive" style="margin-top: 1rem; opacity: 0.85;">
                                <table>
                                    <thead>
                                        <tr>
                                            ${{cols.map(c => `<th>${{c}}</th>`).join('')}}
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${{rows.map(row => `
                                            <tr>
                                                ${{row.map(val => `<td>${{val === null ? 'NULL' : htmlEscape(val.toString())}}</td>`).join('')}}
                                            </tr>
                                        `).join('')}}
                                    </tbody>
                                </table>
                            </div>
                        `;
                    }}
                }}
            }} catch (e) {{
                resultsContainer.innerHTML = `<div class="query-error"><strong>SQL Error:</strong> ${{htmlEscape(e.message)}}</div>`;
            }}
        }}

        function compareResults(res1, res2) {{
            if (res1.length === 0 || res2.length === 0) {{
                return res1.length === res2.length;
            }}
            
            const col1 = res1[0].columns.map(c => c.toLowerCase());
            const col2 = res2[0].columns.map(c => c.toLowerCase());
            if (col1.length !== col2.length) return false;
            
            const val1 = res1[0].values;
            const val2 = res2[0].values;
            if (val1.length !== val2.length) return false;
            
            const normalize = (values) => {{
                return values.map(row => row.map(v => v === null ? 'NULL' : v.toString()).join('|')).sort().join('\\n');
            }};
            
            return normalize(val1) === normalize(val2);
        }}

        function htmlEscape(str) {{
            return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
        }}

        function handleEditorKeys(event, topicId) {{
            if (event.ctrlKey && event.key === 'Enter') {{
                event.preventDefault();
                runPlaygroundQuery(topicId);
            }}
        }}

        function triggerConfetti() {{
            if (typeof confetti === 'function') {{
                confetti({{
                    particleCount: 80,
                    spread: 60,
                    origin: {{ y: 0.8 }}
                }});
            }}
        }}

        // Progress state loading
        function loadProgress() {{
            const saved = localStorage.getItem('sql_tracker_progress');
            if (saved) {{
                try {{
                    progress = JSON.parse(saved);
                }} catch (e) {{
                    progress = {{}};
                }}
            }}
        }}
        
        function saveProgress() {{
            localStorage.setItem('sql_tracker_progress', JSON.stringify(progress));
        }}
        
        // Count solved labs for a topic
        function getTopicCompletedCount(topicId) {{
            if (!challenges[topicId]) {{
                return progress[topicId] ? 1 : 0;
            }}
            let count = 0;
            for (let i = 0; i < 3; i++) {{
                if (progress[topicId + '_' + i]) count++;
            }}
            return count;
        }}

        function isTopicFullyCompleted(topicId) {{
            if (!challenges[topicId]) {{
                return !!progress[topicId];
            }}
            return progress[topicId + '_0'] && progress[topicId + '_1'] && progress[topicId + '_2'];
        }}

        // Update sidebar and checkbox indicators
        function updateSidebarUI() {{
            Object.keys(challenges).forEach(topicId => {{
                const completed = getTopicCompletedCount(topicId);
                const navLink = document.getElementById('nav-link-' + topicId);
                
                if (navLink) {{
                    let badge = navLink.querySelector('.nav-lab-progress');
                    if (!badge) {{
                        badge = document.createElement('span');
                        badge.className = 'nav-lab-progress';
                        navLink.querySelector('.nav-item-title').appendChild(badge);
                    }}
                    
                    const isFull = completed === 3;
                    badge.innerText = isFull ? ' ✓' : ` (${{completed}}/3)`;
                    badge.style.color = isFull ? 'var(--success-color)' : 'var(--text-secondary)';
                    badge.style.fontWeight = isFull ? '800' : 'normal';
                    
                    // Sync checkboxes
                    const checkEl = document.getElementById('check-' + topicId);
                    const cardCheckEl = document.getElementById('card-check-' + topicId);
                    
                    if (isFull) {{
                        if (checkEl) checkEl.classList.add('checked');
                        if (cardCheckEl) cardCheckEl.classList.add('checked');
                    }} else {{
                        if (checkEl) checkEl.classList.remove('checked');
                        if (cardCheckEl) cardCheckEl.classList.remove('checked');
                    }}
                }}
            }});
            
            // For non-challenge items
            document.querySelectorAll('.nav-item').forEach(navLink => {{
                const topicId = navLink.id.replace('nav-link-', '');
                if (!challenges[topicId]) {{
                    const checkEl = document.getElementById('check-' + topicId);
                    const cardCheckEl = document.getElementById('card-check-' + topicId);
                    if (progress[topicId]) {{
                        if (checkEl) checkEl.classList.add('checked');
                        if (cardCheckEl) cardCheckEl.classList.add('checked');
                    }} else {{
                        if (checkEl) checkEl.classList.remove('checked');
                        if (cardCheckEl) cardCheckEl.classList.remove('checked');
                    }}
                }}
            }});
            
            updateProgressBar();
        }}
        
        function getProgressStats() {{
            let total = 0;
            let completed = 0;
            
            const navLinks = document.querySelectorAll('.nav-item');
            navLinks.forEach(navLink => {{
                const topicId = navLink.id.replace('nav-link-', '');
                if (challenges[topicId]) {{
                    total += 3;
                    for (let i = 0; i < 3; i++) {{
                        if (progress[topicId + '_' + i]) completed++;
                    }}
                }} else {{
                    total += 1;
                    if (progress[topicId]) completed++;
                }}
            }});
            
            return {{ total, completed }};
        }}

        function updateProgressBar() {{
            const stats = getProgressStats();
            const percentage = stats.total > 0 ? Math.round((stats.completed / stats.total) * 100) : 0;
            
            document.getElementById('progress-text').innerText = `Progress: ${{stats.completed}} / ${{stats.total}} (${{percentage}}%)`;
            document.getElementById('progress-bar').style.width = percentage + '%';
        }}
        
        function toggleCheck(topicId, event) {{
            if (event) event.stopPropagation();
            
            // For challenge topics, manually clicking toggle updates all labs
            if (challenges[topicId]) {{
                const willComplete = !isTopicFullyCompleted(topicId);
                for (let i = 0; i < 3; i++) {{
                    progress[topicId + '_' + i] = willComplete;
                }}
            }} else {{
                progress[topicId] = !progress[topicId];
            }}
            
            saveProgress();
            updateSidebarUI();
            showToast("Progress updated!");
        }}
        
        function toggleCardCheck(topicId) {{
            toggleCheck(topicId);
        }}
        
        // Theme switching logic
        function toggleTheme() {{
            document.body.classList.toggle('light-theme');
            const isLight = document.body.classList.contains('light-theme');
            localStorage.setItem('sql_tracker_theme', isLight ? 'light' : 'dark');
        }}
        
        function loadTheme() {{
            const savedTheme = localStorage.getItem('sql_tracker_theme');
            if (savedTheme === 'light') {{
                document.body.classList.add('light-theme');
            }}
        }}
        
        // Search functionality
        function handleSearch() {{
            const query = document.getElementById('search').value.toLowerCase().trim();
            const cards = document.querySelectorAll('.topic-card');
            const emptyEl = document.getElementById('empty-search');
            let foundCount = 0;
            
            cards.forEach(card => {{
                const text = card.textContent.toLowerCase();
                const topicId = card.id;
                const sidebarItem = document.getElementById('nav-link-' + topicId)?.parentElement;
                
                if (text.includes(query)) {{
                    card.classList.remove('hidden');
                    if (sidebarItem) sidebarItem.style.display = 'block';
                    foundCount++;
                }} else {{
                    card.classList.add('hidden');
                    if (sidebarItem) sidebarItem.style.display = 'none';
                }}
            }});
            
            document.querySelectorAll('.nav-group').forEach(group => {{
                const list = group.querySelector('.nav-group-list');
                const visibleItems = Array.from(list.children).filter(li => li.style.display !== 'none');
                if (visibleItems.length === 0 && query !== '') {{
                    group.style.display = 'none';
                }} else {{
                    group.style.display = 'block';
                }}
            }});
            
            if (foundCount === 0) {{
                emptyEl.classList.add('visible');
            }} else {{
                emptyEl.classList.remove('visible');
            }}
        }}
        
        function toggleGroup(catId) {{
            const groupEl = document.getElementById('group-' + catId);
            if (groupEl) {{
                groupEl.classList.toggle('collapsed');
            }}
        }}
        
        function navigateToTopic(topicId, event) {{
            event.preventDefault();
            const el = document.getElementById(topicId);
            if (el) {{
                el.scrollIntoView({{ behavior: 'smooth' }});
                history.pushState(null, null, '#' + topicId);
                highlightNav(topicId);
            }}
        }}
        
        function highlightNav(topicId) {{
            document.querySelectorAll('.nav-item').forEach(item => {{
                item.classList.remove('active');
            }});
            const activeLink = document.getElementById('nav-link-' + topicId);
            if (activeLink) {{
                activeLink.classList.add('active');
                const group = activeLink.closest('.nav-group');
                if (group) {{
                    group.classList.remove('collapsed');
                }}
                activeLink.scrollIntoView({{ behavior: 'nearest', block: 'center' }});
            }}
        }}
        
        let isScrolling = false;
        function setupIntersectionObserver() {{
            const observerOptions = {{
                root: document.querySelector('main'),
                rootMargin: '-20% 0px -60% 0px',
                threshold: 0
            }};
            
            const observer = new IntersectionObserver((entries) => {{
                if (isScrolling) return;
                entries.forEach(entry => {{
                    if (entry.isIntersecting) {{
                        highlightNav(entry.target.id);
                    }}
                }});
            }}, observerOptions);
            
            document.querySelectorAll('.topic-card').forEach(card => {{
                observer.observe(card);
            }});
            
            document.querySelector('main').addEventListener('scroll', () => {{
                isScrolling = false;
            }});
        }}
        
        function copyCode(btn) {{
            const codeBlock = btn.closest('.code-container').querySelector('code');
            const textToCopy = codeBlock.textContent;
            
            navigator.clipboard.writeText(textToCopy).then(() => {{
                showToast("Code copied to clipboard!");
                
                const btnSpan = btn.querySelector('span');
                const prevText = btnSpan.innerText;
                btnSpan.innerText = 'Copied!';
                btn.style.borderColor = 'var(--success-color)';
                btn.style.color = 'var(--success-color)';
                
                setTimeout(() => {{
                    btnSpan.innerText = prevText;
                    btn.style.borderColor = '';
                    btn.style.color = '';
                }}, 2000);
            }}).catch(err => {{
                console.error('Failed to copy text: ', err);
            }});
        }}
        
        function showToast(message, isError = false) {{
            const toast = document.getElementById('toast');
            const toastMessage = document.getElementById('toast-message');
            
            toastMessage.innerText = message;
            if (isError) {{
                toast.classList.add('toast-error');
            }} else {{
                toast.classList.remove('toast-error');
            }}
            
            toast.classList.add('show');
            setTimeout(() => {{
                toast.classList.remove('show');
            }}, 2500);
        }}
    </script>
</body>
</html>
'''
    return html_template

def main():
    print(f"Reading {SOURCE_FILE}...")
    try:
        categories = parse_file(SOURCE_FILE)
        print(f"Parsed {len(categories)} categories successfully.")
        
        # Filter categories and topics to keep SQL topics only
        filtered_categories = []
        for cat in categories:
            cat_upper = cat["title"].upper()
            if any(kw in cat_upper for kw in ["INTRODUCTION", "DAILY REVISION", "CHEAT SHEET", "FINAL GOAL", "STATUS"]):
                continue
                
            filtered_topics = []
            for topic in cat["topics"]:
                topic_upper = topic["title"].upper()
                if any(kw in topic_upper for kw in ["WELCOME", "PURPOSE", "PENDING SQL TOPICS ROADMAP", "IMPORTANT LEARNING STRATEGY", "MOST IMPORTANT PATTERNS", "STATUS"]):
                    continue
                filtered_topics.append(topic)
                
            if filtered_topics:
                cat["topics"] = filtered_topics
                if "PHASE 1" in cat_upper:
                    cat["title"] = "Core SQL Foundation"
                elif "PENDING" in cat_upper or "ROADMAP" in cat_upper:
                    cat["title"] = "Advanced SQL Topics"
                filtered_categories.append(cat)
        
        print(f"Filtered to {len(filtered_categories)} categories with actual SQL topics.")
        html_content = build_html(filtered_categories)
        
        print(f"Writing parsed output to {OUTPUT_FILE}...")
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(html_content)
        print("Success! The interactive SQL.js playground file was created with filtered SQL topics.")
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
