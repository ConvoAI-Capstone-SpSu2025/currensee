import pandas as pd
import random
import os
from faker import Faker

# Initialize Faker instance
fake = Faker()

# Helper function to generate synthetic employee data
def generate_employee_data(num_employees=10):
    employees = []
    for _ in range(num_employees):
        employees.append({
            'EmployeeID': fake.unique.uuid4(),
            'FirstName': fake.first_name(),
            'LastName': fake.last_name(),
            'Title': random.choice(['Consultant', 'Manager', 'Senior Consultant', 'Director']),
            'Email': fake.email(),
            'Phone': fake.phone_number(),
            'HireDate': fake.date_this_decade(),
            'Department': random.choice(['Finance', 'Marketing', 'Operations', 'Sales', 'Consulting']),
        })
    return pd.DataFrame(employees)

# Helper function to generate synthetic account data
def generate_account_data(num_accounts=5):
    accounts = []
    for _ in range(num_accounts):
        accounts.append({
            'AccountID': fake.unique.uuid4(),
            'CompanyName': fake.company(),
            'Industry': random.choice(['Finance', 'Healthcare', 'Technology', 'Retail', 'Education']),
            'AnnualRevenue': random.randint(1000000, 50000000),
            'Location': fake.city(),
            'Phone': fake.phone_number(),
            'Website': fake.url(),
        })
    return pd.DataFrame(accounts)

# Helper function to generate synthetic opportunity data
def generate_opportunity_data(accounts_df, num_opportunities_per_account=3):
    opportunities = []
    for _, account in accounts_df.iterrows():
        num_opportunities = random.randint(1, num_opportunities_per_account)
        for _ in range(num_opportunities):
            opportunities.append({
                'OpportunityID': fake.unique.uuid4(),
                'AccountID': account['AccountID'],
                'OpportunityName': fake.bs(),
                'Stage': random.choice(['Prospecting', 'Qualification', 'Proposal', 'Negotiation', 'Won', 'Lost', 'Closed']),
                'Type': random.choice(['New Business', 'Existing Business', 'Renewal', 'Upsell']),
                'CloseDate': fake.date_this_year(),
                'Amount': random.randint(50000, 500000),
            })
    return pd.DataFrame(opportunities)

# Helper function to generate synthetic employee-contact relationship data
def generate_employee_contact_data(employees_df, accounts_df, num_relationships_per_employee=2):
    relationships = []
    for _, employee in employees_df.iterrows():
        num_relationships = random.randint(1, num_relationships_per_employee)
        for _ in range(num_relationships):
            account = random.choice(accounts_df['AccountID'].tolist())
            relationships.append({
                'EmployeeID': employee['EmployeeID'],
                'AccountID': account,
                'ContactName': fake.name(),
                'ContactTitle': random.choice(['CEO', 'Manager', 'Director', 'VP', 'Consultant']),
                'ContactEmail': fake.email(),
                'ContactPhone': fake.phone_number(),
            })
    return pd.DataFrame(relationships)


if __name__ == "__main__":

    # Generate synthetic data for the tables
    employees_df = generate_employee_data(num_employees=10)
    accounts_df = generate_account_data(num_accounts=5)
    opportunities_df = generate_opportunity_data(accounts_df, num_opportunities_per_account=3)
    contacts_df = generate_employee_contact_data(employees_df, accounts_df, num_relationships_per_employee=5)

    # Print the first few rows of each DataFrame
    print("Employees Data:")
    print(employees_df.head())

    print("\nAccounts Data:")
    print(accounts_df.head())

    print("\nOpportunities Data:")
    print(opportunities_df.head())

    print("\nEmployee-Contact Relationships Data:")
    print(contacts_df.head())

    out_dir = os.path.dirname(os.path.abspath(__file__))

    employees_path = os.path.join(out_dir, "../../data/employees.csv")
    employees_df.to_csv(employees_path)

    accounts_path = os.path.join(out_dir, "../../data/accounts.csv")
    accounts_df.to_csv(accounts_path)

    opportunities_path = os.path.join(out_dir, "../../data/opportunities.csv")
    opportunities_df.to_csv(opportunities_path)

    contacts_path = os.path.join(out_dir, "../../data/contacts.csv")
    contacts_df.to_csv(contacts_path)