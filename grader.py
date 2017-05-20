import pypyodbc
import difflib
import pprint as pp
from collections import namedtuple


def parse_tables(table_list, cursor):
    table_dict = {}
    Column = namedtuple('Column', 'name, type, size')
    Relationship = namedtuple('Relationship', 'relatedTable, foreignKey')

    for table in table_list:
        table_dict[table] = {}
        # Collect primary keys and relationships
        for row in cursor.statistics(table):
            # print(row)
            # grab the primary keys, store results in each table's dict as a list with 'primaryKey' as the key
            if row[3] == 0:
                try:
                    table_dict[table]['primaryKey'].append(row[8])
                except KeyError:
                    table_dict[table]['primaryKey'] = [row[8]]
            elif row[3] == 1:
                # store related table and foreign key as named tuple in table's dict with 'relations' as key
                r = Relationship(row[5].replace(row[2], '', 1), row[8])
                try:
                    table_dict[table]['relations'].append(r)
                except KeyError:
                    table_dict[table]['relations'] = [r]
            else:
                pass
        # Collect column info (data types, names, lengths, etc.
        for column in cursor.columns(table):
            # print(column)
            c = Column(column[3], column[5], column[6])
            # print(c)
            try:
                table_dict[table]['fields'].append(c)
            except:
                table_dict[table]['fields'] = [c]

    return table_dict


def grade_tables(sol_table, cdt_table, table, points):
    # this function ought to return a dictionary {table_name: named_tuple_with_grades)
    # the named tuple should have grades for fields, data types, primary keys, relationships, table name/created


    if 'fields' in cdt_table:
        cadet_field_names = [x.name for x in cdt_table['fields']]

        for field in sol_table['fields']:
            if field.name in cadet_field_names:
                print('{} found in cadet {} table'.format(field.name, table))
            else:
                print('{} missing from {} table'.format(field.name, table))
                closest_match = difflib.get_close_matches(field.name, cadet_field_names, 1, 0.8)[0]
                print('--{} is closest match!'.format(closest_match))

    else:
        print('Cadet did not have {} table'.format(table))
    # for each Column in solutionTables[tableName]['fields']
        # if fieldName in [x.name for x in solTables[tableName]['fields']]
            # award base points for field creation
            # if datatype matches:
                # award data type points
                # if size matches:
                    # award size points
                # elif record no siz match
            # elif record no data type match
        # else record no fieldName match

    return {}


def main():

    path = r'.\DBProject172_Solution.accdb'
    tables_to_grade = ['APFT', 'SoldierCompletesTraining', 'OnlineTraining']
    cadet_grade = {}

    # Connect to the solution file
    solConn = pypyodbc.connect(r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};" + "Dbq={0};".format(path))
    solCur = solConn.cursor()

    # Parse the solution for table parameters of tables_to_grade
    solTables = parse_tables(tables_to_grade, solCur)

    # All done with solution file
    solConn.close()

    # Connect to the current cadet's database
    path = r'.\DBProject172_harvie.accdb'
    cdtConn = pypyodbc.connect(r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};" + "Dbq={0};".format(path))
    cdtCur = cdtConn.cursor()

    cdtTables = parse_tables(tables_to_grade, cdtCur)
    cdtConn.close()

    for table in tables_to_grade:
        grade_tables(solTables[table], cdtTables[table], table, 10)

    # print('----------------SOLUTION------------------')
    # pp.pprint(solTables)
    # print('----------------CADET------------------')
    # pp.pprint(cdtTables)


if __name__ == '__main__':
    main()




# solTables[ttc] =

# solCur.execute('''
# SELECT * FROM Soldier;
# ''')

'''
column name (or alias, if specified in the SQL)
type code
display size (pyodbc does not set this value)
internal size (in bytes)
precision
scale
nullable (True/False)
'''


# for d in solCur.description:
#     print(d)

# solTables = [x for x in solCur.tables(tableType='TABLE')]
# for table in solTables:
#     print(table['table_name'])
#     columns = [x for x in solCur.columns(table=table['table_name'])]
#     for col in columns:
#         print(col[3], col[5], col[6])



# for row in solCur.fetchall():
#     print(row['soldierssn'])
