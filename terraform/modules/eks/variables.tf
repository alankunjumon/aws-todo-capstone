
variable "project_name" {
  description = "Name used to identify project resources"
  type        = string
}

variable "private_subnet_ids" {
  description = "Private subnets where EKS worker nodes will run"
  type        = list(string)
}

variable "cluster_role_arn" {
  description = "IAM role ARN for the EKS control plane"
  type        = string
}

variable "node_role_arn" {
  description = "IAM role ARN for EKS worker nodes"
  type        = string
}

variable "node_instance_types" {
  description = "EC2 instance types for the managed node group"
  type        = list(string)
  default     = ["c7i-flex.large"]
}

variable "desired_size" {
  description = "Desired number of worker nodes"
  type        = number
  default     = 2
}

variable "min_size" {
  description = "Minimum number of worker nodes"
  type        = number
  default     = 2
}

variable "max_size" {
  description = "Maximum number of worker nodes"
  type        = number
  default     = 3
}

variable "cluster_endpoint_public_access_cidrs" {
  description = "Public IP CIDR ranges allowed to access the Kubernetes API"
  type        = list(string)
}

variable "node_security_group_id" {
  description = "Security group ID for EKS worker nodes"
  type        = string
}
