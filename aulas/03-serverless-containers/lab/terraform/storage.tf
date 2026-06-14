# Storage Account obrigatório para a Function (estado interno + logs)
resource "azurerm_storage_account" "func_sa" {
  name                     = "stfunc${random_string.sufixo.result}"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_2"
  tags                     = local.tags
}

# Storage do CATÁLOGO da QC — criado NESTA aula (Aula 3 é independente da Aula 2).
# A Function e o ACI leem o produtos.csv daqui via Managed Identity.
resource "azurerm_storage_account" "catalogo" {
  name                     = "stcatqc${random_string.sufixo.result}"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_2"
  tags                     = local.tags
}

resource "azurerm_storage_container" "catalogo" {
  name                  = "catalogo"
  storage_account_name  = azurerm_storage_account.catalogo.name
  container_access_type = "private"
}

# Sobe o produtos.csv automaticamente no apply — sem passo de upload manual.
# A Aula 3 fica autossuficiente (não precisa do storage nem do CSV da Aula 2).
resource "azurerm_storage_blob" "produtos" {
  name                   = "produtos.csv"
  storage_account_name   = azurerm_storage_account.catalogo.name
  storage_container_name = azurerm_storage_container.catalogo.name
  type                   = "Block"
  source                 = "${path.module}/../data/produtos.csv"
}
