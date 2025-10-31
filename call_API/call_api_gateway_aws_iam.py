#!/usr/bin/env python3
import boto3
import os
import json
import requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest


def call_signed_api_local(
    endpoint: str,
    payload: dict,
    region: str = "eu-west-1",
    method: str = "POST",
    api_host: str = "https://api.dev-apvm.awsdev.boehringer.com/",
    cert_path: str = "/home/stava/Errors/utils/call_API/ca-bundle.trust.crt",  # 👈 replace with your path
):
    """
    Call a SigV4-signed API using local AWS credentials (from env or AWS CLI config).
    """
    print("=== Starting local signed API test ===")
    print(f"API host: {api_host}")
    print(f"Endpoint: {endpoint}")
    print(f"Certificate path: {cert_path}")
    print(f"Region: {region}")

    # Create a session using your exported credentials
    session = boto3.session.Session()
    credentials = session.get_credentials().get_frozen_credentials()

    print("Loaded credentials from environment or AWS CLI config")

    headers = {"Content-Type": "application/json"}

    url = f"{api_host.rstrip('/')}/{endpoint.lstrip('/')}"
    print(f"Final URL: {url}")

    request = AWSRequest(
        method=method,
        url=url,
        data=json.dumps(payload),
        headers=headers,
    )

    # Sign the request using SigV4
    SigV4Auth(credentials, "execute-api", region).add_auth(request)

    print("Signed headers:")
    for k, v in request.headers.items():
        print(f"  {k}: {v}")

    # Make the request
    try:
        print("\n=== Sending HTTPS request ===")
        response = requests.request(
            method=method,
            url=request.url,
            headers=dict(request.headers),
            data=request.body,
            verify=cert_path,  # local CA or bundle
            timeout=30,
        )

        print(f"Status code: {response.status_code}")
        print(f"Response headers:\n{json.dumps(dict(response.headers), indent=2)}")

        if response.text:
            print(f"Response body:\n{response.text}")

        response.raise_for_status()
        return response.json()

    except requests.exceptions.SSLError as e:
        print(f"\n❌ SSL Error:\n{e}")
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request Error:\n{e}")


if __name__ == "__main__":
    # Example usage
    payload = {"DryRun": True}
    endpoint = "/db/get_accounts_to_suspend"

    # You can override these via environment variables
    api_host = os.environ.get("API_HOST_NAME", "https://api.dev-apvm.awsdev.boehringer.com/")
    cert_path = os.environ.get("LOCAL_CERT_PATH", "/path/to/local/cert/ca-bundle.trust.crt")

    call_signed_api_local(
        endpoint=endpoint,
        payload=payload,
        region="eu-west-1",
        api_host=api_host,
        cert_path=cert_path,
    )