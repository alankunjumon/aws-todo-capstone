terraform {
  backend "s3" {
    bucket       = "capstone-project-state-file"
    key          = "aws-todo-capstone/dev/terraform.tfstate"
    region       = "us-east-1"
    encrypt      = true
    use_lockfile = true
  }
}

# 1. Configure the AWS provider
provider "aws" {
  region = var.aws_region
}

# 2. Discover available Availability Zones
data "aws_availability_zones" "available" {
  state = "available"
}

# 3. Create the networking module
module "networking" {
  source = "../../modules/networking"

  project_name = var.project_name

  availability_zones = slice(
    data.aws_availability_zones.available.names,
    0,
    var.az_count
  )
}


# 4. Create security groups
module "security" {
  source = "../../modules/security"

  project_name = var.project_name
  vpc_id       = module.networking.vpc_id
}


# 5. Create the ECR repository
module "ecr" {
  source = "../../modules/ecr"

  project_name = var.project_name
}

# 6. Create IAM roles and policies
module "iam" {
  source = "../../modules/iam"

  project_name = var.project_name
}


# 7. Create the RDS PostgreSQL database
module "rds" {
  source = "../../modules/rds"

  project_name          = var.project_name
  private_subnet_ids    = module.networking.private_subnet_ids
  rds_security_group_id = module.security.rds_security_group_id

  db_password = var.db_password
}

# 8. Create the eks cluster and managed nodes
module "eks" {
  source = "../../modules/eks"

  node_security_group_id = module.security.eks_nodes_security_group_id

  project_name = var.project_name

  private_subnet_ids = module.networking.private_subnet_ids

  cluster_role_arn = module.iam.eks_cluster_role_arn
  node_role_arn    = module.iam.eks_node_role_arn

  cluster_endpoint_public_access_cidrs = var.cluster_endpoint_public_access_cidrs
}

#9 Create the load balancer contoller iam role
module "load_balancer_controller_iam" {
  source = "../../modules/load-balancer-controller-iam"

  project_name            = var.project_name
  cluster_oidc_issuer_url = module.eks.cluster_oidc_issuer_url
}
