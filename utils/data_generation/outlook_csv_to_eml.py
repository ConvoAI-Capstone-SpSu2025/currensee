import csv
import os
from datetime import datetime
from email.message import EmailMessage
from email.utils import formatdate, make_msgid

curr_dir = os.path.dirname(os.path.abspath(__file__))

data_dir = os.path.join(curr_dir, "../../data/outlook")
out_dir = os.path.join(data_dir, "eml_files")
csv_fp = os.path.join(data_dir, "bankwell_synthetic_emails.csv")

# Create output directory if it doesn't exist
os.makedirs(out_dir, exist_ok=True)


def format_timestamp(ts_str):
    # Assumes timestamp is in ISO 8601 or similar format
    dt = datetime.fromisoformat(ts_str)
    return formatdate(dt.timestamp(), localtime=True)


with open(csv_fp, newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        msg = EmailMessage()

        msg["Subject"] = row["Subject"]
        msg["From"] = row["From"]
        msg["To"] = row["To"]
        msg["Date"] = format_timestamp(row["Timestamp"])
        msg["Message-ID"] = make_msgid(domain="outlook.com")  # Customizable

        # Optional headers
        msg["X-Thread-ID"] = row["ThreadID"]
        msg.set_content(row["Body"])

        # File name using EmailID
        filename = f"{row['EmailID']}.eml"
        filepath = os.path.join(out_dir, filename)

        with open(filepath, "wb") as f:
            f.write(bytes(msg))

print(f"All emails exported to {out_dir}/")
