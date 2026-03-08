terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# ── Resource Group ─────────────────────────────────────────────────────────────
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

# ── Networking module: VNet + Subnet ───────────────────────────────────────────
module "networking" {
  source              = "./modules/networking"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  vnet_name           = "${var.project_name}-vnet"
  vnet_address_space  = ["10.0.0.0/16"]
  subnet_name         = "${var.project_name}-subnet"
  subnet_prefix       = ["10.0.1.0/24"]
  tags                = var.tags
}

# ── Security module: NSG rules ─────────────────────────────────────────────────
module "security" {
  source              = "./modules/security"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  nsg_name            = "${var.project_name}-nsg"
  subnet_id           = module.networking.subnet_id
  tags                = var.tags
}

# ── Compute module: VM + Public IP + NIC ──────────────────────────────────────
module "compute" {
  source              = "./modules/compute"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  vm_name             = "${var.project_name}-vm"
  vm_size             = var.vm_size
  admin_username      = var.admin_username
  ssh_public_key      = file(var.ssh_public_key_path)
  subnet_id           = module.networking.subnet_id
  nsg_id              = module.security.nsg_id
  tags                = var.tags
}
