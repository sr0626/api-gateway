output "s3_bucket_name" {
  value = aws_s3_bucket.test.id
}

# output "kms_key_name" {
#   value = aws_kms_key.test.id
# }

# output "kms_key_alias" {
#   value = aws_kms_alias.test.id
# }

output "api_invoke_url" {
  description = "API Gateway invoke URL for the Lambda-backed API"
  value       = "https://${aws_api_gateway_rest_api.api.id}.execute-api.${data.aws_region.current.name}.amazonaws.com/${aws_api_gateway_stage.prod.stage_name}"
}