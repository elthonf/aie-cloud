output "resource_group_name" {
  description = "Nome do Resource Group da Aula 3"
  value       = azurerm_resource_group.rg.name
}

output "catalogo_storage_account_name" {
  description = "Storage Account do catálogo (criado nesta aula, já com produtos.csv)"
  value       = azurerm_storage_account.catalogo.name
}

# Function
output "function_app_name" {
  description = "Nome da Function App (usar no 'func azure functionapp publish')"
  value       = azurerm_linux_function_app.fn.name
}

output "function_app_default_hostname" {
  description = "URL HTTPS da Function App"
  value       = "https://${azurerm_linux_function_app.fn.default_hostname}"
}

# Container Registry
output "acr_login_server" {
  description = "Endereço do ACR (usar para 'docker tag' e 'docker push')"
  value       = azurerm_container_registry.acr.login_server
}

output "acr_name" {
  description = "Nome curto do ACR (usar com 'az acr ...')"
  value       = azurerm_container_registry.acr.name
}

# ACI (condicional)
output "aci_fqdn" {
  description = "FQDN do ACI quando habilitado; do contrário, mensagem"
  value       = var.aci_enabled ? azurerm_container_group.aci[0].fqdn : "ACI ainda não habilitado — após pushar imagem, rode 'terraform apply' com -var aci_enabled=true"
}
