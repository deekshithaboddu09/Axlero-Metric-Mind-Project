# Axlero-Metric-Mind-Project
Agentic Semantic BI Engine - Axlero Internship Project 
             
               SQL Commands - Complete Notes

Created by: SIKILI AVINASH

SQL Commands

SQL commands are instructions. It is used to communicate with the database. It is also used to perform specific tasks, functions, and queries of data.

SQL can perform various tasks like create a table, add data to tables, drop the table, modify the table, set permission for users.

Types of SQL Commands

There are five types of SQL commands: DDL, DML, DCL, TCL, and DQL.

1. Data Definition Language (DDL)

DDL changes the structure of the table like creating a table, deleting a table, altering a table, etc.

All the command of DDL are auto-committed that means it permanently save all the changes in the database.

Here are some commands that come under DDL:

CREATE o  ALTER o  DROP o  TRUNCATE

a. CREATE It is used to create a new table in the database.

Syntax:

1.  CREATE TABLE TABLE_NAME (COLUMN_NAME DATATYPES[,....]);

Example:

1.  CREATE TABLE EMPLOYEE(Name VARCHAR2(20), Email VARCHAR2(100), DOB DATE);

b. DROP: It is used to delete both the structure and record stored in the table. Syntax

1.  DROP TABLE ;

Example

1.  DROP TABLE EMPLOYEE;

c. ALTER: It is used to alter the structure of the database. This change could be either to modify the characteristics of an existing attribute or probably to add a new attribute.

Syntax:

To add a new column in the table

1.  ALTER TABLE table_name ADD column_name COLUMN-definition;

To modify existing column in the table:

1.  ALTER TABLE MODIFY(COLUMN DEFINITION....);

EXAMPLE

ALTER TABLE STU_DETAILS ADD(ADDRESS VARCHAR2(20));

ALTER TABLE STU_DETAILS MODIFY (NAME VARCHAR2(20));

d. TRUNCATE: It is used to delete all the rows from the table and free the space containing the table.

Syntax:

1.  TRUNCATE TABLE table_name;

Example:

TRUNCATE TABLE EMPLOYEE;