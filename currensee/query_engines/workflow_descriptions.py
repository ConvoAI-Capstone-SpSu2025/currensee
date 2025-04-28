
from currensee.schema.schema import PostgresTables

crm_table_desc = """


"""

crm_portfolio_table_desc = """
Use when query involves client accounts, portfolio information, positions, stocks, mutual funds, index funds, positions, portfolio makeup, or holdings.
Columns:
 - account_id (PK)
 - company_name
 - symbol (PK)
 - instrument_type
"""

crm_client_alignment_table_desc = """
Use when query involves which clients are assigned to a bank employee, what other employees a client has spoken to, what is the email of the point of contact for a client, what is the name of the contact for a client, or what company a client represents. 

Columns:
 - account_id (PK)
 - employee_id (PK)
 - employee_first_name
 - employee_last_name
 - company
 - industry
 - contact_first_name
 - contact_last_name
 - contact_email
 - contact_title
 - contact_phone
"""

crm_client_info_table_desc = """
Use when query involves clients total balance, client location, client revenue, or client company website.
Columns:
 - account_id (PK)
 - company
 - industry
 - contact_first_name
 - contact_last_name
 - contact_title
 - website
 - location
 - annual_revenue
 - total_account_bal
"""


crm_employees_table_desc = """
Use when query involves employee names, coworkers, company workers, employee titles, employee email, employee location, employee department  employee phone, or employees at bankwell. If the query mentions our company, use this table to learn about the employees.

Columns:
 - employee_id (PK)
 - employee_first_name: First name 
 - employee_last_name: Last name 
 - title: corporate title 
 - email: email address 
 - phone: phone number 
 - hire_date: date the employee was hired
 - department: what department the employee works in

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
    PostgresTables.CRM_Employees: crm_employees_table_desc, 
    PostgresTables.CRM_Clients_Contact: crm_client_info_table_desc
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

