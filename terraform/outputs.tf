output "resource_group_name" {
  description = "Name of the provisioned resource group"
  value       = azurerm_resource_group.main.name
}

output "vm_public_ip" {
  description = "Public IP address of the VM"
  value       = module.compute.public_ip
}

output "ssh_command" {
  description = "Command to SSH into the VM"
  value       = "ssh ${var.admin_username}@${module.compute.public_ip}"
}

output "app_url" {
  description = "URL to access the Streamlit app after Docker is running"
  value       = "http://${module.compute.public_ip}:8501"
}
