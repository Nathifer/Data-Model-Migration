## 🧩 Part 1 – DDL Extraction (WORKSPACE PRO)

### 🎯 Objective

Create a **structured metadata registry** representing the complete Hive data model in **PRO**.

---

### 🛠 What Part 1 Does

#### ⚙️ 1. Parameter Configuration

Configurable parameters control the extraction behavior:

- Databases to scan
- Tables to exclude (regex patterns)
- Target metadata database
- Target Delta table
- Environment identifier (e.g. `PRO`)

This makes the process reusable and environment-agnostic.

---

#### 🗄 2. Metadata Database Initialization

- Creates a dedicated metadata database if it does not exist
- Ensures clear governance separation from business data

---

#### 🔍 3. Database & Table Discovery

- Processes configured databases (or all available databases)
- Excludes system databases
- Skips temporary and backup tables

This guarantees only relevant user objects are analyzed.

---

#### 📜 4. Table-Level Metadata Extraction

For every eligible table, the process extracts:

- `SHOW CREATE TABLE` → full DDL
- `DESCRIBE EXTENDED` → structure and table properties

Captured metadata includes:
- Columns
- Partition columns
- Storage and provider metadata

Each extraction is tracked with a status:

- ✅ **SUCCESS**
- ❌ **ERROR** (with detailed error information)

---

#### 💾 5. Delta Metadata Storage

All extracted metadata is stored in a **Delta table** using a structured schema:

| Field              | Description                     |
|--------------------|---------------------------------|
| `database`         | Database name                   |
| `table_name`       | Table name                      |
| `full_table_name`  | Fully qualified table name      |
| `ddl`              | Full `CREATE TABLE` statement   |
| `columns`          | JSON column metadata            |
| `partition_columns`| JSON partition metadata         |
| `table_properties` | JSON table properties           |
| `extracted_at`     | Extraction timestamp            |
| `environment`      | Environment identifier (`PRO`)  |
| `status`           | `SUCCESS` / `ERROR`             |

---

#### 🔎 6. Validation & Sampling

- Sample DDL inspection
- Per-database extraction statistics
- Error surfacing and diagnostics
- Helper views for analytical queries

These steps ensure data quality and extraction completeness.

---

### 📤 Output of Part 1

- ✅ Delta table containing the **complete PRO Hive data model**
- ✅ Fully queryable and auditable metadata registry
- ✅ Ready for export and consumption in **WORKSPACE PRE**
