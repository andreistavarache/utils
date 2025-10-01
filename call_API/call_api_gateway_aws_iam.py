import datetime
import hashlib
import hmac
import requests
import os

HOST = "api.dev-apvm.awsdev.boehringer.com"
PATH = "/db/accounts_to_close"
METHOD = "POST"  # Change to POST if required
REGION = "eu-west-1"

# AWS access keys
access_key = os.environ['AWS_ACCESS_KEY_ID']  
secret_key = os.environ['AWS_SECRET_ACCESS_KEY']
session_token = os.environ['AWS_SESSION_TOKEN']

# Request parameters
method = METHOD
service = 'execute-api'
host = HOST
region = REGION
endpoint = PATH

# Create a datetime object for signing
t = datetime.datetime.utcnow()
amzdate = t.strftime('%Y%m%dT%H%M%SZ')
datestamp = t.strftime('%Y%m%d') 

# Payload (if required)
payload = '{"body":{"skip_data_gathering":false,"skip_suspending":false,"skip_closing":true,"DryRun":true}}'
payload_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()

# Create the canonical request
canonical_uri = endpoint
canonical_querystring = ''  # Add query params if required
canonical_headers = 'host:' + host + '\n'
signed_headers = 'host'
canonical_request = (method + '\n' + canonical_uri + '\n' + canonical_querystring + '\n'
                     + canonical_headers + '\n' + signed_headers + '\n' + payload_hash)

# Create the string to sign
algorithm = 'AWS4-HMAC-SHA256'
credential_scope = datestamp + '/' + region + '/' + service + '/' + 'aws4_request'
string_to_sign = (algorithm + '\n' +  amzdate + '\n' +  credential_scope + '\n' +  
                  hashlib.sha256(canonical_request.encode('utf-8')).hexdigest())

def sign(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

def getSignatureKey(key, dateStamp, regionName, serviceName):
    kDate = sign(("AWS4" + key).encode("utf-8"), dateStamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, "aws4_request")
    return kSigning

# Sign the string    
signing_key = getSignatureKey(secret_key, datestamp, region, service)
signature = hmac.new(signing_key, (string_to_sign).encode('utf-8'), hashlib.sha256).hexdigest()

# Add signing information to the request
authorization_header = (algorithm + ' ' + 'Credential=' + access_key + '/' + credential_scope + ', ' +  
                        'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature)

# Make the request
headers = {
    'Host': host,
    'x-amz-date': amzdate,
    'x-amz-security-token': session_token,
    'Authorization': authorization_header,
    'Content-Type': 'application/json'  # Add if required
}
request_url = 'https://' + host + canonical_uri
response = requests.post(request_url, headers=headers, data=payload, timeout=5, verify=False)  # Change to POST if required
response.raise_for_status()

print(response.text)