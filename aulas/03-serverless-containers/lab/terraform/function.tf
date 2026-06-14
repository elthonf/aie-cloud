# Function App Python 3.11 com Managed Identity SystemAssigned
resource "azurerm_linux_function_app" "fn" {
  name                       = "func-qc-${random_string.sufixo.result}"
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
    "FUNCTIONS_WORKER_RUNTIME" = "python"
    "AzureWebJobsFeatureFlags" = "EnableWorkerIndexing"
    "STORAGE_ACCOUNT_CATALOGO" = azurerm_storage_account.catalogo.name
  }

  tags = local.tags
}

# Permissão para a Managed Identity da Function ler blobs do Storage do catálogo.
# É o que permite a versão v2-blob da Function operar sem credenciais no código.
resource "azurerm_role_assignment" "fn_blob_reader" {
  scope                = azurerm_storage_account.catalogo.id
  role_definition_name = "Storage Blob Data Reader"
  principal_id         = azurerm_linux_function_app.fn.identity[0].principal_id
}
