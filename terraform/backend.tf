terraform {
  backend "s3" {
    bucket         = "smart-search-storages"
    key            = "terraform.tfstate"
    region         = "eu-west-1"
  }
}
