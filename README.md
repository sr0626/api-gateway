# api-gateway

Overview

- Purpose: Terraform project that deploys an AWS API Gateway backed by a Lambda which lists S3 objects.
- Layout: Terraform files are in the `terraform/` directory and the Lambda source is at `terraform/lambda/`.

Prerequisites

- AWS credentials configured for the target account/region.
- Terraform (tested with Terraform >= 1.5).

Quick deploy

1. Change into the Terraform directory and initialize:

```bash
cd terraform
terraform init
terraform fmt
terraform apply --auto-approve
```

2. After apply, get the API base URL from Terraform outputs:

```bash
terraform output -raw api_invoke_url
# example result: https://x78mylze2e.execute-api.us-west-2.amazonaws.com/prod
```

API usage

- The API forwards requests to the Lambda via a greedy proxy. You can provide the S3 bucket name either as the first path segment or as the `bucket` query parameter.
- Query parameters supported:
	- `bucket` — S3 bucket name (optional if provided in path)
	- `recursive` — `true` (recursive listing) or `false` (top-level prefixes)
	- `max` — maximum items to return (integer)

Examples (replace `<API_BASE>` with the value from `terraform output -raw api_invoke_url`):

Recursive listing (full object listing):

```bash
curl -s "${API_BASE}/my-bucket?recursive=true&max=100" | jq .
```

Non-recursive (top-level prefixes):

```bash
curl -s "${API_BASE}/my-bucket?recursive=false&max=100" | jq .
```

Response shape

The Lambda returns a proxy-compatible JSON response. Successful responses include at least:

```json
{
	"ok": true,
	"bucket": "my-bucket",
	"count": 42,
	"objects": [ {"Key": "path/to/object", "Size": 1234, "LastModified": "..."} ],
	"truncated": false,
	"recursive": true
}
```

Sample outputs

Recursive listing (example curl + pretty JSON output):

```bash
curl -s "${API_BASE}/sr0626-s3-test-044336301301?recursive=true&max=100" | jq .
```

```json
{
	"ok": true,
	"bucket": "sr0626-s3-test-044336301301",
	"count": 3,
	"objects": [
		{"Key": "my_test1/file1.txt", "Size": 123, "LastModified": "2026-03-10T12:00:00Z"},
		{"Key": "my_test1/sub/file2.txt", "Size": 456, "LastModified": "2026-03-10T12:01:00Z"},
		{"Key": "log_sync_from_cw/2026-03-10.log", "Size": 789, "LastModified": "2026-03-10T12:02:00Z"}
	],
	"truncated": false,
	"recursive": true
}
```

Non-recursive listing (example curl + pretty JSON output):

```bash
curl -s "${API_BASE}/sr0626-s3-test-044336301301?recursive=false&max=100" | jq .
```

```json
{
	"ok": true,
	"bucket": "sr0626-s3-test-044336301301",
	"count": 2,
	"objects": [
		{"Prefix": "log_sync_from_cw/"},
		{"Prefix": "my_test1/"}
	],
	"truncated": false,
	"recursive": false
}
```

Lambda notes

- Handler: `terraform/lambda/boto3_lambda.py::lambda_handler` (file was renamed to `boto3_lambda.py` to avoid import errors).
- The handler chooses recursive vs non-recursive listing based on the `recursive` query parameter.

Security and production considerations

- Current IAM: the Lambda role is permissive for S3 List/Get to allow supplying arbitrary bucket names during testing. For production, narrow the IAM policy to the specific buckets the function must access.
- For very large buckets, consider implementing pagination tokens in the API rather than returning extremely large responses.

Troubleshooting

- If API Gateway returns a 502 (Internal server error), check CloudWatch Logs for the Lambda function (log group `/aws/lambda/<your-lambda-name>`) to inspect the exception and stack trace.
- Ensure the Lambda returns a proxy-compatible response with `statusCode`, `headers`, and `body`.

Files of interest

- [terraform/api_gateway.tf](terraform/api_gateway.tf)
- [terraform/lambda.tf](terraform/lambda.tf)
- [terraform/lambda/boto3_lambda.py](terraform/lambda/boto3_lambda.py)

Next steps

- I can tighten the IAM policy, add continuation tokens for pagination, or split listing modes into separate Lambda functions if you'd like — tell me which and I will implement it.