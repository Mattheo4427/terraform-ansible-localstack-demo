terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region                      = "us-east-1"
  access_key                  = "test"
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  endpoints {
    dynamodb = "http://localstack:4566"
    ec2      = "http://localstack:4566"
  }

  default_tags {
    tags = {
      Environment = "localstack"
      Project     = "todo-app"
    }
  }
}