
from currensee.schema.schema import PostgresTables


crm_table_desc = """




"""



outlook_table_desc = """






"""



market_table_desc = """






"""

#NOTE: These are just placeholders to demonstrate intended capabilities.

SQL_TABLE_DESC_MAPPING: dict[str, str] = {
    PostgresTables.CRM_TABLE_ONE: crm_table_desc,
    PostgresTables.OUTLOOK_EMAILS: outlook_table_desc
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

