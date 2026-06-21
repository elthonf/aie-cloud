variable "location" {
  description = "Região do Azure onde os recursos serão provisionados"
  type        = string
  default     = "eastus2"
  # Padrão da disciplina: eastus2.
  # Vision 4.0 Caption não disponível em eastus2 — lab usa Tags + OCR + Objects.
  # Para Caption completo: eastus, westus2, westeurope (verificar política da conta).
  # Azure for Students bloqueia eastus e brazilsouth para a maioria dos recursos.
}
