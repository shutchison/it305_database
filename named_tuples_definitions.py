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
