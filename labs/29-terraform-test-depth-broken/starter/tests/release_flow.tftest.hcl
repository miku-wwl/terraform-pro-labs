run "single_plan" {
  command = plan

  variables {
    service_name    = "checkout"
    release_version = "v1"
  }

  assert {
    condition     = terraform_data.deployment.input.release == "v1"
    error_message = "The proposed release must match the input."
  }
}
