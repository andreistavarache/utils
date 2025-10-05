import os
import boto3
import json
import logger

SSM = boto3.client("ssm")
SSO_ADMIN_CLIENT = get_admin_client("sso-admin")
INSTANCE_ARN = os.environ.get("SSO_INSTANCE_ARN")
client = boto3.client("sts")

def get_admin_client(client_name):
    credentials = client.assume_role(
        RoleArn=os.environ.get("SSO_ROLE_BILLING_ACCOUNT"),
        RoleSessionName="sso_api_session",
    )

    ACCESS_KEY = credentials["Credentials"]["AccessKeyId"]
    SECRET_KEY = credentials["Credentials"]["SecretAccessKey"]
    SESSION_TOKEN = credentials["Credentials"]["SessionToken"]

    return boto3.client(
        client_name,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        aws_session_token=SESSION_TOKEN,
    )


def lambda_handler(event, context):
    dry_run = False

    account_id = json.loads(event["body"]).get("account_id")
    sso_assignments = ""

    try:
        response = (
            SSO_ADMIN_CLIENT.list_permission_sets_provisioned_to_account(
                InstanceArn=INSTANCE_ARN, AccountId=account_id
            )
        )
        permission_sets = response["PermissionSets"]

        while "NextToken" in response:
            response = (
                SSO_ADMIN_CLIENT.list_permission_sets_provisioned_to_account(
                    InstanceArn=INSTANCE_ARN,
                    AccountId=account_id,
                    NextToken=response["NextToken"],
                )
            )
            permission_sets.extend(response["PermissionSets"])

        assignments = []
        for permission_set in permission_sets:

            response = SSO_ADMIN_CLIENT.list_account_assignments(
                InstanceArn=INSTANCE_ARN,
                AccountId=account_id,
                PermissionSetArn=permission_set,
            )

            assignments.extend(response["AccountAssignments"])

            while "NextToken" in response:
                response = SSO_ADMIN_CLIENT.list_account_assignments(
                    InstanceArn=INSTANCE_ARN,
                    AccountId=account_id,
                    PermissionSetArn=permission_set,
                    NextToken=response["NextToken"],
                )
                assignments.extend(response["AccountAssignments"])

        with open("config/assignments_to_retain.json") as file:
            assignments_to_retain = json.load(file)

        for assignment_to_retain in assignments_to_retain:
            for i, existing_assignment in enumerate(assignments):

                if (
                    assignment_to_retain["PermissionSetArn"]
                    == existing_assignment["PermissionSetArn"]
                    and assignment_to_retain["PrincipalType"]
                    == existing_assignment["PrincipalType"]
                    and assignment_to_retain["PrincipalId"]
                    == existing_assignment["PrincipalId"]
                ):
                    print(existing_assignment)
                    del assignments[i]

        sso_assignments = assignments

        print(f"return: {sso_assignments}")

        response_body = {
            "status": "Complete",
            "dry_run": dry_run,
            "sso_assignments_for_deletion": sso_assignments,
        }

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(response_body),
        }

    except Exception as e:
        return {
            "statusCode": 502,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": type(e).__name__, "message": str(e)}),
        }