# Databricks notebook source
# MAGIC %md
# MAGIC # Part 1: DDL Extraction from PRO Environment
# MAGIC 
# MAGIC This notebook extracts DDLs from all tables in the PRO environment and stores them in a Delta table.
# MAGIC 
# MAGIC **Steps:**
# MAGIC 1. Configure parameters
# MAGIC 2. Extract table DDLs
# MAGIC 3. Persist metadata in a Delta table
# MAGIC 4. Validate storage

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Parameter Configuration

# COMMAND ----------

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, ArrayType
from pyspark.sql.functions import col, lit, current_timestamp, to_json, struct
from datetime import datetime
import json

# Configurable parameters
CONFIG = {
    'catalog': 'hive_metastore',  # Hive catalog
    'databases_to_extract': ['default', "backup_db", "db_backup", "temp_schema","*bkp.*",'.*backup.*',,"test_environment","old_database","dev_schema"],  # List of databases or None for all
    'exclude_tables': ['tmp_.*', 'temp_.*', '.*_backup', '.*bkp.*', '.*backup.*', '.*temp.*', '.*tmp.*', '.*clone.*', '.*test.*', '.*old.*', '.*dev.*'],  # Regex patterns to exclude
    'target_database': 'metadata',  # Database to store DDL metadata
    'target_table': 'ddl_registry_pro',  # Target Delta table
    'environment': 'PRO'  # Environment identifier
}

# Display configuration
print("=" * 80)
print("PROCESS CONFIGURATION")
print("=" * 80)
for key, value in CONFIG.items():
    print(f"{key}: {value}")
print("=" * 80)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Create Metadata Database (If Not Exists)

# COMMAND ----------

# Create metadata database if it does not exist
spark.sql(f"CREATE DATABASE IF NOT EXISTS {CONFIG['target_database']}")
print(f"✅ Database {CONFIG['target_database']} verified/created")

# List available databases
print("\n📂 Available databases:")
spark.sql("SHOW DATABASES").show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Get List of Databases to Process

# COMMAND ----------

def get_databases_to_process(databases_list=None):
    """Returns the list of databases to process"""
    if databases_list is None or len(databases_list) == 0:
        databases_df = spark.sql("SHOW DATABASES")
        databases = [row.databaseName for row in databases_df.collect()]
        print(f"📂 Processing ALL databases ({len(databases)} found)")
    else:
        databases = databases_list
        print(f"📂 Processing specific databases: {databases}")
    
    # Exclude system databases
    system_databases = ['information_schema', 'sys']
    databases = [db for db in databases if db not in system_databases]
    
    return databases

databases_to_process = get_databases_to_process(CONFIG['databases_to_extract'])

print(f"\n✅ Databases to process ({len(databases_to_process)}):")
for db in databases_to_process:
    print(f"  - {db}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Function to Extract Table DDL

# COMMAND ----------

import re

def should_exclude_table(table_name, exclude_patterns):
    """Checks whether a table should be excluded based on regex patterns"""
    if not exclude_patterns:
        return False
    
    for pattern in exclude_patterns:
        if re.match(pattern, table_name):
            return True
    return False

def extract_table_ddl(database, table_name):
    """
    Extracts DDL and metadata for a specific table
    
    Returns:
        dict containing table metadata or error information
    """
    full_table_name = f"{database}.{table_name}"
    
    try:
        # Get DDL
        ddl_result = spark.sql(f"SHOW CREATE TABLE {full_table_name}")
        ddl = ddl_result.collect()[0].createtab_stmt
        
        # Get extended schema information
        describe_result = spark.sql(f"DESCRIBE EXTENDED {full_table_name}")
        schema_rows = describe_result.collect()
        
        columns = []
        partition_cols = []
        table_properties = {}
        is_partition_section = False
        
        for row in schema_rows:
            col_name = row.col_name.strip() if row.col_name else ""
            data_type = row.data_type.strip() if row.data_type else ""
            
            if col_name == "# Partition Information":
                is_partition_section = True
                continue
            
            if col_name in ["", "# col_name"] or col_name.startswith("#"):
                continue
            
            if col_name in ["Location", "Provider", "Type", "Table Properties"]:
                table_properties[col_name] = data_type
                continue
            
            if is_partition_section:
                partition_cols.append({"name": col_name, "type": data_type})
            else:
                columns.append({"name": col_name, "type": data_type})
        
        return {
            'database': database,
            'table_name': table_name,
            'full_table_name': full_table_name,
            'ddl': ddl,
            'columns': columns,
            'partition_columns': partition_cols,
            'table_properties': table_properties,
            'extracted_at': datetime.now().isoformat(),
            'environment': CONFIG['environment'],
            'status': 'SUCCESS'
        }
        
    except Exception as e:
        print(f"  ❌ Error extracting {full_table_name}: {str(e)}")
        return {
            'database': database,
            'table_name': table_name,
            'full_table_name': full_table_name,
            'ddl': None,
            'columns': [],
            'partition_columns': [],
            'table_properties': {},
            'extracted_at': datetime.now().isoformat(),
            'environment': CONFIG['environment'],
            'status': 'ERROR',
            'error_message': str(e)
        }

# Extraction test (adjust table name as needed)
print("🧪 Extraction test:")
test_result = extract_table_ddl('default', 'test_table')
if test_result:
    print(f"✅ Test successful for: {test_result['full_table_name']}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Extract DDLs from All Tables

# COMMAND ----------

from pyspark.sql import Row

def extract_all_ddls(databases, exclude_patterns):
    """
    Extracts DDLs from all tables in the specified databases
    
    Returns:
        list of dicts containing table metadata
    """
    all_ddls = []
    total_tables = 0
    success_count = 0
    error_count = 0
    excluded_count = 0
    
    print("=" * 80)
    print("EXTRACTING TABLE DDLs")
    print("=" * 80)
    
    for database in databases:
        print(f"\n📂 Database: {database}")
        
        try:
            tables_df = spark.sql(f"SHOW TABLES IN {database}")
            tables = tables_df.collect()
            
            print(f"   Tables found: {len(tables)}")
            
            for table_row in tables:
                table_name = table_row.tableName
                total_tables += 1
                
                if should_exclude_table(table_name, exclude_patterns):
                    print(f"  ⏭️  Skipped: {table_name}")
                    excluded_count += 1
                    continue
                
                print(f"  🔄 Processing: {table_name}...", end=" ")
                table_info = extract_table_ddl(database, table_name)
                
                if table_info:
                    all_ddls.append(table_info)
                    if table_info['status'] == 'SUCCESS':
                        print("✅")
                        success_count += 1
                    else:
                        print("❌")
                        error_count += 1
                        
        except Exception as e:
            print(f"  ❌ Error processing database {database}: {str(e)}")
            error_count += 1
    
    print("\n" + "=" * 80)
    print("EXTRACTION SUMMARY")
    print("=" * 80)
    print(f"📊 Total tables found: {total_tables}")
    print(f"✅ Successful extractions: {success_count}")
    print(f"❌ Errors: {error_count}")
    print(f"⏭️  Excluded tables: {excluded_count}")
    print("=" * 80)
    
    return all_ddls

extracted_ddls = extract_all_ddls(databases_to_process, CONFIG['exclude_tables'])
print(f"\n✅ Total DDLs extracted: {len(extracted_ddls)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Validate Extracted Data

# COMMAND ----------

if len(extracted_ddls) > 0:
    print("🔍 SAMPLE EXTRACTED DDL:")
    print("=" * 80)
    example = extracted_ddls[0]
    print(f"Database: {example['database']}")
    print(f"Table: {example['table_name']}")
    print(f"Status: {example['status']}")
    print(f"Number of columns: {len(example['columns'])}")
    print("\nFirst 3 columns:")
    for col in example['columns'][:3]:
        print(f"  - {col['name']}: {col['type']}")
    print("\nDDL (first 500 characters):")
    print(example['ddl'][:500] if example['ddl'] else "N/A")
    print("=" * 80)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Convert to Spark DataFrame

# COMMAND ----------

from pyspark.sql.types import StructType, StructField, StringType

schema = StructType([
    StructField("database", StringType(), False),
    StructField("table_name", StringType(), False),
    StructField("full_table_name", StringType(), False),
    StructField("ddl", StringType(), True),
    StructField("columns", StringType(), True),
    StructField("partition_columns", StringType(), True),
    StructField("table_properties", StringType(), True),
    StructField("extracted_at", StringType(), False),
    StructField("environment", StringType(), False),
    StructField("status", StringType(), False),
    StructField("error_message", StringType(), True)
])

def prepare_for_dataframe(ddl_list):
    prepared_data = []
    for ddl in ddl_list:
        prepared_data.append({
            'database': ddl['database'],
            'table_name': ddl['table_name'],
            'full_table_name': ddl['full_table_name'],
            'ddl': ddl['ddl'],
            'columns': json.dumps(ddl['columns']),
            'partition_columns': json.dumps(ddl['partition_columns']),
            'table_properties': json.dumps(ddl['table_properties']),
            'extracted_at': ddl['extracted_at'],
            'environment': ddl['environment'],
            'status': ddl['status'],
            'error_message': ddl.get('error_message')
        })
    return prepared_data

ddl_df = spark.createDataFrame(prepare_for_dataframe(extracted_ddls), schema)

print("✅ DataFrame created successfully")
print(f"📊 Record count: {ddl_df.count()}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Save as Delta Table

# COMMAND ----------

full_target_table = f"{CONFIG['target_database']}.{CONFIG['target_table']}"

print(f"💾 Saving DDLs to Delta table: {full_target_table}")

ddl_df.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(full_target_table)

print(f"✅ Delta table {full_target_table} created/updated")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9. Validate Delta Table

# COMMAND ----------

saved_df = spark.table(full_target_table)

print(f"📊 Records: {saved_df.count()}")
saved_df.groupBy("database", "status").count().show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 10. Example Query: Inspect Table DDL

# COMMAND ----------

example_table = "default.my_table"

print(f"🔍 Querying DDL for: {example_table}")

result = saved_df.filter(col("full_table_name") == example_table).collect()

if result:
    row = result[0]
    print(row.ddl)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 11. Final Summary

# COMMAND ----------

print("=" * 80)
print("✅ PROCESS COMPLETED SUCCESSFULLY")
print("=" * 80)
print(f"📊 Delta table created: {full_target_table}")
print(f"📈 Total records: {saved_df.count()}")
print(f"✅ Successful extractions: {saved_df.filter(col('status') == 'SUCCESS').count()}")
print(f"❌ Errors: {saved_df.filter(col('status') == 'ERROR').count()}")
print("\n📝 Next steps:")
print("   1. Review the metadata table")
print("   2. Run Part 2: Comparison with PRE")
print("   3. Run Part 3: Synchronization")
print("=" * 80)
