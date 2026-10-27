
variable "project_name" {
  description = "Name used to identify project resources"
  type        = string
}

variable "private_subnet_ids" {
  description = "Private subnet IDs for the RDS database"
  type        = list(string)
}

variable "rds_security_group_id" {
  description = "Security group ID for the RDS database"
  type        = string
}

variable "db_username" {
  description = "Master username for PostgreSQL"
  type        = string
  default     = "appadmin"
}

variable "db_password" {
  description = "Master password for PostgreSQL"
  type        = string
  sensitive   = true
}
