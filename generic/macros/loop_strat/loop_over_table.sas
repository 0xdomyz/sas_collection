/* Define the names of the tables */
%let tables = table1 table2 table3;

/* Create an empty results table */
proc sql;
    create table results (TableName char(10), SumValue num);
quit;

/* Loop over the tables */
%macro sum_tables;
    %do i = 1 %to %sysfunc(countw(&tables.));
        %let table = %scan(&tables., &i.);
        proc sql;
            /* Calculate the sum */
            create table temp as
            select sum(column_name) as SumValue
            from &table.;
            
            /* Add the result to the results table */
            insert into results
            select "&table." as TableName, SumValue
            from temp;
        quit;
        
        /* Delete the temporary table */
        proc datasets library=work nolist;
            delete temp;
        quit;
    %end;
%mend sum_tables;

%sum_tables;

