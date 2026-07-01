output "resource_group_name" {
  description = "Nome do Resource Group da QC"
  value       = azurerm_resource_group.rg.name
}

# Storage
output "storage_account_name" {
  description = "Nome do Storage Account (globalmente único)"
  value       = azurerm_storage_account.qc.name
}

output "storage_account_key" {
  description = "Chave primária do Storage Account (sensível)"
  value       = azurerm_storage_account.qc.primary_access_key
  sensitive   = true
}

# SQL
output "sql_server_name" {
  description = "Nome do Azure SQL Server"
  value       = azurerm_mssql_server.qc.name
}

output "sql_database_name" {
  description = "Nome do banco SQL"
  value       = azurerm_mssql_database.qc.name
}

# Key Vault
output "key_vault_name" {
  description = "Nome do Key Vault (usado pelos scripts Python)"
  value       = azurerm_key_vault.qc.name
}

# Cosmos
output "cosmos_endpoint" {
  description = "Endpoint do Cosmos DB"
  value       = azurerm_cosmosdb_account.qc.endpoint
}

output "cosmos_account_name" {
  description = "Nome da conta Cosmos DB"
  value       = azurerm_cosmosdb_account.qc.name
}

# Search
output "search_service_name" {
  description = "Nome do Azure AI Search service"
  value       = azurerm_search_service.qc.name
}

output "search_endpoint" {
  description = "Endpoint do Azure AI Search"
  value       = "https://${azurerm_search_service.qc.name}.search.windows.net"
}

# MongoDB ACI
output "mongodb_public_ip" {
  description = "IP público do ACI com MongoDB"
  value       = azurerm_container_group.mongodb.ip_address
}

output "mongodb_fqdn" {
  description = "FQDN do ACI (alternativa ao IP)"
  value       = azurerm_container_group.mongodb.fqdn
}

output "mongo_express_url" {
  description = "URL do Mongo Express (interface web do MongoDB)"
  value       = "http://${azurerm_container_group.mongodb.ip_address}:8081"
}

output "mongodb_connection_string" {
  description = "Connection string do MongoDB"
  value       = "mongodb://admin:${local.mongo_admin_pass}@${azurerm_container_group.mongodb.ip_address}:27017/?authSource=admin"
  sensitive   = true
}
