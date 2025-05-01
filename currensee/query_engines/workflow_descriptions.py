
from currensee.schema.schema import PostgresTables

crm_table_desc = """


"""



crm_portfolio_table_desc = """
This table lists the investment funds held by client companies through their accounts at our bank. Use this table to identify which funds a specific client owns, and how much is invested in each.

IMPORTANT:
- `company` refers to the client company that owns one or more funds. It is NOT a stock or a mutual fund itself.
- Use this table to answer questions like: "What funds does a client own?" or "What is a company's total portfolio value?"
WARNING: When filtering by fund type (e.g., "Equity funds"), always apply the filter on the `fund_type` column in the `portfolio` table, not in `fund_detail`. The `portfolio` table represents the funds a client owns. The `fund_detail` table only describes what’s inside the fund, not its type.


Columns:
- account_id: Unique identifier for the client's account.
- company: Name of the client company.
- fund_type: Category of the fund (e.g., Equity, Bond).
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
- fund (Foreign Key, portfolio.symbol): Ticker of the fund holding this asset.
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
This workflow describes how to use the client contact table to answer user questions about client information. This table is specifically designed to provide details about the primary point of contact for each client account.

**Use this table when the user's question asks for information related to:**

* The client's primary contact person's **email address**.
* The client's primary contact person's **phone number**.
* The client's primary contact person's **full name**.
* The **city** where the client company is located.
* The client company's **annual revenue**.
* The client company's **website address**.
* Identifying the **email of the point of contact** for a specific client.
* Identifying the **name of the contact person** for a specific client.
* Determining the **company** that a specific contact person represents.

**Key uses of this table include:**

* Identifying the **primary point of contact** for a given client account.
* Finding out **how to contact a client** (via email or phone).

**Important Considerations:**

* **Do not use this table** to answer questions about **Bankwell employees**. This table contains information about external client contacts only.
* The terms **"client," "company," and "account"** can be used interchangeably to refer to the organizations listed in this table.

**Table Columns and their Meanings:**

* `account_id` (Primary Key): A unique identifier for each client account.
* `company`: The name of the client company. This may also be referred to as the client or the account.
* `industry`: The primary industry in which the client company operates.
* `contact_first_name`: The first name of the primary contact person at the client company.
* `contact_last_name`: The last name of the primary contact person at the client company.
* `contact_title`: The job title of the primary contact person at the client company.
* `email`: The email of the primary contact person at the client company.
* `phone`: The email of the primary contact person at the client company.
* `website`: The official website address of the client company.
* `location`: The city in which the client company is primarily located.
* `annual_revenue`: The total annual revenue generated from this client account by Bankwell.
* `total_account_bal`: The total balance of all accounts held by the client at Bankwell.

"""

crm_employees_table_desc = """
This workflow describes how to use the employee information table to answer user questions about individuals working within Bankwell. This table contains details about Bankwell's employees.

**Use this table when the user's question asks for information related to:**

* An **employee's full name**.
* An employee's **job title** or **corporate title**.
* An employee's **email address**.
* An employee's **phone number**.
* An employee's **work location** (implicitly understood as being within Bankwell, though not explicitly listed as a separate column).
* An employee's **department**.
* Identifying **coworkers** or other **employees at Bankwell**.

**Key uses of this table include:**

* Finding contact information for Bankwell employees.
* Identifying an employee's role or department within Bankwell.
* Determining who works in the same department as a specific employee.

**Important Considerations:**

* This table **exclusively contains information about employees who work at Bankwell**. You can assume that any employee mentioned here is a Bankwell employee.
* The terms **"employee," "coworker," "company worker," and "Bankwell employee"** all refer to individuals listed in this table. When a query mentions "our company" or "Bankwell," this is the appropriate table to use.

**Table Columns and their Meanings:**

* `employee_id` (Primary Key): A unique identifier for each Bankwell employee.
* `first_name`: The first name of the Bankwell employee.
* `last_name`: The last name of the Bankwell employee.
* `title`: The official corporate title of the Bankwell employee.
* `email`: The professional email address of the Bankwell employee.
* `phone`: The office phone number of the Bankwell employee.
* `hire_date`: The date when the employee was hired by Bankwell.
* `department`: The specific department in which the Bankwell employee works.

By understanding these columns and the intended use cases, you can effectively translate natural language queries into SQL to retrieve the requested employee information for Bankwell personnel.
"""

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


outlook_table_desc = """

"""



market_table_desc = """


"""

#NOTE: These are just placeholders to demonstrate intended capabilities.

SQL_TABLE_DESC_MAPPING: dict[str, str] = {
    PostgresTables.CRM_TABLE_ONE: crm_table_desc,
    PostgresTables.OUTLOOK_EMAILS: outlook_table_desc, 
    PostgresTables.CRM_Client_Alignment: crm_client_alignment_table_desc,
    PostgresTables.CRM_Portfolio: crm_portfolio_table_desc ,
    PostgresTables.CRM_Employees: crm_employees_table_desc, 
    PostgresTables.CRM_Clients_Contact: crm_client_info_table_desc,
    PostgresTables.CRM_Fund_Detail: crm_fund_details_desc
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

