
output "db_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = aws_db_instance.postgres.endpoint
}

output "db_address" {
  description = "RDS PostgreSQL hostname"
  value       = aws_db_instance.postgres.address
}

output "db_port" {
  description = "Port used by PostgreSQL"
  value       = aws_db_instance.postgres.port
}

output "db_name" {
  description = "Application database name"
  value       = aws_db_instance.postgres.db_name
}
