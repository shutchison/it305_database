# This code was a collaboration effort and has been brought to you by:
# The Man, the Myth, The Legend, Jason Hussey (perhaps you've heard of him)
# and The Irascible Scott Hutchison

import pypyodbc
from pprint import pprint
from named_tuples_definitions import *
import time

# The Hutchison-Hussey (in that order) database class definition.
class HH_Database(object):
    def __init__(self, path_to_database):
        self.path_to_database = path_to_database
        
        self.tables = []
        self.statistics = {} # key: table_name, value: list of table_statistics namedtuples
        self.columns = {} # key: table_name, value: list of column namedtuples
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
                
                ### HERE IS WHERE IT IS!!!
                
                for stat in list(table_cursor.statistics(t.name)):
                    stat = table_statistic(*stat)
                    if t.name not in self.statistics:
                        self.statistics[t.name] = [stat]
                    else:
                        self.statistics[t.name].append(stat)
                
                for col in list(table_cursor.columns(t.name)):
                    col = column(*col)
                    if t.name not in self.columns:
                        self.columns[t.name] = [col]
                    else:
                        self.columns[t.name].append(col)
                        
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
        return_string += "Statistics are:\n"
        return_string += "-"*30 + "\n"
        for k,v in self.statistics.items():
            return_string += "- " + str(k) + "\n"
            for stat in v:
                return_string += "    - " + str(stat) + "\n"
            return_string += "\n"
        return_string += "\n"

        return_string += "-"*30 + "\n"
        return_string += "Columns are:\n"
        return_string += "-"*30 + "\n"
        for k,v in self.columns.items():
            return_string += "- " + str(k) + "\n"
            for col in v:
                return_string += "    - " + str(col) + "\n"
            return_string += "\n"
        return_string += "\n"

        return_string += "-"*30 + "\n"
        return_string += "sql_queries are:\n"
        return_string += "-"*30 + "\n"
        for s in self.sql_queries:
            return_string += "- " + str(s) + "\n"
    
        return return_string
        
    def compare_tables(self, other, table_name):
        mismatch_found = False

        solution_table = self.get_namedtuple("tables", table_name)
        compare_table = other.get_namedtuple("tables", table_name)
        #print(solution_table)
        #print(compare_table)
        
        for field in solution_table._fields:
            if field == "catalog":
                #differnt database files are expected to have different names.
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
        print("************compare_statistics not working yet***********")
        #Clearly, this is Princess Leia...
        print("@(-_-)@ \"Help me Jason Hussey!  You\'re my only hope!\"") 
        print("************")
        return

        mismatch_found = False

        solution_stat_list = self.get_namedtuple("statistics", table_name)
        compare_stat_list = other.get_namedtuple("statistics", table_name)
        #print(solution_stat_list)
        #print(compare_stat_list)
        

        # making an assumption that they will be in the same order here...
        # not very robust...  On second thought, this will not work  :(
        for index, solution_stat in enumerate(solution_stat_list):
            print("comparing:")
            print(solution_stat)
            print(compare_stat_list[index])
            for field in solution_stat._fields:
                if field == "table_catalog":
                    continue
                if getattr(solution_stat, field) != getattr(compare_stat_list[index], field):
                    print("  -Mismatch detected in statistics!!!")
                    print("    -self's " + field + " value is   :", getattr(solution_stat, field))
                    print("    -others's " + field + " value is :", getattr(compare_stat_list[index], field))
                    mismatch_found = True
                else:
                    pass
                    #print(field, " matches")
        if not mismatch_found:
            print("  -Statistic fields all check out.  Hooah!")
        
    def compare_columns(self, other, table_name):
        mismatch_found = False

        #I don't know which fields you don't care about, but put them in 
        #this list of strings
        fields_to_ignore = ["table_catalog"]
        
        solution_col_list = self.get_namedtuple("columns", table_name)
        #pprint(solution_col_list)
        
        for solution_col in solution_col_list:
        
            compare_col = other.get_namedtuple("columns", table_name, solution_col.column_name)
            #print(compare_col)
        
            for field in solution_col._fields:
                if field in fields_to_ignore:
                    continue
                if getattr(solution_col, field) != getattr(compare_col, field):
                    if mismatch_found == False:
                        mismatch_found = True
                        print("  -Mismatched columns detected!")
                        print("    -" + solution_col.column_name, "does not match")
                    print("      -self's " + field + " value is   :", getattr(solution_col, field))
                    print("      -others's " + field + " value is :", getattr(compare_col, field))
                    
                else:
                    pass
                    #print(field, " matches")
        if not mismatch_found:
            print("  -Column fields all check out.  Hooah!")
        
    def compare_sql_queries(self, other):
        print("************compare_sql_queries not implemented yet***********")
        pass
        
    def get_namedtuple(self, tuple_name, name_of_table, name_of_column=""):
        if tuple_name == "tables":
            for table in self.tables:
                if table.name == name_of_table:
                    return table
        elif tuple_name == "statistics":
            return self.statistics[name_of_table]
        elif tuple_name == "columns":
            if name_of_column == "":
                return self.columns[name_of_table]
            else:
                for column in self.columns[name_of_table]:
                    if column.column_name == name_of_column:
                        return column

            
        else:
            print("No attribute named:", tuple_name)
            exit()
                        
solution_database_obj = HH_Database(r".\DBTEEverB_SOLN.ACCDB")    
cadet_database_obj = HH_Database(r".\DBTEEverB.ACCDB")

# With an overloaded str function, you can print the database!
print("==="*30)
print("Solution database is:")
print("==="*30)
print(solution_database_obj)
print("==="*30)
print("Cadet database is:")
print("==="*30)
print(cadet_database_obj)
print("==="*30)

solution_database_obj.set_tables_to_grade(['Cadet', 'CadetInTest', 'FitnessTests', 'Profile'])
solution_database_obj.compare_with_other(cadet_database_obj)

#
#for table, stat in solution_database_obj.statistics.items():
#    i = 0
#    print("-"*30)
#    print("for", table)
#    for field in stat._fields:
#    
#        print(i, "-",field, ":", getattr(stat, field))
#        i += 1
#
#for table, col in solution_database_obj.columns.items():
#    i = 0
#    print("-"*30)
#    print("for", table)
#    for field in col._fields:
#    
#        print(i, "-",field, ":", getattr(col, field))
#        i += 1

#for relationships, look in the statistics:
#if index_name == None, this table_statistic contains the statistics about that table.
#if index_name == PrimaryKey, this means that column name contains the primary key for this table. 
#sometimes is a combination of the two tables.  i.e. CadetCadetInTest  This is a foreign key 1-many from cadet to cadetInTest where the column name specifies what the foreign key is
#if index_name == a column on this table