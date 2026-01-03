# 🧩 Part 3 – Full Schema Synchronization (PRO → PRE)

## 📌 Overview

This notebook implements the **final synchronization layer** of the Hive Data Model lifecycle, ensuring that **PRE accurately reflects PRO** in terms of structure, object types, and metadata.

It consumes:
- The **DDL registry extracted from PRO** (Part 1)
- The **schema comparison results** between PRO and PRE (Part 2)

And produces:
- A **safe, auditable synchronization plan**
- SQL statements to **create or evolve tables and views**
- A detailed execution report

> ⚠️ This notebook **must be executed in the PRE environment**.

---

## 🎯 Objectives

- Synchronize **schemas, tables, and views** from PRO to PRE
- Automatically adapt **EXTERNAL table locations**
- Handle **partitioned tables**, **views**, and **schema evolution**
- Generate a **controlled execution plan** with risk classification
- Support **dry-run mode** for safe validation

---

## 🧱 Supported Object Types

| Object Type | Supported | Notes |
|------------|----------|------|
| Managed Tables | ✅ | Full CREATE and ALTER support |
| External Tables | ✅ | LOCATION automatically adapted |
| Partitioned Tables | ✅ | Partition columns preserved |
| Views | ✅ | Created with adapted DDL |
| Temporary / Backup Objects | 🚫 | Explicitly excluded |

---

## ⚙️ Configuration

The notebook is fully parameterized through a configuration block:

### Execution Control
- **Dry Run Mode** – simulate changes without executing them
- **Target Environment** – PRE

### Metadata Sources
- Schema comparison results table
- DDL registry table from PRO
- Synchronization execution log table

### Storage Mapping
Used only for **EXTERNAL tables**:
- PRO storage identifier
- PRE storage identifier

### Automatic Exclusions
Regex-based exclusion of:
- Backup tables
- Temporary tables
- Test / development artifacts
- Non-governed schemas

This ensures only **production-grade, authoritative objects** are synchronized.

---

## 🔍 Step-by-Step Logic

### 1️⃣ Load Metadata Inputs

- Latest schema comparison analysis
- DDL registry extracted from PRO
- Filters only tables that **require action**

---

### 2️⃣ DDL Analysis

For each object, the notebook detects:

- Object type (TABLE / VIEW)
- External vs managed
- Partitioned tables
- Partition columns
- LOCATION (if external)

This metadata drives the synchronization strategy.

---

### 3️⃣ DDL Adaptation (PRO → PRE)

For **EXTERNAL tables only**:
- The `LOCATION` path is rewritten
- Storage identifiers are mapped from PRO to PRE
- Table structure remains **identical**

Managed tables and views are **not modified structurally**.

---

### 4️⃣ Synchronization Strategy Generation

Based on the comparison results, one of the following actions is generated:

#### 🆕 CREATE
- Create database (if missing)
- Create table or view using adapted DDL

#### 🔧 UPDATE_SCHEMA
- Add missing columns (single `ALTER TABLE ADD COLUMNS`)
- Change column types (when compatible)
- Flag incompatible changes for manual migration

#### ✅ NO_ACTION
- Table already synchronized

---

### 5️⃣ Schema Evolution Rules

#### ➕ Add Columns
- Multiple columns added in a **single ALTER TABLE**
- Partition columns are automatically excluded

#### 🔄 Change Column Types
- Compatible changes handled automatically
- Complex changes generate **manual migration guidance**

No columns are ever **dropped automatically**.

---

### 6️⃣ Risk Classification

Each synchronization plan is classified:

| Risk Level | Meaning |
|-----------|--------|
| LOW | Safe automated change |
| MEDIUM | Structural change (external / partitioned) |
| HIGH | Manual intervention required |

This allows controlled execution and governance review.

---

## 📋 Synchronization Plan Output

For each table, the plan includes:

- Target database and table
- Object type
- Action type
- Generated SQL statements
- Schema changes
- Partition metadata
- Risk level
- Manual review flag
- Human-readable notes

Plans are generated **before any execution**.

---

## 🔎 Review & Filtering

The notebook provides:
- Action-based filtering (CREATE / UPDATE)
- Object-type filtering (VIEW / EXTERNAL / PARTITIONED)
- High-risk focus view
- Statement previews (safe inspection)

This enables **full transparency before execution**.

---

## 🧪 Dry Run Mode

When `dry_run = true`:
- No SQL is executed
- All statements are generated and logged
- Risk and impact can be reviewed safely

This is the **recommended default mode**.

---

## 📤 Final Outputs

✅ Complete synchronization plan  
✅ Adapted SQL statements (PRO → PRE)  
✅ Risk and governance metadata  
✅ Ready-to-execute migration logic  

---

## 🧩 Position in the Data Model Lifecycle

