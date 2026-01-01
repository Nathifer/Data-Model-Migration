# Hive Data Model Migration Across Workspaces (PRO → PRE)


This repository implements an automated, **DDL-driven process** to migrate and synchronize a Hive data model across **isolated workspaces**.

- **WORKSPACE PRO** → Source environment and *single source of truth*
- **WORKSPACE PRE** → Target environment to be aligned with PRO

The migration covers the full Hive data model:
- Schemas (databases)
- Tables
- Views
- Columns
- Data types and object definitions

The solution extracts DDLs from PRO, transfers them across workspaces, compares them with PRE, and applies only the required changes.

---

## Architecture & Workspace Isolation

The workspaces are **fully isolated**:
- No direct access between Hive metastores
- No cross-workspace queries

DDL transfer between environments is done via:
- Shared storage or CSV export / import

- Exporting DDLs from PRO

Because workspaces are isolated, DDLs must be transferred externally.

**Option A – Shared Storage**

- Write the Delta table (or a subset) to storage accessible by both workspaces

**Option B – CSV Export**

- Query the Delta table in PRO
- Export the results to CSV
- Import the CSV into WORKSPACE PRE

The exported dataset becomes the PRO reference inside PRE.

> ⚠️ PRO is never modified  
> ⚙️ All changes are applied only in PRE

---

## Workflow Overview
WORKSPACE PRO

└─ Part 1: Extract DDLs → Delta Table

├─ Export via Shared Storage

└─ Export via CSV
↓
WORKSPACE PRE

├─ Part 2: Import & Compare

└─ Part 3: Synchronize Model


## Benefits
- Clear separation of environments
- Safe migration across isolated workspaces
- Fully automated and repeatable process
- Reduced manual intervention and errors
- Traceability via Delta tables and stored DDLs

## Notes
- Always validate generated DDLs before running in critical environments
- Recommended to test in lower environments first
- Extendable to additional object types if required
