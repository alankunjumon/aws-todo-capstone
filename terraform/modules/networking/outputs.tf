
# 1. Output the VPC ID
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

# 2. Output the public subnet IDs
output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = aws_subnet.public[*].id
}

# 3. Output the private subnet IDs
output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = aws_subnet.private[*].id
}

# 4. Output the Availability Zones
output "availability_zones" {
  description = "Availability Zones used by the network"
  value       = var.availability_zones
}
