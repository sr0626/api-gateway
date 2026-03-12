locals {
  s3_bucket_name = "${var.s3_bucket_name}-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_bucket" "test" {
  bucket        = local.s3_bucket_name
  force_destroy = true
}

resource "aws_s3_object" "folders" {
  for_each = toset([
    "my_test1/",
    "log_sync_from_cw/"
  ])

  bucket = aws_s3_bucket.test.id
  key    = each.key
}

resource "aws_s3_bucket_server_side_encryption_configuration" "test" {
  bucket = aws_s3_bucket.test.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = data.aws_kms_alias.test.id
    }

    bucket_key_enabled = true
  }
}