# Azure Container Registry — guarda a imagem do container FastAPI
resource "azurerm_container_registry" "acr" {
  name                = "acrqc${random_string.sufixo.result}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Basic"
  admin_enabled       = true # didático; em produção, usar Managed Identity para auth
  tags                = local.tags
}

# Managed Identity user-assigned para o ACI (separada da Function)
resource "azurerm_user_assigned_identity" "aci_id" {
  name                = "id-aci-qc-${random_string.sufixo.result}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  tags                = local.tags
}

# Permissão para a UAI do ACI ler blobs do Storage do catálogo
# (já podemos conceder antes do ACI existir — a role pertence à identidade, não ao ACI)
resource "azurerm_role_assignment" "aci_blob_reader" {
  scope                = azurerm_storage_account.catalogo.id
  role_definition_name = "Storage Blob Data Reader"
  principal_id         = azurerm_user_assigned_identity.aci_id.principal_id
}

# ACI roda o container puxando a imagem do ACR.
# Habilitado apenas quando var.aci_enabled = true (a imagem precisa existir no ACR antes).
resource "azurerm_container_group" "aci" {
  count = var.aci_enabled ? 1 : 0

  name                = "aci-qc-${random_string.sufixo.result}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  ip_address_type     = "Public"
  dns_name_label      = "qc-api-${random_string.sufixo.result}"
  os_type             = "Linux"

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.aci_id.id]
  }

  image_registry_credential {
    server   = azurerm_container_registry.acr.login_server
    username = azurerm_container_registry.acr.admin_username
    password = azurerm_container_registry.acr.admin_password
  }

  container {
    name   = "produtos-api"
    image  = "${azurerm_container_registry.acr.login_server}/produtos-api:v1"
    cpu    = "0.5"
    memory = "1.0"

    ports {
      port     = 8080
      protocol = "TCP"
    }

    environment_variables = {
      STORAGE_ACCOUNT_CATALOGO = azurerm_storage_account.catalogo.name
    }
  }

  tags = local.tags
}
