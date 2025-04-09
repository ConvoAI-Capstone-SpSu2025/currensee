"""
NOTE: This is a work in progress!

"""

import faker
import datetime
import random

# Initialize Faker for generating synthetic names
fake = faker.Faker()

# Set parameters
total_weeks = (datetime(2025, 12, 31) - datetime.now()).days // 7
meetings_per_week = 7
total_meetings = total_weeks * meetings_per_week

# Generate a list of synthetic client names
client_names = [fake.name() for _ in range(100)]

# Reset meetings list
meetings = []

# Generate meeting schedule with at least 7 meetings per week
current_date = datetime.now("cst")
for week in range(total_weeks):
    for i in range(meetings_per_week):
        meeting_type = random.choice(["internal", "external"])
        
        if meeting_type == "internal":
            title, description = random.choice(internal_meetings)
        else:
            title, description = random.choice(external_meetings)
            client_name = random.choice(client_names)
            # Add client name to title or description
            if random.random() < 0.5:
                title = f"{title} - {client_name}"
            else:
                description = f"{description} (Client: {client_name})"
        
        # Select a random day in the current week (Mon-Fri)
        weekday = random.randint(0, 4)
        meeting_date = current_date + timedelta(days=(week * 7 + weekday))
        meeting_date = meeting_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Generate random time within business hours
        start_hour = random.randint(8, 16)
        start_minute = random.choice([0, 15, 30, 45])
        duration_minutes = random.choice([30, 45, 60])
        
        start_time = meeting_date.replace(hour=start_hour, minute=start_minute)
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        meetings.append({
            "Subject": title,
            "Start Date": start_time.strftime("%Y-%m-%d"),
            "Start Time": start_time.strftime("%H:%M"),
            "End Date": end_time.strftime("%Y-%m-%d"),
            "End Time": end_time.strftime("%H:%M"),
            "Location": "Microsoft Teams Meeting",
            "Description": description
        })

# Create DataFrame and save to CSV
df_updated = pd.DataFrame(meetings)
updated_csv_path = "/mnt/data/consultant_meetings_schedule_updated.csv"
df_updated.to_csv(updated_csv_path, index=False)

updated_csv_path
