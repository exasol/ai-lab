import boto3

s3 = boto3.client("s3")


def lambda_handler(event, context):
    bucket_name = "ai-lab-example-data-s3"
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