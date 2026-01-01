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

#### 🚫 4.  Automatic Exclusions

To ensure clean and relevant metadata extraction, the process automatically excludes **non-business, temporary, backup, and development artifacts**.

---

##### 🧾 4.1 Excluded Tables (by Name Pattern)

Any table matching the following patterns is **automatically excluded**, regardless of the database:

| Pattern     | Example Table Names                    |
|------------|----------------------------------------|
| `bkp`      | `table_bkp`, `bkp_table`               |
| `backup`   | `table_backup`, `backup_2023`          |
| `temp`     | `temp_staging`, `table_temp`           |
| `tmp`      | `tmp_process`, `table_tmp`             |
| `clone`    | `table_clone`, `clone_test`            |
| `test`     | `test_table`, `table_test`             |
| `old`      | `old_version`, `table_old`             |
| `dev`      | `dev_table`                            |

These patterns typically represent:
- Temporary or intermediate tables
- Backups or historical copies
- Clones created for testing
- Development-only artifacts

---

##### 🗄 4.2 Excluded Databases / Schemas

The following databases or schemas are **fully excluded** from processing:

- `backup_db`
- `db_backup`
- `temp_schema`
- `bkp_`
- `test_environment`
- `old_database`

These environments are considered **non-authoritative** and are not part of the governed Hive model.

---

##### 📋 4.3 Explicitly Excluded Tables (Inside Valid Databases)

Even within valid business databases, the following tables are explicitly excluded:

- `table_bkp`
- `staging_temp`
- `clone_process`

---

##### ✅ Resulting Behavior

- Only **governed, production-grade tables** are extracted
- Noise from backups, tests, and temporary objects is eliminated
- The resulting metadata registry reflects the **true PRO source of truth**

This exclusion logic ensures a **clean, stable, and auditable** Hive model reference for downstream comparison and synchronization.

---

#### 📜 5. Table-Level Metadata Extraction

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

#### 💾 6. Delta Metadata Storage

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

#### 🔎 7. Validation & Sampling

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
