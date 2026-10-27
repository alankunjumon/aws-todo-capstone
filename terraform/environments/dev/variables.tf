
variable "project_name" {
  description = "Name used to identify project resources"
  type        = string
  default     = "aws-todo"
}

variable "aws_region" {
  description = "AWS region for the infrastructure"
  type        = string
  default     = "us-east-1"
}

variable "az_count" {
  description = "Number of Availability Zones to use"
  type        = number
  default     = 2
}

variable "db_password" {
  description = "Master password for the RDS PostgreSQL database"
  type        = string
  sensitive   = true
}


variable "cluster_endpoint_public_access_cidrs" {
  description = "Public IP CIDR ranges allowed to access the Kubernetes API"
  type        = list(string)
}
