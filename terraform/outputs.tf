output "dynamodb_table" {
  description = "Name of the DynamoDB table"
  value       = aws_dynamodb_table.todo_table.name
}

output "dynamodb_table_arn" {
  description = "ARN of the DynamoDB table"
  value       = aws_dynamodb_table.todo_table.arn
}

output "nginx_url" {
  description = "URL of the Nginx load balancer"
  value       = "http://localhost:80"
}