
# the first line has to be empty for jinja2 indentation ¯\_(ツ)_/¯
import os
import boto3

s3 = None
ENV_BUCKET_NAME = "BUCKET_NAME"

def lambda_handler(event, context):
    global s3
    if s3 is None:
        s3 = boto3.client("s3")
    bucket_name = os.environ[ENV_BUCKET_NAME]

    # Block all public access
    s3.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            "BlockPublicAcls": True,
            "IgnorePublicAcls": True,
            "BlockPublicPolicy": True,
            "RestrictPublicBuckets": True
        }
    )
    print(f"Public access disabled for bucket {bucket_name}")
    return {
        "statusCode": 200,
        "body": f"Bucket {bucket_name} is now restricted due to high request volume."
    }