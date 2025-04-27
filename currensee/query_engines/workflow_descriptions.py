
from currensee.schema.schema import PostgresTables

crm_table_desc = """






"""

crm_portfolio_table_desc = """
Use when query involves client accounts, portfolio information, account positions, stocks, mutual funds, or index funds.  
Columns:
 - AccountID (PK)
 - Company_name
 - symbol (PK)
 - instrument_type
"""

crm_client_alignment_table_desc = """
Use when query involves which clients are assigned to a bank employee, what other employees a client has spoken to, what is the email of the point of contact for a client, what is the name of the contact for a client, or what company a client represents.
Columns:
 - AccountID (PK)
 - EmployeeID
 - EmployeeFirstName
 - EmployeeLastName
 - Company
 - Industry
 - ContactFirstName
 - ContactLastName
 - ContactEmail
 - ContactTitle
 - ContactPhone
"""


crm_employees_table_desc = """
Use when query involves what employee names, employee titles, employee email, employee location, employee department or employee phone.
Columns:
 - EmployeeID (PK)
 - EmployeeFirstName
 - EmployeeLastName
 - Title
 - Email
 - Phone
 - HireDate
 - Department
"""


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
    PostgresTables.CRM_Employees: crm_employees_table_desc
}

#################################
# THE STRINGS BELOW ARE SAMPLES #
# FROM ANOTHER APPLICATION, DO  #
# NOT USE FOR REAL DEVELOPMENT  #
#################################

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

