# CLAUDE.md - AI Assistant Guide

This document provides comprehensive guidance for AI assistants working with this repository.

## Repository Overview

This repository implements a **GitOps workflow for managing Google Cloud Platform (GCP) infrastructure using Terraform and Cloud Build**. It demonstrates infrastructure as code best practices for multi-environment deployments.

**Primary Technologies:**
- **Terraform 0.11.14**: Infrastructure as Code
- **Google Cloud Build**: CI/CD automation
- **Google Cloud Platform**: Target infrastructure platform
- **GitOps**: Branch-based environment management

**Purpose:** Automate infrastructure provisioning using a GitOps approach where branches represent environments and commits trigger automated deployments.

## Codebase Structure

```
.
├── cloudbuild.yaml           # Cloud Build pipeline configuration
├── environments/             # Environment-specific configurations
│   ├── dev/                 # Development environment
│   │   ├── backend.tf       # GCS backend configuration
│   │   ├── main.tf          # Environment main config (env="dev")
│   │   ├── variables.tf     # Input variables
│   │   ├── terraform.tfvars # Variable values
│   │   ├── versions.tf      # Terraform version constraints
│   │   └── outputs.tf       # Output values
│   └── prod/                # Production environment
│       ├── backend.tf       # GCS backend configuration
│       ├── main.tf          # Environment main config (env="prod")
│       ├── variables.tf     # Input variables
│       ├── terraform.tfvars # Variable values
│       ├── versions.tf      # Terraform version constraints
│       └── outputs.tf       # Output values
├── modules/                 # Reusable Terraform modules
│   ├── vpc/                # VPC network module
│   │   ├── main.tf         # VPC and subnet creation
│   │   ├── variables.tf    # Module inputs
│   │   ├── outputs.tf      # Module outputs
│   │   └── versions.tf     # Provider versions
│   ├── http_server/        # HTTP server compute instance module
│   │   ├── main.tf         # GCE instance with Apache2
│   │   ├── variables.tf    # Module inputs
│   │   ├── outputs.tf      # Module outputs
│   │   └── versions.tf     # Provider versions
│   └── firewall/           # Firewall rules module
│       ├── main.tf         # HTTP firewall rule
│       ├── variables.tf    # Module inputs
│       ├── outputs.tf      # Module outputs
│       └── versions.tf     # Provider versions
├── README.md               # User documentation
├── CONTRIBUTING.md         # Contribution guidelines
└── LICENSE                 # Apache 2.0 license
```

## GitOps Workflow

### Branch-Based Environment Deployment

The repository uses **branch names to determine which environment to deploy**:

1. **Environment Branches** (`dev`, `prod`):
   - Commits to these branches trigger `terraform apply`
   - Changes are automatically deployed to the corresponding environment
   - Branch name must match a directory in `environments/`

2. **Feature Branches** (any other name):
   - Runs `terraform init` and `terraform plan` for all environments
   - Does NOT apply changes (safe for testing)
   - Used for development and testing

### Cloud Build Pipeline (`cloudbuild.yaml`)

The pipeline consists of 4 steps:

1. **Branch Name Detection**: Displays the branch being built
2. **Terraform Init**: Initializes Terraform for the target environment
3. **Terraform Plan**: Generates execution plan
4. **Terraform Apply**: Applies changes (only for environment branches)

**Key Logic:**
```bash
if [ -d "environments/$BRANCH_NAME/" ]; then
  # Apply to specific environment
else
  # Run plan for all environments (no apply)
fi
```

## Infrastructure Components

### Current Implementation

The repository deploys a simple HTTP server infrastructure:

1. **VPC Module** (`modules/vpc/`):
   - Creates a VPC network named after the environment (`dev` or `prod`)
   - Creates subnet: `{env}-subnet-01`
   - Uses IP ranges: `10.10.10.0/24` (dev) or `10.20.10.0/24` (prod)
   - Region: `us-west1`

2. **HTTP Server Module** (`modules/http_server/`):
   - Provisions a GCE `f1-micro` instance
   - Installs Apache2 via startup script
   - Serves a simple HTML page showing environment name
   - Zone: `us-west1-a`
   - Image: `debian-cloud/debian-9`

3. **Firewall Module** (`modules/firewall/`):
   - Creates firewall rule to allow HTTP traffic (port 80)
   - Applies to instances tagged with `http-server`
   - Source: `0.0.0.0/0` (public internet)

### Module Dependencies

```
main.tf (environment)
  ├── vpc module → creates network and subnet
  ├── http_server module → requires subnet from vpc
  └── firewall module → requires subnet from vpc
```

## Key Terraform Conventions

### Version and Syntax

- **Terraform Version**: 0.11.14 (legacy syntax)
- **Interpolation**: Uses `"${var.name}"` syntax (pre-0.12)
- **Google Provider**: Uses `terraform-google-modules/network/google` v0.6.0

### State Management

- **Backend**: Google Cloud Storage (GCS)
- **Dev State**: `gs://hello-world-306019-tfstate/env/dev`
- **Prod State**: `gs://hello-world-306019-tfstate/env/prod`
- State is stored separately per environment

### Variable Patterns

**Required Variables:**
- `project`: GCP project ID (defined in `terraform.tfvars`)

**Local Variables:**
- `env`: Environment name (`dev` or `prod`) defined in `main.tf`

### Naming Conventions

**Resources:**
- Networks: `{env}` (e.g., `dev`, `prod`)
- Subnets: `{env}-subnet-01`
- Instances: `{network}-apache2-instance`
- Firewall rules: `{network}-allow-http`

**Pattern:** Resources are prefixed with environment/network name for easy identification

## Development Guidelines for AI Assistants

### 1. Making Infrastructure Changes

When modifying infrastructure:

**DO:**
- ✅ Preserve the modular structure (keep logic in modules)
- ✅ Maintain consistency between `dev` and `prod` environments
- ✅ Update both environments unless specifically targeting one
- ✅ Add new resources to appropriate modules
- ✅ Update module outputs if adding new exported values
- ✅ Keep the Terraform 0.11 syntax (`"${}"` interpolation)
- ✅ Test changes in `dev` before promoting to `prod`
- ✅ Update version constraints in `versions.tf` files

**DON'T:**
- ❌ Put resource definitions directly in environment `main.tf`
- ❌ Use Terraform 0.12+ syntax (no `var.name` without quotes)
- ❌ Hardcode values that should be variables
- ❌ Skip updating both environments for shared changes
- ❌ Modify state backend configuration without coordination
- ❌ Change the GitOps workflow without updating documentation

### 2. Adding New Modules

When creating a new module:

1. Create directory under `modules/{module_name}/`
2. Include these files:
   - `main.tf`: Resource definitions
   - `variables.tf`: Input variables with descriptions
   - `outputs.tf`: Output values
   - `versions.tf`: Provider version constraints
3. Add Apache 2.0 license header to all files
4. Reference from environment `main.tf` files
5. Pass required variables from environment to module

**Example Module Reference:**
```hcl
module "new_module" {
  source  = "../../modules/new_module"
  project = "${var.project}"
  env     = "${local.env}"
  subnet  = "${module.vpc.subnet}"  # If needed
}
```

### 3. Working with Environments

**Environment-Specific Values:**
- Defined in `terraform.tfvars` (not tracked in detail here)
- Backend bucket and prefix in `backend.tf`
- Local `env` variable in `main.tf`

**Adding New Environment:**
1. Create `environments/{env_name}/` directory
2. Copy structure from `dev/` or `prod/`
3. Update `local.env` value in `main.tf`
4. Create new backend bucket or prefix
5. Update `terraform.tfvars` with environment values
6. Create corresponding git branch

### 4. Cloud Build Considerations

When modifying `cloudbuild.yaml`:

- Pipeline runs on every commit
- Uses Terraform 0.11.14 Docker image
- Each step must succeed (|| exit 1)
- Environment branch detection is case-sensitive
- Plan runs for all environments on feature branches

**Pipeline Modification Guidelines:**
- Preserve the conditional logic for branch detection
- Maintain error handling (`|| exit 1`)
- Keep informative echo statements
- Test in a feature branch first

### 5. Common Operations

#### Updating a Module

```bash
# 1. Modify module files in modules/{name}/
# 2. Update both dev and prod if needed
# 3. Test plan locally
cd environments/dev
terraform init
terraform plan
```

#### Adding a New Resource

```bash
# 1. Add to appropriate module
# 2. Add variables if needed
# 3. Add outputs if needed
# 4. Update environment main.tf to use new output
```

#### Changing Network Configuration

- Network changes affect firewall and compute instances
- Update VPC module first
- Ensure dependent modules use new outputs
- Consider IP range changes carefully (may recreate resources)

### 6. Security Considerations

**Current Security Posture:**
- Firewall allows `0.0.0.0/0` (public access) on port 80
- Resources use default service accounts
- State stored in GCS (ensure proper IAM)
- No secrets management implementation

**When Adding Security Features:**
- Consider using Secret Manager for sensitive values
- Implement least-privilege IAM roles
- Restrict firewall rules to specific source ranges
- Enable VPC Flow Logs for network monitoring
- Consider Cloud Armor for DDoS protection

### 7. Terraform State Management

**Important:**
- State is stored remotely in GCS
- Never commit `terraform.tfstate` files
- Each environment has isolated state
- State bucket must exist before `terraform init`

**When Working with State:**
- Always use `terraform init` before operations
- Be cautious with `terraform destroy`
- Consider state locking for concurrent operations
- Backup state before major changes

### 8. Testing Strategy

**Local Testing:**
```bash
# Plan changes
cd environments/dev
terraform init
terraform plan

# Apply to dev first
terraform apply

# Verify
# Check GCP console for resources

# Then promote to prod
cd ../prod
terraform init
terraform plan
terraform apply
```

**CI/CD Testing:**
- Create feature branch
- Push changes
- Check Cloud Build logs for plan output
- Merge to `dev` for deployment
- Test in dev environment
- Merge to `prod` for production deployment

### 9. Documentation Updates

When making changes, update:
- This CLAUDE.md file (for structural changes)
- README.md (for user-facing changes)
- Inline comments in Terraform files
- Module variable descriptions

### 10. Code Style

**Terraform Style:**
- Use 2-space indentation
- Include license header in all files
- Add comments for complex logic
- Use descriptive variable names
- Group related resources together

**File Organization:**
```hcl
# Copyright header
# (blank line)
# Locals
# (blank line)
# Provider/Module/Resource blocks
```

## Quick Reference

### File Purposes

| File | Purpose |
|------|---------|
| `main.tf` | Primary resource/module definitions |
| `variables.tf` | Input variable declarations |
| `terraform.tfvars` | Variable value assignments |
| `outputs.tf` | Output value definitions |
| `backend.tf` | State backend configuration |
| `versions.tf` | Provider version constraints |

### Important Commands

```bash
# Initialize Terraform
terraform init

# Preview changes
terraform plan

# Apply changes
terraform apply

# Destroy infrastructure
terraform destroy

# Format code
terraform fmt

# Validate configuration
terraform validate
```

### Module Structure Pattern

```hcl
module "{module_name}" {
  source  = "../../modules/{module_name}"
  project = "${var.project}"
  # ... other variables
}
```

## Troubleshooting Common Issues

### State Lock Errors
- Another operation may be in progress
- Check Cloud Build for running jobs
- Wait for completion or break lock if necessary

### Backend Initialization Errors
- Verify GCS bucket exists
- Check IAM permissions on bucket
- Ensure correct bucket name in `backend.tf`

### Module Not Found
- Check relative path in `source` attribute
- Ensure module directory exists
- Run `terraform init` after adding modules

### Terraform Version Mismatch
- This project uses Terraform 0.11.14
- Cloud Build uses `hashicorp/terraform:0.11.14` image
- Use same version locally for consistency

## Related Documentation

- [Google Cloud Terraform Tutorial](https://cloud.google.com/solutions/managing-infrastructure-as-code)
- [Terraform 0.11 Documentation](https://www.terraform.io/docs/language/index.html)
- [Google Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Contributing Guidelines](CONTRIBUTING.md)

## Project Metadata

- **License**: Apache 2.0
- **Copyright**: 2019 Google LLC
- **Terraform Version**: 0.11.14
- **Primary Cloud**: Google Cloud Platform
- **CI/CD**: Google Cloud Build

---

**Last Updated**: 2025-11-19
**Repository**: solutions-terraform-cloudbuild-gitops
