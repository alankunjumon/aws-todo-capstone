
# 1. Output the VPC ID
output "vpc_id" {
  description = "ID of the shared VPC"
  value       = module.networking.vpc_id
}

# 2. Output the public subnet IDs
output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = module.networking.public_subnet_ids
}

# 3. Output the private subnet IDs
output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = module.networking.private_subnet_ids
}

# 4. Output the selected Availability Zones
output "availability_zones" {
  description = "Availability Zones used by the network"
  value       = module.networking.availability_zones
}
