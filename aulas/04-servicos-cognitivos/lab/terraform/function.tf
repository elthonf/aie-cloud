# Storage obrigatório para o runtime da Function App
resource "azurerm_storage_account" "func_sa" {
  name                     = "stfunc04${random_string.sufixo.result}"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_2"
  tags                     = local.tags
}

resource "azurerm_service_plan" "plan" {
  name                = "asp-qc-aula04-${random_string.sufixo.result}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  os_type             = "Linux"
  sku_name            = "Y1"
  tags                = local.tags
}

resource "azurerm_linux_function_app" "fn" {
  name                       = "func-qc-aula04-${random_string.sufixo.result}"
  resource_group_name        = azurerm_resource_group.rg.name
  location                   = azurerm_resource_group.rg.location
  service_plan_id            = azurerm_service_plan.plan.id
  storage_account_name       = azurerm_storage_account.func_sa.name
  storage_account_access_key = azurerm_storage_account.func_sa.primary_access_key

  site_config {
    application_stack {
      python_version = "3.11"
    }
  }

  identity {
    type = "SystemAssigned"
  }

  app_settings = {
    "FUNCTIONS_WORKER_RUNTIME"         = "python"
    "AzureWebJobsFeatureFlags"         = "EnableWorkerIndexing"
    "SCM_DO_BUILD_DURING_DEPLOYMENT"   = "true"
    "ENABLE_ORYX_BUILD"                = "true"
    "AI_ENDPOINT"                      = azurerm_cognitive_account.ai.endpoint
    "AI_REGION"                        = var.location
    # AI_KEY via Key Vault reference — MI da Function lê sem expor a chave no código
    "AI_KEY"                           = "@Microsoft.KeyVault(SecretUri=${azurerm_key_vault_secret.ai_key.id})"
    "DATA_STORAGE_ACCOUNT"             = azurerm_storage_account.data.name
    "MONGODB_URI"                      = "mongodb://admin:${local.mongo_admin_pass}@${azurerm_container_group.mongodb.ip_address}:27017/?authSource=admin"
  }

  tags = local.tags
}

# MI da Function: lê segredos do Key Vault (necessário para resolver a KV reference do AI_KEY)
resource "azurerm_role_assignment" "fn_kv_user" {
  scope                = azurerm_key_vault.kv.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_linux_function_app.fn.identity[0].principal_id
}

# MI da Function: chama Language e Vision via Managed Identity (sem chave)
resource "azurerm_role_assignment" "fn_ai_user" {
  scope                = azurerm_cognitive_account.ai.id
  role_definition_name = "Cognitive Services User"
  principal_id         = azurerm_linux_function_app.fn.identity[0].principal_id
}

# MI da Function: lê e escreve no Blob de dados (upload de áudio/imagem para testes)
resource "azurerm_role_assignment" "fn_blob_contributor" {
  scope                = azurerm_storage_account.data.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_linux_function_app.fn.identity[0].principal_id
}
