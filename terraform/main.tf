provider "aws" {
  region = "eu-west-1"
}

data "aws_secretsmanager_secret" "smart_search" {
  name = "smart-search"
}

data "aws_secretsmanager_secret_version" "smart_search_secret_version" {
  secret_id = data.aws_secretsmanager_secret.smart_search.id
}

resource "aws_kms_key" "opensearch_kms_key" {
  description             = "KMS key for OpenSearch encryption at rest"
  deletion_window_in_days = 30
}

resource "aws_kms_alias" "opensearch_kms_alias" {
  name          = "alias/smart-search-kms"
  target_key_id = aws_kms_key.opensearch_kms_key.id
}

resource "aws_opensearch_domain" "opensearch_domain" {
  domain_name           = "smart-search"
  engine_version = "OpenSearch_2.11"
  cluster_config {
    instance_type = "t3.small.search"
    instance_count = 1
  }
  domain_endpoint_options {
    enforce_https = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }

  node_to_node_encryption {
    enabled = true
  }
  encrypt_at_rest {
    enabled = true
    kms_key_id = aws_kms_key.opensearch_kms_key.arn
  }
  ebs_options {
    ebs_enabled = true
    volume_size = 10
  }
  access_policies = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = "*"
      Action    = "es:*"
      Resource  = "arn:aws:es:*:*:domain/smart-search/*"
    }]
  })
  advanced_security_options {
    enabled             = true
    internal_user_database_enabled = true
    master_user_options {
      master_user_name    = jsondecode(data.aws_secretsmanager_secret_version.smart_search_secret_version.secret_string)["OPEN_SEARCH_INITIAL_ADMIN_USERNAME"]
      master_user_password = jsondecode(data.aws_secretsmanager_secret_version.smart_search_secret_version.secret_string)["OPENSEARCH_INITIAL_ADMIN_PASSWORD"]
    }
  }
}

resource "aws_db_instance" "postgresql_db" {
  identifier            = "smart-search-db"
  allocated_storage     = 20
  engine                = "postgres"
  engine_version        = "15"
  instance_class        = "db.t3.small"
  db_name                  = jsondecode(data.aws_secretsmanager_secret_version.smart_search_secret_version.secret_string)["POSTGRES_DB"]
  username              = jsondecode(data.aws_secretsmanager_secret_version.smart_search_secret_version.secret_string)["POSTGRES_USER"]
  password              = jsondecode(data.aws_secretsmanager_secret_version.smart_search_secret_version.secret_string)["POSTGRES_PASSWORD"]
  skip_final_snapshot   = true
  publicly_accessible = true

  vpc_security_group_ids = [aws_security_group.postgresql_sg.id]
}

resource "aws_security_group" "postgresql_sg" {
  name        = "postgresql_sg"
  description = "Security group for PostgreSQL database"

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "opensearch_security_group" {
  name        = "opensearch-security-group"
  description = "Security group for OpenSearch domain"

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


data "aws_s3_bucket" "inputs" {
  bucket = "smart-search-inputs"
}

data "aws_s3_bucket" "outputs" {
  bucket = "smart-search-outputs"
}

data "aws_s3_bucket" "storages" {
  bucket = "smart-search-storages"
}

output "opensearch_host" {
  value = aws_opensearch_domain.opensearch_domain.endpoint
}

output "postgresql_host" {
  value = aws_db_instance.postgresql_db.address
}
