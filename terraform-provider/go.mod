module github.com/afeldman/errorbrain/terraform-provider

go 1.21

require (
	github.com/afeldman/errorbrain/sdk-go v0.1.0
	github.com/hashicorp/terraform-plugin-sdk/v2 v2.29.0
)

replace github.com/afeldman/errorbrain/sdk-go => ../sdk-go
