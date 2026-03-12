# data "aws_iam_policy_document" "kms_policy" {
#   # --- Admin / safety: retain control of the key policy ---
#   statement {
#     sid    = "EnableIAMUserPermissions"
#     effect = "Allow"
#     principals {
#       type        = "AWS"
#       identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
#     }
#     actions   = ["kms:*"]
#     resources = ["*"]
#   }
# }

# resource "aws_kms_key" "test" {
#   description             = "CMK for Amazon Connect artifacts"
#   deletion_window_in_days = 7
#   enable_key_rotation     = true
#   policy                  = data.aws_iam_policy_document.kms_policy.json

#   # lifecycle {
#   #   prevent_destroy = true
#   # }
# }

# resource "aws_kms_alias" "test" {
#   name          = "alias/my-kms-alias"
#   target_key_id = aws_kms_key.test.key_id

#   # lifecycle {
#   #   prevent_destroy = true
#   # }
# }

data "aws_kms_alias" "test" {
  name = "alias/test-key"
}

data "aws_kms_key" "test" {
  key_id = data.aws_kms_alias.test.target_key_id
}