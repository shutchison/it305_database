from collections import namedtuple

# explaination for what these mean is here:
# https://docs.microsoft.com/en-us/sql/odbc/reference/syntax/sqltables-function
table_argument_names = ["catalog",
                        "schema",
                        "name",
                        "type",
                        "remarks"]
table = namedtuple("table", table_argument_names)

# explaination for what these mean is here:
# https://docs.microsoft.com/en-us/sql/odbc/reference/syntax/sqlstatistics-function
statistic_argument_names = ["table_catalog", 
                          "table_schema",
                          "table_name",
                          "non_unique",
                          "index_qualifier",
                          "index_name",
                          "type",
                          "ordinal_position",
                          "column_name",
                          "asc_or_desc",
                          "cardinality",
                          "pages",
                          "filter_condition"]                         
table_statistic = namedtuple("table_statistic", statistic_argument_names)

# explaination for what these mean is here:
#https://docs.microsoft.com/en-us/sql/odbc/reference/syntax/sqlcolumns-function
column_argument_names = ["table_catalog",
                         "table_schema",
                         "table_name",
                         "column_name",
                         "data_type",
                         "type_name",
                         "column_size",
                         "buffer_length",
                         "decimal_digits",
                         "num_prec_radix",
                         "nullable",
                         "remarks",
                         "column_def",
                         "sql_data_type",
                         "sql_datetime_sub",
                         "char_octet_length",
                         "ordinal_position",
                         "is_nullable",
                         "unknown_thing_not_documented"] 
column = namedtuple("column", column_argument_names)

# https://docs.microsoft.com/en-us/sql/odbc/reference/syntax/sqlprimarykeys-function
primary_key_argument_names = ["table_cat",
                              "table_schema",
                              "table_name",
                              "column_name",
                              "key_seq",
                              "pk_name"]
primary_key = namedtuple("primary_key", primary_key_argument_names)

# https://docs.microsoft.com/en-us/sql/odbc/reference/syntax/sqlforeignkeys-function
foreign_key_argument_names = ["pktable_cat",
                              "pktable_schema",
                              "pktable_name",
                              "pkcolumn_name",
                              "fktable_cat",
                              "fktable_schema",
                              "fktable_name",
                              "fkcolumn_name",
                              "key_seq",
                              "update_rule",
                              "delete_rule",
                              "fk_name",
                              "pk_name",
                              "deferrability"]
foreign_key = namedtuple("foreign_key", foreign_key_argument_names)