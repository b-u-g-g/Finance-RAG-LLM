variable "resource_group_name" {
  description = "Name of the Azure Resource Group"
  type        = string
  default     = "finance-rag-llm-rg"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "East US"
}

variable "project_name" {
  description = "Prefix for all resource names"
  type        = string
  default     = "finance-rag"
}

variable "vm_size" {
  description = "Azure VM size (Standard_B1s = cheapest, within student credits)"
  type        = string
  default     = "Standard_B1s"
}

variable "admin_username" {
  description = "Admin username for the VM"
  type        = string
  default     = "azureuser"
}

variable "ssh_public_key_path" {
  description = "Path to your SSH public key. Generate with: ssh-keygen -t rsa -b 4096"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}

variable "tags" {
  description = "Tags applied to every resource (useful for cost tracking)"
  type        = map(string)
  default = {
    project     = "finance-rag-llm"
    environment = "production"
    managed_by  = "terraform"
  }
}
