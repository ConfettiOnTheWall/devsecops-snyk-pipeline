# Minimal, intentionally-flawed Terraform used as the target for
# `snyk iac test`. The S3 bucket below is missing encryption and has a
# public-read ACL — both are things Snyk IaC should flag.

provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "demo_bucket" {
  bucket = "devsecops-snyk-demo-bucket"
  acl    = "public-read" # intentional misconfig — Snyk should flag this
}

resource "aws_security_group" "demo_sg" {
  name        = "devsecops-demo-sg"
  description = "Intentionally open security group for IaC scanning demo"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # intentional misconfig — open SSH to the world
  }
}
