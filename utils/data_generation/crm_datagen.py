import pandas as pd
import random
import os
import re
from faker import Faker

# Initialize Faker instance
#Lily's modification of CRM data
#Faker is a Python package that integrates fake data for you.

#Some hard coded data of publicly traded companies to be our mock clients

fake = Faker()

# Helper function to generate synthetic employee data
def generate_employee_data(num_employees=10, ourcompany_name = 'bankwell'):
    Company = ourcompany_name
    employees = [
        {
            'EmployeeID': fake.unique.uuid4(),
            'FirstName': "Jane",
            'LastName': "Moneypenny",
            'Title': "Relationship Manager",
            'Email': "jane.moneypenny1@bankwell.com",
            'Phone': fake.phone_number(),
            'HireDate': fake.date_this_decade(),
            'Department': 'Enterprise Investment',
            'Market': 'San Fransisco'
        }
    ]

    for _ in range(num_employees-1):
      EmployeeID = fake.unique.uuid4()
      FirstName = fake.first_name()
      LastName = fake.last_name()
      Title = random.choice(['Finance Assistant', 'Financial Advisor', 'Senior Relationship Manager', 'Product Specialist', 'Relationship Manager'])
      Phone = fake.phone_number()
      Department = random.choice(['Enterprise Investment', 'Small Business Investment', 'Operations', 'Sales', 'Customer Support'])
      HireDate = fake.date_this_decade()
      Market = random.choice(['San Fransisco', 'New York City', 'Boston', 'Denver', 'Los Angeles', 'Miami', 'Washington DC', 'Seattle', 'Dallas', 'Chicago'])
      Company_clean = re.sub(r'\W+', '', Company).lower()
      Email = f"{FirstName.lower()}.{LastName.lower()}@{Company_clean}.com"


      employees.append({
            'EmployeeID': EmployeeID,
            'FirstName': FirstName,
            'LastName': LastName,
            'Title': Title,
            'Email': Email,
            'Phone': Phone,
            'HireDate': HireDate,
            'Department': Department,
            'Market': Market
        })
    return pd.DataFrame(employees)

# Helper function to generate point of contact and info for a Company
def generate_point_of_contact(Company_name):
    AccountID = fake.unique.uuid4()
    FirstName = fake.first_name()
    LastName = fake.last_name()
    ContactTitle = random.choice(["Senior Director", "Manager", "Director", "VP", "Consultant"])
    Phone = fake.phone_number()
    Website = fake.url()
    Location = random.choice(['San Fransisco', 'New York City', 'Boston', 'Denver', 'Los Angeles', 'Miami', 'Washington DC', 'Seattle', 'Dallas', 'Chicago'])
    AnnualRevenue = random.randint(1000000, 50000000)
    TotalAccountBal = random.randint(1000000, 50000000)

    # Clean Company name for use in email
    Company_clean = re.sub(r'\W+', '', Company_name).lower()
    Email = f"{FirstName.lower()}.{LastName.lower()}@{Company_clean}.com"

    return {
        "AccountID": AccountID,
        "ContactFirstName": FirstName,
        "ContactLastName": LastName,
        "ContactTitle": ContactTitle,
        "Phone": Phone,
        "Email": Email,
        "Website": Website,
        "Location": Location,
        "AnnualRevenue": AnnualRevenue,
        "TotalAccountBal": TotalAccountBal
    }


def generate_account_data(num_accounts=5, clients_company = []):
# Build the data
  accounts = []
  for company in clients_company:
      contact = generate_point_of_contact(company["Company"])
      record = {
          "Company": company["Company"],
          "industry": company["industry"],
          **contact
      }
      accounts.append(record)
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
                'EmployeeFirstName': employee['FirstName'],
                'EmployeeLastName': employee['LastName'],
                'AccountID': account,
                'Company': accounts_df.loc[accounts_df['AccountID'] == account, 'Company'].iloc[0],
                'Industry': accounts_df.loc[accounts_df['AccountID'] == account, 'industry'].iloc[0],
                'ContactFirstName': accounts_df.loc[accounts_df['AccountID'] == account, 'ContactFirstName'].iloc[0],
                'ContactLastName': accounts_df.loc[accounts_df['AccountID'] == account, 'ContactLastName'].iloc[0],
                'ContactEmail': accounts_df.loc[accounts_df['AccountID'] == account, 'Email'].iloc[0],
                'ContactTitle': accounts_df.loc[accounts_df['AccountID'] == account, 'ContactTitle'].iloc[0],
                'ContactPhone': accounts_df.loc[accounts_df['AccountID'] == account, 'Phone'].iloc[0],
            })
    return pd.DataFrame(relationships)


def generate_portfolios(df_accounts, max_positions=10, instruments=[]):
    portfolio_records = []

    for _, row in df_accounts.iterrows():
        AccountId = row["AccountID"]
        Company = row["Company"]
        num_positions = random.randint(5, 10)
        positions = random.sample(instruments, num_positions)
        for symbol, instrument_type in positions:
            portfolio_records.append({
                "AccountID": AccountId,
                "Company_name": Company,
                "symbol": symbol,
                "instrument_type": instrument_type
            })

    return pd.DataFrame(portfolio_records)


if __name__ == "__main__":
    
    clients_company_info = [
        {"Company": "Broadcom", "industry": "Technology"},
        {"Company": "Cisco", "industry": "Technology"},
        {"Company": "Palantir Technologies", "industry": "Technology"},
        {"Company": "Fiserv", "industry": "Technology"},
        {"Company": "Atlassian", "industry": "Technology"},
        {"Company": "Leidos", "industry": "Technology"},
        {"Company": "Duolingo", "industry": "Technology"},
        {"Company": "Logitech", "industry": "Technology"},
        {"Company": "Celestica", "industry": "Technology"},
        {"Company": "Dropbox", "industry": "Technology"},
        {"Company": "Plexus", "industry": "Technology"},
        {"Company": "Silicon Laboratories", "industry": "Technology"},
        {"Company": "Mobix Labs", "industry": "Technology"},
        {"Company": "Mariott", "industry": "Hospitality"},
        {"Company": "InterContinental Hotels Group", "industry": "Hospitality"},
        {"Company": "Sonder Holdings", "industry": "Hospitality"},
        {"Company": "Hyatt Hotels", "industry": "Hospitality"},
        {"Company": "Royal Caribbean Cruises", "industry": "Hospitality"},
        {"Company": "UnitedHealth", "industry": "Healthcare"},
        {"Company": "Johnson & Johnson", "industry": "Healthcare"},
        {"Company": "AbbVie", "industry": "Healthcare"},
        {"Company": "Novo Nordisk", "industry": "Healthcare"},
        {"Company": "Abbott Laboratories", "industry": "Healthcare"},
        {"Company": "AstraZeneca", "industry": "Healthcare"},
        {"Company": "Merck & Co", "industry": "Healthcare"},
        {"Company": "Intuitive Surgical", "industry": "Healthcare"},
        {"Company": "Medtronic", "industry": "Healthcare"},
        {"Company": "Zoetis", "industry": "Healthcare"},
        {"Company": "Humana", "industry": "Healthcare"},
        {"Company": "Illumina", "industry": "Healthcare"},
        {"Company": "Guardant Health", "industry": "Healthcare"},
        {"Company": "Rhythm Pharmaceuticals", "industry": "Healthcare"},
        {"Company": "Amedisys", "industry": "Healthcare"},
        {"Company": "Rivian Automotive", "industry": "Automotive"},
        {"Company": "Fordy", "industry": "Automotive"},
        {"Company": "lululemon athletica", "industry": "Retail"},
        {"Company": "DICK'S Sporting Goods", "industry": "Retail"},
        {"Company": "GameStop Corp", "industry": "Retail"},
        {"Company": "Texas Roadhouse", "industry": "Retail"},
        {"Company": "Hasbro", "industry": "Retail"},
        {"Company": "Mattel", "industry": "Retail"},
        {"Company": "Wayfair", "industry": "Retail"},
        {"Company": "Peloton", "industry": "Retail"},
        {"Company": "Sally Beauty", "industry": "Retail"},
        {"Company": "Lifetime Brand", "industry": "Retail"},
        {"Company": "Allbirds", "industry": "Retail"},
        {"Company": "Walmart", "industry": "Retail"},
        {"Company": "Tyson Foods", "industry": "Retail"},
        {"Company": "Sprouts Farmers Market", "industry": "Retail"},
        {"Company": "Dollar Tree", "industry": "Retail"},
        {"Company": "Stride", "industry": "Retail"},
        {"Company": "Spectrum Brands", "industry": "Retail"},
        {"Company": "Udemy", "industry": "Retail"},
        {"Company": "Vital Farms", "industry": "Retail"},
        {"Company": "Graham Holdings Company", "industry": "Retail"},
        {"Company": "Hims & Hers Health", "industry": "Retail"},
        {"Company": "Smithfield Foods", "industry": "Retail"},
        {"Company": "Albertsons Companies", "industry": "Retail"},
        {"Company": "Albany International", "industry": "Manufacturing"},
        {"Company": "IT Tech Packaging", "industry": "Manufacturing"},
        {"Company": "Lockheed Martin Corporation", "industry": "Manufacturing"},
        {"Company": "Landstar System", "industry": "Manufacturing"},
        {"Company": "Hexcel Corporation", "industry": "Manufacturing"},
        {"Company": "AeroVironment", "industry": "Manufacturing"},
        {"Company": "Matson", "industry": "Manufacturing"},
        {"Company": "McGrath RentCorp", "industry": "Manufacturing"},
        {"Company": "Mueller Industries", "industry": "Manufacturing"},
        {"Company": "Dolby Laboratories", "industry": "Manufacturing"},
        {"Company": "ManpowerGroup", "industry": "Manufacturing"},
        {"Company": "Welltower", "industry": "RealEstate"},
        {"Company": "Iron Mountain Incorporated", "industry": "RealEstate"},
        {"Company": "Camden Property", "industry": "RealEstate"},
        {"Company": "CubeSmart", "industry": "RealEstate"},
        {"Company": "Federal Realty Investment Trust", "industry": "RealEstate"},
        {"Company": "Essential Properties Realty", "industry": "RealEstate"},
        {"Company": "Compass", "industry": "RealEstate"},
        {"Company": "Medical Properties Trust", "industry": "RealEstate"},
        {"Company": "Broadstone", "industry": "RealEstate"},
        {"Company": "Ladder Capital Corp", "industry": "RealEstate"},
        {"Company": "Peakstone Realty Trus", "industry": "RealEstate"},
        {"Company": "Fathom Holdings", "industry": "RealEstate"},
        {"Company": "Presidio Property Trust", "industry": "RealEstate"},
        {"Company": "Service Properties Trust", "industry": "RealEstate"},
    ]

    stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'JPM', 'V', 'UNH']
    bonds = ['US10Y', 'US30Y', 'CORP1', 'CORP2', 'MUNI1', 'MUNI2']
    mutual_funds = ['VFIAX', 'SWPPX', 'FXAIX', 'VTSAX', 'FZROX', 'SPY']
    # All symbols with types
    instruments = (
        [(sym, 'Stock') for sym in stocks] +
        [(sym, 'Bond') for sym in bonds] +
        [(sym, 'Mutual Fund') for sym in mutual_funds]
    )

    # Generate synthetic data for the tables
    employees_df = generate_employee_data(num_employees=100, ourcompany_name = 'bankwell')
    accounts_df = generate_account_data(num_accounts=500, clients_company = clients_company_info)
    opportunities_df = generate_opportunity_data(accounts_df, num_opportunities_per_account=3)
    contacts_df = generate_employee_contact_data(employees_df, accounts_df, num_relationships_per_employee=30)
    portfolio_df = generate_portfolios(accounts_df, max_positions=10, instruments = instruments)

    # Print the first few rows of each DataFrame
    print("Employees Data:")
    print(employees_df.head())

    print("\nAccounts Data:")
    print(accounts_df.head())

    print("\nOpportunities Data:")
    print(opportunities_df.head())

    print("\nEmployee-Contact Relationships Data:")
    print(contacts_df.head())
    
    print("\nPortfolio Info for Each Account")
    print(portfolio_df.head())

    out_dir = os.path.dirname(os.path.abspath(__file__))

    employees_path = os.path.join(out_dir, "../../data/crm/employees.csv")
    employees_df.to_csv(employees_path)

    accounts_path = os.path.join(out_dir, "../../data/crm/accounts.csv")
    accounts_df.to_csv(accounts_path)

    opportunities_path = os.path.join(out_dir, "../../data/crm/opportunities.csv")
    opportunities_df.to_csv(opportunities_path)

    contacts_path = os.path.join(out_dir, "../../data/crm/contacts.csv")
    contacts_df.to_csv(contacts_path)
    
    portfolio_path = os.path.join(out_dir, "../../data/crm/portfolio.csv")
    portfolio_df.to_csv(portfolio_path)

    # Identify the contacts specifically assigned to Jane and produce CSV to create synthetic email
    # correspondence and events
    janes_id = employees_df[employees_df['LastName'] == 'Moneypenny'].iloc[0]['EmployeeID']
    contacts_accounts_df = contacts_df.merge(accounts_df, on='AccountID', how='left')
    janes_contacts_accounts_df = contacts_accounts_df[contacts_accounts_df['EmployeeID'] == janes_id]
    janes_contacts_path = os.path.join(out_dir, "../../data/crm/janes_contacts.csv")
    janes_contacts_accounts_df.to_csv(janes_contacts_path)