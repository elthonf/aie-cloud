# Key Vault — guarda a connection string do SQL como segredo
resource "azurerm_key_vault" "qc" {
  name                       = "kv-qc-${random_string.sufixo.result}"
  location                   = azurerm_resource_group.rg.location
  resource_group_name        = azurerm_resource_group.rg.name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  enable_rbac_authorization  = true
  soft_delete_retention_days = 7
  purge_protection_enabled   = false
  tags                       = local.tags
}

# Concede ao usuário autenticado permissão de gerenciar segredos
resource "azurerm_role_assignment" "kv_admin" {
  scope                = azurerm_key_vault.qc.id
  role_definition_name = "Key Vault Secrets Officer"
  principal_id         = data.azurerm_client_config.current.object_id
}

# Aguarda a role propagar antes de criar o segredo (evita 403)
resource "time_sleep" "wait_rbac" {
  depends_on      = [azurerm_role_assignment.kv_admin]
  create_duration = "60s"
}

# Connection string do Azure SQL como segredo no Vault
resource "azurerm_key_vault_secret" "sql_connection" {
  name         = "sql-connection-string"
  key_vault_id = azurerm_key_vault.qc.id
  # Encrypt=yes / TrustServerCertificate=no: sintaxe aceita pelo ODBC Driver 18
  # (pyodbc no Cloud Shell). "true"/"false" só valem para .NET/SqlClient e o
  # ODBC rejeita com "Invalid value specified for connection string attribute 'Encrypt'".
  value        = "Server=tcp:${azurerm_mssql_server.qc.fully_qualified_domain_name},1433;Database=${azurerm_mssql_database.qc.name};User ID=sqladminqc;Password=${var.sql_admin_password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
  content_type = "connection-string"
  depends_on   = [time_sleep.wait_rbac]
}
