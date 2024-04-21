/* Specify the start and end dates */
%let start_date = '202201';
%let end_date = '202212';

/* Create tables based on yyyymm keys */
%macro create_tables;
  %local yyyymm;
  
  %do yyyymm = &start_date %to &end_date;
    /* Create table for yyyymm */
    data table_&yyyymm;
        set  sashelp.class;
        /* creat a month column */
        month = &yyyymm;
    run;
  %end;
%mend;

%create_tables;

/* combines list of tables covering a range of suffixes */
%macro combine_tables;
  %local yyyymm;
  
    data combined_table;
        set 
        %do yyyymm = &start_date %to &end_date;
            table_&yyyymm
        %end;
    run;

%mend;

%combine_tables;
