variable "log_retention" {
  type    = number
  default = 30
}

variable "s3_bucket_name" {
  type    = string
  default = "sr0626-s3-test"
}

variable "lambda_name" {
  type    = string
  default = "sr0626-test-lambda"
}

