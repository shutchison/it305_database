# This code was a collaboration effort and has been brought to you by:
# The Man, the Myth, The Legend, Jason Hussey (perhaps you've heard of him)
# and The Irascible Scott Hutchison

import pypyodbc
from pprint import pprint
from named_tuples_definitions import *

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
        if self.tables_to_grade == []:
            print("***WARNING*** You haven't told me which tables to grade.  Call the set_tables_to_grade() method")
        else:
            with open(output_file_name, "wt") as out_file:
                # maybe pass our out_file to these methods so they can write to the file themselves?
                for table_to_grade in self.tables_to_grade:
                    print("-"*30)
                    print("Checking table:", table_to_grade)
                    print("-"*30)
                    self.compare_tables(other, table_to_grade)
                    self.compare_statistics(other, table_to_grade)
                    self.compare_columns(other, table_to_grade)
                    self.compare_sql_queries(other)
                    print()
            
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
        
    def compare_tables(self, other, table_name):
        mismatch_found = False

        solution_table = self.get_namedtuple_by_table_name("tables", table_name)
        compare_table = other.get_namedtuple_by_table_name("tables", table_name)
        #print(solution_table)
        #print(compare_table)
        
        for field in solution_table._fields:
            if field == "catalog":
                continue
            if getattr(solution_table, field) != getattr(compare_table, field):
                print(" -Mismatch detected in tables!!!")
                print("   -self's " + field + " value is   :", getattr(solution_table, field))
                print("   -others's " + field + " value is :", getattr(compare_table, field))
                mismatch_found = True
            else:
                pass
                #print(field, " matches")
        if not mismatch_found:
            print("  -Table fields all check out.  Hooah!")  

    def compare_statistics(self, other, table_name):
        mismatch_found = False

        solution_stat = self.get_namedtuple_by_table_name("statistics", table_name)
        compare_stat = other.get_namedtuple_by_table_name("statistics", table_name)
        #print(solution_stat)
        #print(compare_stat)
        
        for field in solution_stat._fields:
            if field == "table_catalog":
                continue
            if getattr(solution_stat, field) != getattr(compare_stat, field):
                print("  -Mismatch detected in statistics!!!")
                print("    -self's " + field + " value is   :", getattr(solution_stat, field))
                print("    -others's " + field + " value is :", getattr(compare_stat, field))
                mismatch_found = True
            else:
                pass
                #print(field, " matches")
        if not mismatch_found:
            print("  -Statistic fields all check out.  Hooah!")
        
    def compare_columns(self, other, table_name):
        mismatch_found = False

        solution_col = self.get_namedtuple_by_table_name("columns", table_name)
        compare_col = other.get_namedtuple_by_table_name("columns", table_name)

        #print(solution_col)
        #print(compare_col)
        
        for field in solution_col._fields:
            if field == "table_catalog":
                continue
            if getattr(solution_col, field) != getattr(compare_col, field):
                print("  -Mismatch detected in columns!!!")
                print("    -self's " + field + " value is   :", getattr(solution_col, field))
                print("    -others's " + field + " value is :", getattr(compare_col, field))
                mismatch_found = True
            else:
                pass
                #print(field, " matches")
        if not mismatch_found:
            print("  -Column fields all check out.  Hooah!")
        
    def compare_sql_queries(self, other):
        print("compare_sql_queries not implemented yet")
        pass
        
    def get_namedtuple_by_table_name(self, tuple_name, name_of_table):
        if tuple_name == "tables":
            for table in self.tables:
                if table.name == name_of_table:
                    return table
        elif tuple_name == "columns":
            for col in self.columns.values():
                if col.table_name == name_of_table:
                    return col
        elif tuple_name == "statistics":
            for stat in self.statistics.values():
                if stat.table_name == name_of_table:
                    return stat
        else:
            print("No attribute named:", tuple_name)
            exit()
                        
solution_database_obj = HH_Database(r".\DBTEEverB_SOLN.ACCDB")    
cadet_database_obj = HH_Database(r".\DBTEEverB.ACCDB")

# With an overloaded str function, you can print the database!
print(solution_database_obj)
print("==="*30)
print(cadet_database_obj)
print("==="*30)

solution_database_obj.set_tables_to_grade(['Cadet', 'CadetInTest', 'FitnessTests', 'Profile'])
solution_database_obj.compare_with_other(cadet_database_obj)



