output "name" {
  description = "The name of the Linux Web App."
  value       = azurerm_linux_web_app.this.name
}

output "default_site_hostname" {
  description = "The default hostname of the Linux Web App."
  value       = azurerm_linux_web_app.this.default_hostname
}

output "principal_id" {
  description = "The Principal ID of the System Assigned Managed Identity for the App Service."
  value       = azurerm_linux_web_app.this.identity[0].principal_id
}
