
# Output the EKS cluster role ARN
output "eks_cluster_role_arn" {
  description = "ARN of the EKS cluster IAM role"
  value       = aws_iam_role.eks_cluster.arn
}

# Output the EKS worker-node role ARN
output "eks_node_role_arn" {
  description = "ARN of the EKS worker-node IAM role"
  value       = aws_iam_role.eks_node.arn
}

# Output the EKS worker-node role name
output "eks_node_role_name" {
  description = "Name of the EKS worker-node IAM role"
  value       = aws_iam_role.eks_node.name
}
