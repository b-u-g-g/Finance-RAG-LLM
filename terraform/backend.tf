terraform {
  backend "azurerm" {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "tfstatefinancerag"
    container_name       = "tfstate"
    key                  = "finance-rag-llm.tfstate"
  }
}
