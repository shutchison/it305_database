# This code was a collaboration effort and has been brought to you by:
# The Man, the Myth, The Legend, Jason Hussey (perhaps you've heard of him)
# and The Irascible Scott Hutchison

import pypyodbc
from pprint import pprint
from collections import namedtuple

def get_cursor(path_to_table):
    connect_string = r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};" + "Dbq={0};".format(path_to_table)
    #print(connect_string)
    connection =  pypyodbc.connect(connect_string)
    return connection.cursor()


solution_cursor = get_cursor(r".\DBTEEverB_SOLN.ACCDB")

row = namedtuple("row", "catalog, schema, name, type, remarks")
table = namedtuple("table", "table_cat, table_schem, table_name, non_unique, index_qualifier, index_name, type, ordinal_position, column_nameasc_or_desc, cardinality, pages, filter_condition, rows")

rows = []

for row in map(row._make, solution_cursor.tables()):
    if row.type != "SYSTEM TABLE":
        print(row)
        rows.append(row)
        
t = list(map(table._make, solution_cursor.statistics(rows[0].name)))[0]

print(t.table_name)