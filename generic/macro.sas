/* head */
/* ######################################## */
%macro head(table_name);
   proc sql outobs=5;
      select * from &table_name.;
   quit;
%mend;

%head(sashelp.cars);

/* to avoid fetching the whole table */
%macro head(table_name);
    proc sql;
        connect to mysql (/* your connection options here */);
        select * from connection to mysql
        (
            select * from &table_name. limit 5
        );
        disconnect from mysql;
    quit;
%mend;

%head(my_table);

/* data step within a macro */
/* ######################################## */

%macro create_data(n);
    data work.sample;
        do i = 1 to &n;
            output;
        end;
    run;
%mend;

%create_data(5);

/* within loop within data step */
%macro create_datasets(n);
    %do i = 1 %to &n;
        data work.sample_&i;
            do j = 1 to &i;
                output;
            end;
        run;
    %end;
%mend;

%create_datasets(5);


/* logging */
/* ######################################## */

/* printing a word that shows up in the results page*/
DATA _NULL_;
    PUT '================= Section 1 Results =================';
RUN;

TITLE '================= Section 1 Results =================';
/* Your code for Section 1 here */

/* loops */
/* ######################################## */

/* a do loop that prints out 1 to 100 */
DATA _NULL_;
    DO I = 1 TO 100;
        PUT I;
    END;
RUN;

/* same but inside a macro */
%macro print_1_to_100;
    %do i = 1 %to 100;
        %put &i;
        /* print like these: on loop 3 */
        %put on loop &i;
    %end;
%mend;

%print_1_to_100;


/* variable */
/* ######################################## */

/* creating a global variable */
%let global_var = 5;
%put &global_var;

/* creating a local variable */
%macro local_var;
    %let local_var = 10;
    %put &local_var;
%mend;

%local_var;

/* creating a macro variable */

%macro create_macro_var;
    %let macro_var = 15;
    %put &macro_var;

    %global macro_var;
%mend;

%create_macro_var;

/* creating a macro variable with a value from a dataset */
DATA _NULL_;
    SET sashelp.class;
    CALL SYMPUT('class_size', _N_);
RUN;

%put &class_size;


