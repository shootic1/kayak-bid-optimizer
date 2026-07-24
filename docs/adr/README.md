# Architecture Decision Records (ADRs)

This directory records significant architectural decisions for KAYAK Bid
Optimizer Pro, in [MADR](https://adr.github.io/madr/)-style Markdown.

## Process

- Any significant architectural change lands with an ADR **in the same pull request**.
- Use [`0000-template.md`](0000-template.md) as the starting point; number sequentially.
- Once **Accepted**, an ADR is immutable — supersede it with a new ADR rather than editing it.

## Index

| ADR | Title | Status |
|-----|-------|--------|
| [0001](0001-monorepo-structure.md) | Monorepo structure | Accepted |
| [0002](0002-technology-stack.md) | Technology stack & version strategy | Accepted |
| [0003](0003-exact-version-pinning.md) | Exact version pinning & lock files | Accepted |
| [0004](0004-api-versioning.md) | API versioning (infra-unversioned / app-versioned) | Accepted |
| [0005](0005-clean-architecture-and-domain-layer.md) | Clean architecture & domain layer | Accepted |
| [0006](0006-shared-workspace-package.md) | Shared workspace package | Accepted |
| [0007](0007-reserved-async-processing.md) | Reserved async processing | Accepted |
| [0008](0008-deployment-architecture.md) | Deployment architecture | Accepted |
| [0009](0009-uv-python-dependency-management.md) | uv for Python dependency management | Accepted |
