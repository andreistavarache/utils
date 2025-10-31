#!/usr/bin/env python3
import boto3
import os
import json
import requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest


def call_api_local(
    endpoint: str,
    payload: dict,
    region: str = "eu-west-1",
    method: str = "POST",
    api_host: str = "https://api.dev-apvm.awsdev.boehringer.com/",
    cert_path: str = None,  # 👈 replace with your path
):
    """
    Call a SigV4-signed API using local AWS credentials (from env or AWS CLI config).
    """
    print("\n=== Starting local API call ===")
    print(f"API host 👉: {api_host}")
    print(f"Endpoint 👉: {endpoint}")
    verify_option = cert_path if cert_path else False
    if verify_option:
        print(f"Certificate path 👉: {cert_path}")
    else:
        print("❌ Call without a certificate!")
    print(f"Region 👉: {region}")

    # Create a session using your exported credentials (you have to get them from SSO and export them first)
    session = boto3.session.Session()
    credentials = session.get_credentials().get_frozen_credentials()

    headers = {"Content-Type": "application/json"}
    url = f"{api_host.rstrip('/')}/{endpoint.lstrip('/')}"
    print(f"\nFinal URL: {url}")

    # The code instantiates an AWSRequest object, which is likely from the botocore library (AWS's low-level Python SDK).
    # This object encapsulates all the information needed to make an authenticated request to an AWS API.
    aws_request_object = AWSRequest(
        method=method,
        url=url,
        data=json.dumps(payload),
        headers=headers,
    )

    # Sign the request using SigV4
    SigV4Auth(credentials, "execute-api", region).add_auth(aws_request_object)

    print("\nSigned headers👇")
    for k, v in aws_request_object.headers.items():
        print(f"  {k}: {v}")

    # Make the request
    try:
        print("\n ⌛ Sending HTTPS request...")
        response = requests.request(
            method=method,
            url=aws_request_object.url,
            headers=dict(aws_request_object.headers),
            data=aws_request_object.body,
            verify=verify_option,
            timeout=30,
        )

        print(f"Status code🗽 {response.status_code}")
        print(f"Response headers:\n{json.dumps(dict(response.headers), indent=2)}")

        if response.text:
            try:
                response_json = response.json()

            # If the API returns an envelope with a JSON string in "body", decode it so it's pretty-printed
                if isinstance(response_json, dict) and isinstance(response_json.get("body"), str):
                    try:
                        parsed_body = json.loads(response_json["body"])
                        response_json["body"] = parsed_body
                    except json.JSONDecodeError:
                        pass

                print(f"Response body:\n{json.dumps(response_json, indent=2)}")
            except json.JSONDecodeError:
                print(f"Response body (non-JSON):\n{response.text}")

        response.raise_for_status()
        return response.json()

    except requests.exceptions.SSLError as e:
        print(f"\n❌ SSL Error:\n{e}")
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request Error:\n{e}")


if __name__ == "__main__":
    # Example usage
    payload = {"DryRun": "false"}
    endpoint = "/db/get_accounts_to_suspend"

    # You can override these via environment variables
    api_host = os.environ.get("API_HOST_NAME", "https://api.prod-apvm.aws.boehringer.com/")
    # Set your certificate path here if needed 👇
    cert_path = None  

    call_api_local(
        endpoint=endpoint,
        payload=payload,
        region="eu-west-1",
        api_host=api_host,
        cert_path=cert_path,
    )