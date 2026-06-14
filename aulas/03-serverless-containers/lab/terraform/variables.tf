variable "location" {
  # Padrão da disciplina: eastus2. Brazil South costuma ser bloqueado pela
  # política "best available regions" das contas Azure for Students.
  description = "Região do Azure onde os recursos serão provisionados"
  type        = string
  default     = "eastus2"
}

variable "aci_enabled" {
  description = "Quando true, provisiona o Azure Container Instances. Deixe false no primeiro apply (a imagem precisa ser pushed ao ACR antes do ACI subir)."
  type        = bool
  default     = false
}
