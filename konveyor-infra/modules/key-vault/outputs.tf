output "key_vault_id" {
  description = "Key Vault ID"
  value       = azurerm_key_vault.vault.id
}

output "key_vault_name" {
  description = "Key Vault name"
  value       = azurerm_key_vault.vault.name
}

output "vault_uri" {
  description = "The URI of the Key Vault"
  value       = azurerm_key_vault.vault.vault_uri
}
