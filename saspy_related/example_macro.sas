/* Create tables based on yyyymm keys */
%macro create_tables(start_date=, end_date=);
    %local yyyymm;

    %do yyyymm=&start_date %to &end_date;
        /* Create table for yyyymm */
        data table_&yyyymm;
            set sashelp.class;
            /* creat a month column */
            month=&yyyymm;
        run;
    %end;
%mend;

%let start_date=202201;
%let end_date=202212;
%create_tables(start_date=&start_date, end_date=&end_date);
