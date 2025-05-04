
from currensee.schema.schema import PostgresTables


crm_portfolio_table_desc = """
This table lists the investment funds held by client companies through their accounts at our bank. Use this table to identify which funds a specific client owns, and how much is invested in each.

IMPORTANT:
- `company` refers to the client company that owns one or more funds. It is NOT a stock or a mutual fund itself.
- Use this table to answer questions like: "What funds does a client own?" or "What is a company's total portfolio value?"
WARNING: When filtering by fund type (e.g., "Equity Fund"), always apply the filter on the `fund_type` column in the `portfolio` table, not in `fund_detail`. The `portfolio` table represents the funds a client owns. The `fund_detail` table only describes what’s inside the fund, not its type.


Columns:
- account_id: Unique identifier for the client's account.
- company: Name of the client company.
- fund_type: Category of the fund (Equity Fund or Bond Fund).
- symbol: Identifier of the fund. This is used to join with the `fund_detail` table.
- tot_balance: Total assets held by the client.
- fund_balance: Amount the client has invested in this particular fund.
"""

crm_fund_details_desc = """
This table lists the specific stocks or bonds held within each mutual fund. Funds can be bond funds or equity funds. Use this table to determine which assets are held in a fund.

NOTE: The `position_name` column refers to the name of the stock or bond inside a fund. It does NOT refer to a client company. 
NOTE: Do not use `fund_type` in this table to filter for client fund types (e.g., Equity). Instead, apply the `fund_type` filter in the `portfolio` table — that’s where the type of fund the client owns is defined.

Columns:
- ticker (Primary Key): Ticker of the individual asset.
- position_name: Full name of the stock or bond.
- fund (Foreign Key, portfolio.symbol): Symbol of the fund holding this asset.
- weight: Proportion of the fund held in this asset.
"""

crm_client_alignment_table_desc = """
Use when query involves which clients are assigned to a bank employee, what other employees a client has spoken to. Use when asked what employees work on a client or account.

Columns:
 - account_id (PK)
 - employee_id (PK)
 - employee_first_name
 - employee_last_name
 - company
"""

crm_client_info_table_desc = """
**Table: `client_contact`**

Maps client companies (accounts) to their primary point of contact and provides related company details. Contains **EXTERNAL CLIENT** information only. **Do NOT use for Bankwell employee data.**

**Relevant Columns for Querying:**

*   `account_id` (INT/VARCHAR, Primary Key): Unique identifier for the client account.
*   `company` (TEXT/VARCHAR): Name of the client company (also referred to as client or account).
*   `industry` (TEXT/VARCHAR): Client's primary industry.
*   `contact_first_name` (TEXT/VARCHAR): First name of the primary contact.
*   `contact_last_name` (TEXT/VARCHAR): Last name of the primary contact. (Combine with `contact_first_name` for full name searches).
*   `contact_title` (TEXT/VARCHAR): Job title of the primary contact.
*   `email` (TEXT/VARCHAR): Email address of the primary contact.
*   `phone` (TEXT/VARCHAR): **Phone number** of the primary contact.
*   `website` (TEXT/VARCHAR): Client company's official website.
*   `location` (TEXT/VARCHAR): City where the client company is primarily located.
*   `annual_revenue` (NUMERIC/DECIMAL): **Bankwell's** total annual revenue generated **from** this client account. (*Note: This is revenue for Bankwell, not the client's total revenue.*)
*   `total_account_bal` (NUMERIC/DECIMAL): Total balance of all accounts held by the client at Bankwell.

**Querying Rules & Constraints:**

1.  **Scope:** Use this table for questions about:
    *   Primary contact details (name, email, phone) for a specific client company.
    *   Finding the company associated with a specific contact person.
    *   Client company details (location, website, Bankwell revenue, total balance, industry).
    *   Recognize terms "client," "company," and "account" as referring to `company` column.
2.  **Filtering:** Users typically query by:
    *   **Company Name:** Match against `company`.
    *   **Contact Full Name:** Match against `contact_first_name` and `contact_last_name`.
    *   **Contact Email:** Match against `email`.
3.  **Matching:** Perform case-insensitive matching for text fields (`company`, `contact_first_name`, `contact_last_name`, `email`, `location`, `industry`).
4.  **Output Columns:** Select columns relevant to the user's query (e.g., if asked for contact email for "Acme Corp", filter by `company`='Acme Corp' and select `email`, `contact_first_name`, `contact_last_name`).

**Key Focus for LLM:**

*   Identify the filter entity (company name, contact name, contact email) from the user query.
*   Construct appropriate `WHERE` clauses, handling full name searches and using case-insensitive comparisons.
*   Distinguish clearly between queries about *clients* (this table) and *Bankwell employees* (use `employees` table).
*   Select the specific output columns requested by the user.
*   Be aware of the specific definition of `annual_revenue` (Bankwell's revenue from the client).

"""

crm_employees_table_desc = """
**Table: `employees`**

Stores profile information for current Bankwell employees. Assume all individuals in this table work at Bankwell.

**Relevant Columns for Querying:**

*   `employee_id` (INT/VARCHAR, Primary Key): Unique employee identifier.
*   `first_name` (TEXT/VARCHAR): Employee's first name.
*   `last_name` (TEXT/VARCHAR): Employee's last name. (Combine with `first_name` for full name searches).
*   `title` (TEXT/VARCHAR): Employee's official job title.
*   `email` (TEXT/VARCHAR): Employee's Bankwell email address.
*   `phone` (TEXT/VARCHAR): Employee's office phone number.
*   `hire_date` (DATE/DATETIME): Date employee joined Bankwell.
*   `department` (TEXT/VARCHAR): Department the employee works in.

**Querying Rules & Constraints:**

1.  **Scope:** Use this table for questions about Bankwell employee details (contact info, role, department, colleagues). Recognize terms like "employee," "coworker," "company worker," "Bankwell," and "our company" as referring to this table's scope.
2.  **Filtering:** Users typically query by:
    *   **Full Name:** Match against `first_name` and `last_name`.
    *   **Job Title:** Match against `title`.
    *   **Email Address:** Match against `email`.
    *   **Phone Number:** Match against `phone`.
    *   **Department:** Match against `department` (e.g., "Who works in the Finance department?", "Who are Jane Doe's colleagues?" - implying same department).
3.  **Matching:** Perform case-insensitive matching for text fields (`first_name`, `last_name`, `title`, `email`, `department`).
4.  **Output Columns:** Select columns relevant to the user's specific query (e.g., if asked for email, return `email`; if asked for title, return `title`; if asked generally about an employee, return name, title, email, phone, department).

**Key Focus for LLM:**

*   Identify the filter criteria from the user query (name, title, email, department, etc.).
*   Construct appropriate `WHERE` clauses, handling full name searches across `first_name` and `last_name`. Use case-insensitive comparisons.
*   For "colleague" or "coworker" queries about a specific person, infer the need to filter by that person's `department`.
*   Select the specific output columns requested or a standard set (name, title, contact info, department) for general queries.
"""

crm_table_description_mapping = {
    'employees': crm_employees_table_desc,
    'portfolio': crm_portfolio_table_desc,
    'fund_detail': crm_fund_details_desc,
    'client_alignment': crm_client_alignment_table_desc,
    'clients_contact': crm_client_info_table_desc
}

#crm_employees_table_desc = """
#Use when query involves employee names, coworkers, company workers, employee titles, employee email, employee location, employee #department  employee phone, workers at bankwell or employees at bankwell. If the query mentions our company, use this table to learn about #the employees. All employees listed here work at bankwell.

#Columns:
# - employee_id (PK)
# - employee_first_name: First name 
# - employee_last_name: Last name 
# - title: corporate title 
# - email: email address 
# - phone: phone number 
# - hire_date: date the employee was hired
# - department: what department the employee works in
#"""




outlook_email_table_desc = """

**Table: `email_data`**

Stores email communications involving Jane Moneypenny (`jane.moneypenny1@outlook.com`).

**Relevant Columns for Querying:**

*   `email_timestamp` (TEXT/VARCHAR): Exact time the email was sent (YYYY-MM-DD HH:MM:SS).
*   `from_name` (TEXT/VARCHAR): Sender's full name.
*   `from_email` (TEXT/VARCHAR): Sender's email address. Jane's is always `jane.moneypenny1@outlook.com`.
*   `to_names` (TEXT/VARCHAR): Recipient(s) full name(s). May contain multiple comma-separated names (e.g., "John Doe, Mary Smith").
*   `to_emails` (TEXT/VARCHAR): Recipient(s) email address(es). May contain multiple comma-separated emails (e.g., "john.doe@example.com, mary.smith@example.com").
*   `email_subject` (TEXT/VARCHAR): The subject line of the email.
*   `email_body` (TEXT/VARCHAR): The core content/message of the email. Assumed to be pre-processed to exclude greetings, sign-offs, and signatures.

**Querying Rules & Constraints:**

1.  **Scope:** Queries target emails **sent by or received by** Jane Moneypenny (`jane.moneypenny1@outlook.com`).
2.  **Client Identification:** User queries will typically identify the other party (client) by **full name** or **email address**.
3.  **Filtering Logic:** Generate SQL to find emails where:
    *   (`from_email` = 'jane.moneypenny1@outlook.com' AND (`to_emails` CONTAINS client_email OR `to_names` CONTAINS client_name))
    *   OR
    *   (`to_emails` CONTAINS 'jane.moneypenny1@outlook.com' AND (`from_email` = client_email OR `from_name` = client_name))
    *   Use case-insensitive matching for emails and names.
    *   Handle potential fuzzy matching for **names** if explicitly requested or implied by the query.
    *   For multi-value fields (`to_names`, `to_emails`), use appropriate containment checks (e.g., `LIKE '%value%'` in SQL).
4.  **Date Range:** By default, restrict results to emails where `email_timestamp` is between `2018-06-01 00:00:00` and `2023-12-31 23:59:59`.
5.  **Ordering:** When "recent," "latest," or similar terms are used, **always** sort results by `email_timestamp` in **descending order**.
6.  **Output Columns:** Select relevant columns based on the query, typically including `email_timestamp`, `from_name`, `from_email`, `to_names`, `to_emails`, `email_subject`, and potentially `email_body`. Ensure `email_timestamp` format is YYYY-MM-DD HH:MM:SS.

**Key Focus for LLM:**

*   Identify Jane's email (`jane.moneypenny1@outlook.com`) and the client identifier (name/email) from the user query.
*   Construct the correct `WHERE` clause incorporating the bidirectional communication logic (Jane sends TO client OR client sends TO Jane).
*   Properly handle checks within potentially multi-value `to_names` and `to_emails` fields.
*   Apply date range filter.
*   Apply `ORDER BY email_timestamp DESC` when recency is requested.
*   Select requested output columns.


"""



outlook_meeting_table_desc = """

**Table: `meeting_data`**

This table contains records of past meetings hosted by Jane Moneypenny.

**Relevant Columns for Querying:**

*   `meeting_timestamp` (TEXT/VARCHAR): The exact date and time of the meeting. **Crucially, assume this timestamp is stored in UTC and needs conversion for ET filtering.** ( *Or specify the actual stored timezone if known, e.g., "already stored in ET"*).
*   `invitees` (TEXT/VARCHAR): Name(s) of external attendees. May contain multiple names. Use for filtering by full name (support fuzzy matching).
*   `invitee_emails` (TEXT/VARCHAR): Email address(es) corresponding to `invitees`. Use for filtering by exact email address.
*   `meeting_subject` (TEXT/VARCHAR): The topic of the meeting.

**Querying Rules & Constraints:**

1.  **Date Range:** Only include meetings where `meeting_timestamp` is between `2018-06-01 00:00:00` and `2023-12-31 23:59:59`.
2.  **Time/Day Filter:**
    *   Only include meetings held Monday through Friday.
    *   Only include meetings held between 9:00 AM (09:00:00) and 5:00 PM (17:00:00) **Eastern Time (ET)**. Remember to handle timezone conversion from the stored timestamp.
3.  **Filtering Criteria:** User queries will provide either:
    *   An **invitee's full name**: Perform a case-insensitive, **fuzzy match** against the `invitees` column (e.g., "Jennifer Phelps" should match "Jenny Phelps", "Jen Phelps", "Jennifer Phelps").
    *   An **invitee's email address**: Perform an exact, case-insensitive match against the `invitee_emails` column.
    *   *Note:* The `invitees` and `invitee_emails` columns might contain multiple entries. The filter should match if the target name/email is present within the column's content.
4.  **Ordering:** Always sort results by `meeting_timestamp` in **descending order** (most recent first).
5.  **Output Columns:** Return **only** these columns in the specified order:
    *   `meeting_timestamp` (Format as YYYY-MM-DD HH:MM:SS)
    *   `invitees`
    *   `invitee_emails`
    *   `meeting_subject`

**Example Goal:**

*   User: "Recent meetings with Jen Phelps"
*   Action: Generate SQL to find meetings matching name "Jen Phelps" (fuzzy), within the date/time/day constraints, ordered descending by timestamp, selecting the four specified output columns.

**Key Focus for LLM:**

*   Translate user requests involving names or emails into appropriate SQL `WHERE` clauses, incorporating fuzzy logic for names and exact matching for emails.
*   Correctly apply the date range, day-of-week, and time-of-day filters (including **ET timezone conversion**).
*   Ensure the `SELECT` clause contains only the required output columns.
*   Always include `ORDER BY meeting_timestamp DESC`.
*   Ignore any mention of the host (Jane Moneypenny) in the query generation logic, as it's a constant.


"""

outlook_table_description_mapping = {
    'email_data': outlook_email_table_desc,
    'meeting_data': outlook_meeting_table_desc
}





#################################
# THE STRINGS BELOW ARE SAMPLES #
# FROM ANOTHER APPLICATION, DO  #
# NOT USE FOR REAL DEVELOPMENT  #
#################################


#table_desc = """\
#This table represents text chunks from an SEC filing. Each row contains the following columns:

#id: id of row
#page_label: page number 
#file_name: top-level file name
#text: all text chunk is here
#embedding: the embeddings representing the text chunk

#For most queries you should perform semantic search against the `embedding` column values, since \
#that encodes the meaning of the text.

#"""


# salesforce_account_table_desc = """

# Use when query involves organizations, industries or clients.
# Columns:
# - expert_name (PK)
# - organization_sector_description
# - accounts


# """


# salesforce_employee_table_desc = """

# Use when query relates to expert identity.
# Columns:
# - salesforce_expert_id (PK)
# - employee_name
# - segment
# - job_title
# - global_region
# - country


# """


# salesforce_matter_table_desc = """

# Use for questions about projects, expertise, experience, or skills.
# Columns:
# - opportunity_id
# - contact_id
# - salesforce_expert_id (FK)
# - account_id (FK)
# - opportunity_narrative_embedding


# """

