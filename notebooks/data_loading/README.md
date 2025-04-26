# Instrctions for using the cloud sql database:

1. Find the external IP of your JupyterLab VM 
https://console.cloud.google.com/compute/instances?project=adsp-34002-on02-sopho-scribe&authuser=1

    Go to VM Instances
    Find your JupyterLab VM
    Copy the External IP address (looks like 34.91.100.45).
2. Add the VM's IP to your Cloud SQL authorized networks 
https://console.cloud.google.com/sql/instances/currensee-sql/connections/networking?authuser=1&project=adsp-34002-on02-sopho-scribe

    Go to Cloud SQL instances.
    Click your instance.
    Click Connections in the left sidebar.
    Scroll to Authorized networks → Add network.
    Name: anything like jupyterlab-vm
    Network: paste the external IP you just copied (e.g., 34.91.100.45/32)
    IMPORTANT: Add /32 to allow only that single IP.
    Click Save.

# Please use the 'secret access' for uploading data instead of hard coding credentials


You can see what branch you are on by looking at the cloud gui 

For example:

    def access_secret(secret_id):
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(name=name)
        return response.payload.data.decode("UTF-8")
    
    PROJECT_ID = 'adsp-34002-on02-sopho-scribe'
    REGION = 'us-central1'
    DB_NAME = 'crm'
    DB_USER = access_secret('cloudSqlUser')
    DB_PASSWORD = access_secret('cloudSqlUserPassword')
    DB_HOST = '35.232.92.211'
    DB_PORT = '5432'

    engine = create_engine(
        f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}',
        connect_args={'sslmode': 'require'}
    )
    
Note - I had to run in the Python 3 kernel environment to use the google cloud secret manager