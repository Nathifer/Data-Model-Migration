# 🧩 Part 2 – Schema Comparison(WORKSPACE PRE)

## 🎯 Objective

Compare the Hive metadata extracted from **WORKSPACE PRO** (Part 1 output) against the actual tables in **WORKSPACE PRE** in order to:

- Detect schema drift
- Identify missing or divergent tables
- Decide what synchronization action is required

⚠️ **Important:**  
Part 2 is a **read-only, analytical step**.  
It **does NOT create or modify any tables**.

---

## 🛠 What Part 2 Does

---

## ⚙️ 1. Configuration & Inputs

Part 2 consumes the metadata registry produced in **Part 1** and defines comparison behavior via configuration:

- Source metadata table (PRO snapshot)
- Target environment (PRE)
- Database and table exclusion patterns
- Comparison rules (columns, partitions, types)

This keeps the process **environment-agnostic** and reusable.

---

## 🗄 2. Load PRO Metadata Registry

The process reads the Delta table generated in Part 1, which represents the **authoritative Hive model from PRO**.

This table acts as:
- A frozen snapshot of PRO
- The single source of truth for comparison
- A fully auditable metadata reference

No direct connection to PRO is required.

---

## 🔍 3. Target Discovery in PRE

For each table defined in the PRO metadata registry, the process checks:

- Does the database exist in PRE?
- Does the table exist in PRE?

This establishes whether the object:
- Already exists
- Is missing
- Requires deeper comparison

---

## 🚫 4. Automatic Exclusions

To ensure clean and meaningful comparisons, non-business objects are excluded.

### 4.1 Excluded Databases / Schemas

Databases matching patterns such as the following are ignored:

- backup environments
- temporary schemas
- development-only schemas
- historical or deprecated databases

These environments are considered **non-authoritative** and outside governance scope.

---

### 4.2 Excluded Tables (by Name Pattern)

Tables matching typical non-business patterns are skipped:

- backups
- temporary tables
- test artifacts
- clones
- deprecated versions

This avoids false positives and unnecessary noise.

---

## 🧾 5. PRE Table Schema Extraction

For tables that exist in PRE, the process extracts the **actual physical schema** using SQL introspection.

Captured information includes:
- Column names
- Data types
- Partition columns

System metadata and technical fields are filtered out to ensure a fair comparison.

---

## 🧹 6. Schema Normalization

Before comparison, both PRO and PRE schemas are normalized:

- Metadata rows are removed
- Partition columns are handled separately
- Column names and types are standardized

This guarantees that differences detected are **real schema differences**, not formatting artifacts.

---

## 🔎 7. Schema Comparison Engine

This is the core logic of Part 2.

For each table, the engine compares:
- Columns present in PRO but missing in PRE
- Columns present in PRE but not in PRO
- Columns with mismatched data types

The comparison is **structural**, not semantic.

---

## ⚖️ 8. Drift Classification

Based on comparison results, each table is assigned a clear action:

| Action | Meaning |
|------|--------|
| `NO_ACTION` | PRE table matches PRO |
| `CREATE_TABLE` | Table exists in PRO but not in PRE |
| `UPDATE_SCHEMA` | Table exists but schema differs |
| `ERROR` | Table could not be analyzed |

This transforms raw differences into **actionable decisions**.

---

## 📊 9. Result Aggregation & Metrics

The process generates:
- Per-action statistics
- Counts of impacted tables
- High-level visibility of schema drift

This allows teams to assess **impact before applying changes**.

---

## 📋 10. Output of Part 2

The final output is a **comparison result dataset** containing:

- Table identity
- Detected differences
- Required action
- Diagnostic information

This dataset is designed to be **directly consumed by Part 3**.

---

## 🚦 What Part 2 Does NOT Do

❌ No table creation  
❌ No schema alteration  
❌ No data movement  

Part 2 is **safe, read-only, and fully auditable**.

---

## 🧠 Summary

👉 **Part 2 answers one question clearly:**

> *“What is different between PRO and PRE, and what should be done about it?”*

It provides a deterministic, explainable bridge between:
- **Metadata extraction (Part 1)**  
- **Physical synchronization (Part 3)**

---

## 🔜 Next Step

➡️ **Part 3 – Schema Synchronization (WORKSPACE PRE)**  
Applies the actions identified in Part 2 to bring PRE in line with PRO.
