# This code was a collaboration effort and has been brought to you by:
# The Man, the Myth, The Legend, Jason Hussey (perhaps you've heard of him)
# and The Irascible Scott Hutchison

import pypyodbc
from pprint import pprint
from named_tuples_definitions import *
from operator import itemgetter
import difflib

# The Hutchison-Hussey (in that order) database class definition.
class HH_Database(object):
    """
    Provides a class which enables the comparison of two different Microsoft
    Access Databases.  Descriptive differences between the two are displayed
    to the screen and will eventually be written to a file.
    
    Use case is to provide a solution database, and compare that to a student
    submission.  This allows for easy grading of student submissions to 
    required database projects.
    
    i.e.:
    >>> solution_database_obj = HH_Database(r".\DBTEEverB_SOLN.ACCDB")
    >>> cadet_database_obj = HH_Database(r".\DBTEEverB.ACCDB")
    >>> solution_database_obj.set_tables_to_grade(['Cadet', 'CadetInTest', 'FitnessTests', 'Profile'])
    >>> solution_database_obj.compare_with_other(cadet_database_obj)
    
    """
    def __init__(self, path_to_database):
        """
        Args:
        - path_to_database (str): The relative or absolute path to the Microsoft
            Access database that you'd like to open.
        
        Attributes:
        - path_to_database (str): Set to the same string as the argument
        - connection (pypyodbc connection object): the pypyodbc connection to the 
            database
        - database_cursor (pypyodbc cursor object): the pypyodbc cursor object for
            interacting with the database.
        - tables (list): A list of namedtuples of type table
        - statistics (dictionary): stores the cursor.statistic information of 
            each table in the database
                key: table_name (str)
                value: namedtuple object of type table_statistic
        - columns (dictionary): stores the cursor.column information for each
            column for each table in the database
                key: table_name (str)
                value: A list of namedtuples of type column
        - primary_keys (dictionary): stores the cursor.statistic information of
            the primary keys for each table in the database
                key: table_name (str)
                value: A list of namedtuples of type table_statistic
        - primary_keys (dictionary): stores the cursor.statistic information of
            the foreign keys for each table in the database
                key: table_name (str)
                value: A list of namedtuples of type table_statistic
        - sql_queries (list): A list of named tuples of type table.  Basically,
            these are cursor.tables() that have a type of "VIEW".
        - tables_to_grade (list): A list of strings of table_names that need to
            be compared.
        """
        self.path_to_database = path_to_database
        
        connect_string = r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};" + "Dbq={0};".format(self.path_to_database) 
        self.connection = pypyodbc.connect(connect_string)
        self.database_cursor = self.connection.cursor()

        self.tables = []
        self.statistics = {}
        self.columns = {}
        self.primary_keys = {}
        self.foreign_keys = {}
        self.sql_queries = []

        self.tables_to_grade = []
        
        self.get_table_info()
        
        #self.connection.close()
        
    def set_tables_to_grade(self, tables_list):
        """
        Allows the user to set the tables which will be compared.
        
        Args:
        tables_list (list): A list of strings which are the names of the tables
            that need to be compared.
        """
        self.tables_to_grade = tables_list
        
    def get_table_info(self):
        """
        Uses the cursor to populate the attributes for the class.  This method
            is called by the classes __init__ method.
        """
        for t in list(self.database_cursor.tables()):
            t = table(*t)
            if t.type == "TABLE":
                
                self.tables.append(t)

                for stat in list(self.database_cursor.statistics(t.name)):
                    stat = table_statistic(*stat)
                    if stat.non_unique == None:
                        self.statistics[t.name] = stat
                    #elif stat.non_unique == 0 and stat.table_name not in stat.index_name:
                    elif stat.index_name == "PrimaryKey":
                        if t.name not in self.primary_keys:
                            self.primary_keys[t.name] = [stat]
                        else:
                            self.primary_keys[t.name].append(stat)
                    elif stat.table_name in stat.index_name:
                        if t.name not in self.foreign_keys:
                            self.foreign_keys[t.name] = [stat]
                        else:
                            self.foreign_keys[t.name].append(stat)
                    #else:
                    #    print("Stat ignored:", stat)
                for col in list(self.database_cursor.columns(t.name)):
                    col = column(*col)
                    if t.name not in self.columns:
                        self.columns[t.name] = [col]
                    else:
                        self.columns[t.name].append(col)
                        
            elif t.type == "VIEW":
                self.sql_queries.append(t)
                
        self._remove_extraneous_fk_stats()
        
    def _remove_extraneous_fk_stats(self): 
        """ 
        Retains only foreign keys whose index_name is a combination of two table 
        names.  Discards the rest. 
        """ 
        table_names = [t.name for t in self.tables] 
        
        #Generate all possible combinations of two table names 
        table_name_combinations = [] 
        for i1, t1 in enumerate(table_names): 
            for i2, t2 in enumerate(table_names): 
                if i1 == i2: 
                    continue 
                table_name_combinations.append(t1 + t2) 
    
        fks_to_remove = [] 
        
        for table_name_dict_key, fk_stats in self.foreign_keys.items(): 
            for fk_index, fk in enumerate(fk_stats): 
                if fk.index_name not in table_name_combinations: 
                    fks_to_remove.append((table_name_dict_key, fk_index)) 
        
        #Sort so we remove from the end of the list and don't mess up our 
        # indexes for later removals 
        fks_to_remove = sorted(fks_to_remove, key=itemgetter(1), reverse=True) 
        
        for table_name_dict_key, index_to_remove in fks_to_remove: 
            self.foreign_keys[table_name_dict_key].pop(index_to_remove) 

    def compare_with_other(self, other, output_file_name = "compare_results.txt"):
        """
        Method called by the user to compare two databases to one another.
        
        Args:
        - other (HH_Database object): the other database that you'd like to compare
            this database to
        - output_file_name (str): Optional argument to specify the name of the 
            output file which the differences between the two databases will be
            written to.
            
        The two databases tables and columns should be identically named, or
            comparrison between the two will fail.
        """
        if self.tables_to_grade == []:
            print("***WARNING*** You haven't told me which tables to grade. Call the set_tables_to_grade() method")
        else:
            with open(output_file_name, "wt") as out_file:
                # maybe pass our out_file to these methods so they can write to the file themselves?
                print
                for table_to_grade in self.tables_to_grade:
                    print("="*30)
                    print("Checking table:", table_to_grade)
                    print("="*30)
                    
                    #Check if cadet mis-capitalized their table
                    cadet_alternate_spelling = ""
                    found_case_mismatch = False
                    for cadet_table in other.tables:
                        alt_spelling = cadet_table.name
                        if alt_spelling.casefold() == table_to_grade.casefold():
                            cadet_alternate_spelling = alt_spelling
                            found_case_mismatch = True
                            break
                    #Use difflib to find and compare the closest table name to 
                    # the solutions table, and compare that one.
                    if not found_case_mismatch:
                        cadet_tables = [table.name for table in other.tables]
                        cadet_alternate_spelling = difflib.get_close_matches(table_to_grade, cadet_tables, 1, 0.8)[0]
                        print("  -No match found from cadet's tables. Comparing to cadet's", cadet_alternate_spelling, "table instead")
                        
                    self.compare_tables(other, table_to_grade, cadet_alternate_spelling)
                    self.compare_columns(other, table_to_grade, cadet_alternate_spelling) 
                    self.compare_primary_keys(other, table_to_grade, cadet_alternate_spelling)
                    self.compare_foreign_keys(other, table_to_grade, cadet_alternate_spelling)
                    print()
                #print("-"*30)
                #print("Checking SQL queries")
                #print("-"*30)    
                #self.compare_sql_queries(other)
                #print()
                
    def compare_tables(self, other, table_name, cadet_alternate_spelling = ""):
        """
        Compares a table from this database object with an identically named database
            from the "other" variable.
            
        Args:
        - other (HH_Database object): another HH_Database object whose 
            identically named table will be compared.
        - table_name (str): The name of the table to be compared.
        """
        print("  " + "-"*30)
        print("  CHECKING TABLE")
        
        if cadet_alternate_spelling == "":
            cadet_alternate_spelling = table_name
                    
        mismatch_found = False

        fields_to_ignore = ['catalog']
        
        solution_table = self.get_namedtuple("tables", table_name)
        compare_table = other.get_namedtuple("tables", cadet_alternate_spelling)
        #print(solution_table)
        #print(compare_table)
        
        if compare_table == None:
            print("  -cadet is missing this table! Here are the cadet's tables:")
            for table in other.tables:
                print("    -" + table.name)
            print("  " + "-"*30)
            return
        
        for field in solution_table._fields:
            if field in fields_to_ignore:
                continue
            if getattr(solution_table, field) != getattr(compare_table, field):
                print("  -Mismatch detected in tables!!!")
                print("    -solution's " + field + " value is   :", getattr(solution_table, field))
                print("    -cadet's " + field + " value is      :", getattr(compare_table, field))
                mismatch_found = True
            else:
                pass
                #print(field, " matches")
        if not mismatch_found:
            print("  -Cadet has this table.  Hooah!")
        
        print("  " + "-"*30)
            
    def compare_statistics(self, other, table_name, cadet_alternate_spelling = ""):
        """
        Compares the statistics of a table from this database object with an identically named database from the "other" variable.
            
        Args:
        - other (HH_Database object): another HH_Database object whose 
            identically named table will be compared.
        - table_name (str): The name of the table to be compared.
        """
        if cadet_alternate_spelling == "":
            cadet_alternate_spelling = table_name
            
        mismatch_found = False

        solution_stat = self.get_namedtuple("statistics", table_name)
        compare_stat = other.get_namedtuple("statistics", cadet_alternate_spelling)
        #print(solution_stat)
        #print(compare_stat)
        if compare_stat == None:
            print("  -cadet is missing this table! Here are the cadet's tables:")
            for table in other.tables:
                print("    -" + table.name)
            return
        ignore_fields = ['table_catalog']
        
        for field in solution_stat._fields:
            if field in ignore_fields:
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
                    
    def compare_primary_keys(self, other, table_name, cadet_alternate_spelling = ""):
        """
        Compares the primary keys from this database object with an 
        identically named database from the "other" variable.
            
        Args:
        - other (HH_Database object): another HH_Database object whose 
            identically named table will be compared.
        - table_name (str): The name of the table to be compared.
        """
        print("  " + "-"*30)
        print("  CHECKING PRIMARY KEYS")
        
        if cadet_alternate_spelling == "":
            cadet_alternate_spelling = table_name
            
        mismatch_found = False

        ignore_fields = ['table_catalog']
        
        solution_pk_list = self.get_namedtuple("primary_keys", table_name)
        cadet_pk_list = other.get_namedtuple("primary_keys", cadet_alternate_spelling)
        
        if solution_pk_list == None:
            print("  -" + table_name + " does not have any primary keys.")
            print("  " + "-"*30)
            return
        
        #print("Solution is:")
        #pprint(solution_pk_list)
        #print()
        #print("cadet is:")
        #pprint(cadet_pk_list)
        #print()
        
        for solution_pk in solution_pk_list:
            #print("solution:", solution_pk)
            compare_pk = other.get_namedtuple("primary_keys", cadet_alternate_spelling, solution_pk.column_name)
            if compare_pk == None:
                print("  -Mismatch detected in primary keys!!!")
                sol_pks_string = ""
                for pk_table_stat in solution_pk_list:
                    sol_pks_string += pk_table_stat.column_name + ", "
                sol_pks_string = sol_pks_string[:-2]
                
                print("    -solution's primary keys are: " + sol_pks_string)
                
                compares_actual_pk = other.get_namedtuple("primary_keys", cadet_alternate_spelling)
                if compares_actual_pk == None:
                    print("    -cadet's has no primary key for this table!")
                else:
                    compare_pk_string = ""
                    for compare_pk_dict_key, compare_pks in other.primary_keys.items():
                        if compare_pk_dict_key == cadet_alternate_spelling:
                            for pk_table_stat in compare_pks:
                                compare_pk_string += pk_table_stat.column_name + ", "
                            compare_pk_string = compare_pk_string[:-2]
                
                    print("    -cadet's primary keys are   : " + compare_pk_string)
                        

                mismatch_found = True
                break
            #print("compare:",compare_pk)
            for field in solution_pk._fields:
                if field in ignore_fields:
                    continue
                elif getattr(solution_pk, field) != getattr(compare_pk, field):
                    print(" -Mismatch detected in primary keys!!!")
                    print("   -solution's " + field + " value is   :", getattr(solution_pk, field))
                    print("   -cadet's " + field + " value is :", getattr(compare_pk, field))
                    mismatch_found = True
                else:
                    pass
                #print(field, " matches")
        if not mismatch_found:
            print("  -Primary Key fields all check out.  Hooah!") 
        print("  " + "-"*30)    
    def compare_foreign_keys(self, other, table_name, cadet_alternate_spelling = ""):
        """
        Compares the primary keys from this database object with an 
        identically named database from the "other" variable.
            
        Args:
        - other (HH_Database object): another HH_Database object whose 
            identically named table will be compared.
        - table_name (str): The name of the table to be compared.
        """
        print("  " + "-"*30)
        print("  CHECKING FOREIGN KEYS")
        if cadet_alternate_spelling == "":
            cadet_alternate_spelling = table_name
            
        mismatch_found = False

        ignore_fields = ['table_catalog']
        
        solution_fk_list = self.get_namedtuple("foreign_keys", table_name)
        cadet_fk_list = other.get_namedtuple("foreign_keys", cadet_alternate_spelling)
        
        #print("Solution is:")
        #pprint(solution_fk_list)
        #print()
        #print("cadet is:")
        #pprint(cadet_fk_list)
        #print()
              
        if solution_fk_list == None:
            if cadet_fk_list == None:
                print("  -Foreign Key fields all check out (Both have none). Hooah!")
            else:
                print("  -Solution has no foreign keys found for the", table_name, "table")
                for fk in cadet_fk_list:
                    relationship_string = fk.index_name.split(fk.table_name)[0] + "-->" + fk.table_name
                    print("      -" + relationship_string + " : " + fk.column_name)
            print("  " + "-"*30)
            return

        if cadet_fk_list == None:
            print("  -Mismatch detected in foreign keys!!!")
            print("    -solution's foreign keys are: ")
            for fk in solution_fk_list:
                relationship_string = fk.index_name.split(fk.table_name)[0] + "-->" + fk.table_name
                print("      -" + relationship_string + " : " + fk.column_name)
            print("    -cadet's has no foreign keys for this table!!!")
            mismatch_found = True
            print("  " + "-"*30)
            return
        
        
        for solution_fk in solution_fk_list:
            #print("solution:", solution_pk)
            compare_fk = other.get_namedtuple("foreign_keys", cadet_alternate_spelling, solution_fk.column_name)
            if compare_fk == None:
                    print("  -Mismatch detected in foreign keys!!!")
                    print("   -solution's foreign key is: " + solution_fk.column_name)
                    print("   -cadet's is missing this foreign key! Here are the cadet relationships for this table:")
                    for fk in cadet_fk_list:
                        relationship_string = fk.index_name.split(fk.table_name)[0] + "-->" + fk.table_name
                        print("      -" + relationship_string + " : " + fk.column_name)
                    mismatch_found = True
                    continue
            #print("compare:",compare_pk)
            for field in solution_fk._fields:
                if field in ignore_fields:
                    continue
                elif getattr(solution_fk, field) != getattr(compare_fk, field):
                    print("  -Mismatch detected in foreign keys!!!")
                    print("    -solution's " + field + " value is   :", getattr(solution_fk, field))
                    print("    -cadet's " + field + " value is :", getattr(compare_fk, field))
                    mismatch_found = True
                else:
                    pass
                #print(field, " matches")
        if not mismatch_found:
            print("  -Foreign Key fields all check out.  Hooah!")        
        print("  " + "-"*30)   
        
    def compare_columns(self, other, table_name, cadet_alternate_spelling = ""):
        """
        Compares all the columns from a table from this database object with an 
        identically named table from the "other" variable.
            
        Args:
        - other (HH_Database object): another HH_Database object whose 
            identically named table will be compared.
        - table_name (str): The name of the table whose columns will be compared.
        """
        print("  " + "-"*30)
        print("  CHECKING COLUMNS")
        if cadet_alternate_spelling == "":
            cadet_alternate_spelling = table_name
            
        mismatch_found = False

        fields_to_ignore = ["table_catalog",
                            "table_schema",
                            "table_name",
                            "data_type",
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
        
        solution_col_list = self.get_namedtuple("columns", table_name)
        #pprint(solution_col_list)
        
        for solution_col in solution_col_list:
            compare_col = other.get_namedtuple("columns", cadet_alternate_spelling, solution_col.column_name)
            #print("solution:")
            #print(solution_col)
            #print("cadet:")
            #print(compare_col)
            
            #correct mis-capitalized column name
            for col in other.get_namedtuple("columns", cadet_alternate_spelling):
                if col.column_name.casefold() == solution_col.column_name.casefold():
                    #print("  -mis-capitalization detected in column name")
                    compare_col = col
                    break

            if compare_col == None:
                print("    -" + solution_col.column_name + " does not match") 
                print("      -Cadet is missing this column!  Cadet's columns are:")
                compare_cols = other.get_namedtuple("columns", cadet_alternate_spelling)
                column_string = ""
                for col in [c.column_name for c in compare_cols]:
                    column_string += col + ", "
                print("        -" + column_string[:-2])
                    
                
                mismatch_found = True
                continue
            
            
            already_printed_column_name = False
            for field in solution_col._fields:
                if field in fields_to_ignore:
                    continue
                if getattr(solution_col, field) != getattr(compare_col, field):
                    if mismatch_found == False:
                        mismatch_found = True
                        print("  -Mismatched columns detected!")
                    if not already_printed_column_name:
                        print("    -" + solution_col.column_name, "does not match")
                        already_printed_column_name = True
                    print("      -solution's " + field + " value is :", getattr(solution_col, field))
                    print("      -cadet's " + field + " value is    :", getattr(compare_col, field))
                    
                else:
                    pass
                    #print(field, " matches")
        if not mismatch_found:
            print("  -Column fields all check out.  Hooah!")
        print("  " + "-"*30)
    def compare_sql_queries(self, other):
        """
        Compares all the sql queries from this database object with all the
        identically named sql queries from the "other" variable.
            
        Args:
        - other (HH_Database object): another HH_Database object whose 
            identically named sql queries will be compared.
        """
        mismatch_found = False
        
        compare_query = None
        for sol_query in self.sql_queries:
            #find matching sql_query in other
            for other_query in other.sql_queries:
                if other_query.name == sol_query.name:
                    compare_query = other_query
            
            #print("solution")
            #print(sol_query)
            #print("cadet")
            #print(compare_query)
            
            if compare_query == None:
                print("  -Cadet database does not have a query named:", sol_query.name)
                mismatch_found = True
            else:
                sol_results = self.database_cursor.execute("SELECT * FROM " + sol_query.name)
                try:
                    compare_results = other.database_cursor.execute("SELECT * FROM " + other_query.name)
                    
                    sol_set = set(list(sol_results))
                    compare_set = set(list(compare_results))
                    
                    #print(sol_set)
                    #print(compare_set)
                    
                    if sol_set.union(compare_set) != sol_set:
                        print("  -SQL query results for", sol_query.name, "do NOT match!")
                        mismatch_found - True
                        print("    -Solution's query results are:")
                        print("     -", list(sol_results))
                        print("    -Cadet's query results are:")
                        print("     -", list(compare_results))
                        mismatch_found = True
                        print()
                    else:
                        print("  -" + sol_query.name + "'s results match!")
                except Exception as e:
                    print("  -cadet's sql query " + sol_query.name + " had the following error:")
                    print(e)
                    mismatch_found = True
        if not mismatch_found:
            print("  -SQL queries all check out.  Hooah!")
                
                

    def get_namedtuple(self, tuple_name, name_of_table, name_of_column=""):
        """
        An accessor method for pulling the desired table, statistic, column, or
          query from the attributes of this object.  Uses the table name or the 
          name of the column to select the desired attribute, and is usually used
          in the retreival for comparison of attributes from the "other" database.
        
        Args:
        - tuple_name (str): Either "tables", "statistics", "columns", "primary_keys",
          or "foreign_keys".  Anything else will cause the program to exit.
        - name_of_table (str): the name of the table whos attribute you'd like to retrieve.
        - name_of_column (str): Used when retrieving columns or keys.  Failing to 
            provide this when asking for columns or keys gets you the list of all
            of them.  Providing this will attempt to provide you with the correct
            column for comparison.
        
        Returns:
        - if the tuple_name is "tables": returns the table namedtuple with the 
            desired table name.
        - if the tuple_name is "statistics": returns the table_statistic named tuple
            associated with that table..
        - if the tuple_name is "columns": 
            - If no name_of_column is provided as an argument, returns
                a list of column namedtuples with all the columns associated with the 
                desired table.
            - If name_of_column is provided as an argument, returns the column 
                namedtuple for the desired table and the desired column.
        - if the tuple_name is "primary_keys": 
            - If no name_of_column is provided as an argument, returns
                a list of table_statistic namedtuples with all the 
                statistics associated with the primary keys of the desired table.
            - If name_of_column is provided as an argument, returns the table_statistic 
                namedtuple for the desired primary key and the desired column, or None
                if no primary keys exist.
        - if the tuple_name is "foreign_keys": 
            - If no name_of_column is provided as an argument, returns
                a list of table_statistic namedtuples with all the 
                statistics associated with the foreign keys of the desired table,
                or None if no foreign keys exist.
            - If name_of_column is provided as an argument, returns the table_statistic 
                namedtuple for the desired table and the desired column.
        """
        if tuple_name == "tables":
            for table in self.tables:
                if table.name == name_of_table:
                    return table
        elif tuple_name == "statistics":
            return self.statistics.get(name_of_table, None)
        elif tuple_name == "columns":
            if name_of_column == "":
                return self.columns.get(name_of_table, None)
            else:
                columns = self.columns.get(name_of_table, None)
                if columns == None:
                    return None
                for column in columns:
                    if column.column_name == name_of_column:
                        return column
        elif tuple_name == "primary_keys":
            if name_of_column == "":
                return self.primary_keys.get(name_of_table, None)
            else:
                pk_list = self.primary_keys.get(name_of_table, None)
                if pk_list == None:
                    return None
                for pk in pk_list:
                    if pk.column_name == name_of_column:
                        return pk
        elif tuple_name == "foreign_keys":
            if name_of_column == "":
                return self.foreign_keys.get(name_of_table, None)
            else:
                for fk in self.foreign_keys[name_of_table]:
                    if fk.column_name == name_of_column:
                        return fk
        else:
            print("No attribute named:", tuple_name)
            exit()
    
    def __repr__(self):
        """
        Overridden to allow HH_Database objects __repr__ to work.
        """
        return self.__class__.__name__ + "(" + repr(self.path_to_database) + ")"
        
    def __str__(self):
        """
        Allows for string representation of HH_Database objects.  This output is
            quite long, but prints out all relavent information about the object,
            which has been loaded from the database.
        """
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
            return_string += "  - " + k + ": " + str(v) + "\n"
        return_string += "\n"
        return_string += "\n"
        
        return_string += "-"*30 + "\n"
        return_string += "primary keys are:\n"
        return_string += "-"*30 + "\n"
        for k,v in self.primary_keys.items():
            return_string += "- " + str(k) + "\n"
            for stat in v:
                return_string += "    - " + str(stat) + "\n"
            return_string += "\n"
        return_string += "\n"
        
        return_string += "-"*30 + "\n"
        return_string += "foreign keys are:\n"
        return_string += "-"*30 + "\n"
        for k,v in self.foreign_keys.items():
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
        
if __name__ == "__main__":
    #solution_database_obj = HH_Database(r".\DBTEEverB_SOLN.ACCDB")
    solution_database_obj = HH_Database(r".\test_db_files\Solution.ACCDB")
    #cadet_database_obj = HH_Database(r".\DBTEEverB.ACCDB")
    cadet_database_obj = HH_Database(r".\test_db_files\6.ACCDB")
    
    #With an overloaded str function, you can print the database!
    #print("==="*30)
    #print("Solution database is:")
    #print("==="*30)
    #print(solution_database_obj)
    #print("==="*30)
    #print("Cadet database is:")
    #print("==="*30)
    #print(cadet_database_obj)
    #print("==="*30)

    #solution_database_obj.set_tables_to_grade(['Profile', 'FitnessTests', 'CadetInTest'])
    solution_database_obj.set_tables_to_grade(['Run', 'Race', 'CadetRunsRace'])
    solution_database_obj.compare_with_other(cadet_database_obj)
 