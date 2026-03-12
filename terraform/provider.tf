terraform {
  required_version = ">=1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }

    archive = {
      source  = "hashicorp/archive"
      version = "2.7.1"
    }
  }
}

provider "aws" {
  region = "us-west-2"

  default_tags {
    tags = {
      Owner   = "Terraform_IaC"
      Purpose = "aws_terraform_tests"
    }
  }
}
