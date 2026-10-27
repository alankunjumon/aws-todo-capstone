
output "eks_nodes_security_group_id" {
  description = "ID of the security group for EKS worker nodes"
  value       = aws_security_group.eks_nodes.id
}

output "rds_security_group_id" {
  description = "ID of the security group for the RDS database"
  value       = aws_security_group.rds.id
}
