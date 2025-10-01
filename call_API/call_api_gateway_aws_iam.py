import boto3
import requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

# AWS Credentials
access_key = "ssss"
secret_key = "ssss"
region = "eu-west-1"
service = "execute-api"

# API Endpoint
url = "https://api.dev-apvm.awsdev.boehringer.com/db/accounts_to_close"
headers = {
    "Content-Type": "application/json",
    "x-amz-date": "20251001T103802Z"
}

# Create AWSRequest
request = AWSRequest(method="GET", url=url, headers=headers)
SigV4Auth(boto3.Session().get_credentials(), service, region).add_auth(request)

# Send the request with SSL verification disabled
response = requests.get(url, headers=dict(request.headers), verify=False)
print(response.status_code, response.text)