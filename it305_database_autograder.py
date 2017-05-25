# This code was a collaboration effort and has been brought to you by:
# The Man, the Myth, The Legend, Jason Hussey (perhaps you've heard of him)
# and The Irascible Scott Hutchison

import pypyodbc
from pprint import pprint
from collections import namedtuple

# The Hutchison-Hussey (in that order) database class definition.
class HH_Database(object):
    def __init__(self, path_to_database):
        self.path_to_database = path_to_database
        
        self.tables = []
        self.statistics = {}
        self.columns = {}
        self.sql_queries = []
        
        self.tables_to_grade = []
        
        self.get_table_info()
        
    def set_tables_to_grade(self, tables_list):
        self.tables_to_grade = tables_list
        
    def get_table_info(self):
        """
        populates class varibles.     
        """
        table_cursor = self.get_cursor()
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

        for t in list(table_cursor.tables()):
            t = table(*t)
            if t.type == "TABLE":
                
                self.tables.append(t)
                self.statistics[t.name] = table_statistic(*list(table_cursor.statistics(t.name))[0])
                self.columns[t.name] = column(*list(table_cursor.columns(t.name))[0])
            elif t.type == "VIEW":
                self.sql_queries.append(t)

    
    def get_cursor(self):
        connect_string = r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};" + "Dbq={0};".format(self.path_to_database)
        #print(connect_string)
        connection =  pypyodbc.connect(connect_string)
        return connection.cursor()

    def compare_with_other(self, other, output_file_name = "compare_results.txt"):
        with open(output_file_name, "wt") as out_file:
            # maybe pass our out_file to these methods so they can write to the file themselves?
            self.compare_tables(other)
            self.compare_statistics(other)
            self.compare_columns(other)
            self.compare_sql_queries(other)
            
    def __repr__(self):
        return self.__class__.__name__ + "(" + repr(self.path_to_database) + ")"
        
    def __str__(self):
        return_string = ""
        return_string += "-"*30 + "\n"
        return_string += "Tables are:\n"
        return_string += "-"*30 + "\n"
        for t in self.tables:
            return_string += str(t)
            return_string += "\n"
        return_string += "\n"
        
        return_string += "-"*30 + "\n"
        return_string += "statistics are:\n"
        return_string += "-"*30 + "\n"
        for k,v in self.statistics.items():
            return_string += "- " + str(k) + ": " + str(v) + "\n"
        return_string += "\n"

        return_string += "-"*30 + "\n"
        return_string += "columns are:\n"
        return_string += "-"*30 + "\n"
        for k,v in self.columns.items():
            return_string += "- " + str(k) + ": " + str(v) + "\n"
        return_string += "\n"

        return_string += "-"*30 + "\n"
        return_string += "sql_queries are:\n"
        return_string += "-"*30 + "\n"
        for s in self.sql_queries:
            return_string += "- " + str(s) + "\n"
    
        return return_string
        
    def compare_tables(self, other):
        mismatch_found = False
        
        print("-"*30)
        print("Comparing tables")
        print("-"*30)
        if self.tables_to_grade == []:
            print("***WARNING*** You haven't told me which tables to grade.  Call the set_tables_to_grade() method")
        else:
            solution_table = None
            for table_to_grade in self.tables_to_grade:
                for table in self.tables:
                    if table.name == table_to_grade:
                        solution_table = table
                        break
                compare_table = None
                for other_table in other.tables:
                    if other_table.name == table_to_grade:
                        compare_table = other_table
                        break
                #print(solution_table)
                #print(compare_table)
                
                for field in solution_table._fields:
                    if field == "catalog":
                        continue
                    if getattr(solution_table, field) != getattr(compare_table, field):
                        print(" -Mismatch detected in " + table_to_grade + "!!!")
                        print("   -self's " + field + " value is   :", getattr(solution_table, field))
                        print("   -others's " + field + " value is :", getattr(compare_table, field))
                        mismatch_found = True
                    else:
                        pass
                        #print(field, " matches")
        if not mismatch_found:
            print(" -Tables all check out.  Hooah!")
        print("-"*30)
        print()   
    def compare_statistics(self, other):
        mismatch_found = False
        
        print("-"*30)
        print("Comparing statistics")
        print("-"*30)
        if self.tables_to_grade == []:
            print("***WARNING*** You haven't told me which tables to grade.  Call the set_tables_to_grade() method")
        else:
            solution_stat = None
            for table_to_grade in self.tables_to_grade:
                for stat in self.statistics.values():
                    if stat.table_name == table_to_grade:
                        solution_stat = stat
                        break
                compare_stat = None
                for other_stat in other.statistics.values():
                    if other_stat.table_name == table_to_grade:
                        compare_stat = other_stat
                        break
                #print(solution_stat)
                #print(compare_stat)
                
                for field in solution_stat._fields:
                    if field == "table_catalog":
                        continue
                    if getattr(solution_stat, field) != getattr(compare_stat, field):
                        print(" -Mismatch detected in " + table_to_grade + "!!!")
                        print("    -self's " + field + " value is   :", getattr(solution_stat, field))
                        print("    -others's " + field + " value is :", getattr(compare_stat, field))
                        mismatch_found = True
                    else:
                        pass
                        #print(field, " matches")
        if not mismatch_found:
            print(" -statistics all check out.  Hooah!")
        print("-"*30)
        print()
        
    def compare_columns(self, other):
        mismatch_found = False
        
        print("-"*30)
        print("Comparing columns")
        print("-"*30)
        if self.tables_to_grade == []:
            print("***WARNING*** You haven't told me which tables to grade.  Call the set_tables_to_grade() method")
        else:
            solution_col = None
            for table_to_grade in self.tables_to_grade:
                for col in self.columns.values():
                    if col.table_name == table_to_grade:
                        solution_col = col
                        break
                compare_col = None
                for other_col in other.columns.values():
                    if other_col.table_name == table_to_grade:
                        compare_col = other_col
                        break
                #print(solution_col)
                #print(compare_col)
                
                for field in solution_col._fields:
                    if field == "table_catalog":
                        continue
                    if getattr(solution_col, field) != getattr(compare_col, field):
                        print("  -Mismatch detected in " + table_to_grade + "!!!")
                        print("    -self's " + field + " value is   :", getattr(solution_col, field))
                        print("    -others's " + field + " value is :", getattr(compare_col, field))
                        mismatch_found = True
                    else:
                        pass
                        #print(field, " matches")
        if not mismatch_found:
            print("  -Columns all check out.  Hooah!")
        print("-"*30)
        print()
        
    def compare_sql_queries(self, other):
            print("compare_sql_queries not implemented yet")
            pass
    
solution_database_obj = HH_Database(r".\DBTEEverB_SOLN.ACCDB")    
cadet_database_obj = HH_Database(r".\DBTEEverB.ACCDB")

# With an overloaded str function, you can print the database!
print(solution_database_obj)

solution_database_obj.set_tables_to_grade(['Cadet', 'CadetInTest', 'FitnessTests', 'Profile'])
solution_database_obj.compare_with_other(cadet_database_obj)



