/* processor treates all text as string */

/* quotes are escaped */
%let var1=World;
%put Hello, &var1;

%let var1="World";
%put Hello, &var1;

%let var1='World';
%put Hello, &var1;

/* macro variable resolve with double quotes but not with single quotes */
%let var1 = World;
%put "Hello, &var1";  /* This will output: Hello, World */
%put 'Hello, &var1';  /* This will output: Hello, &var1 */

/* concatenating str by puting them together */
%let var1 = Hello;
%let var2 = World;
%let var3 = &var1 &var2;
%put &var3;  /* This will output: Hello World */

%let var3 = &var1.&var2.;
%put &var3;  /* This will output: HelloWorld */

/* escape quote by %str, or nothing */
%let var1 = %str("Hello, World");
%put &var1 aaa;  /* This will output: "Hello, World" aaa */

%let var1 = "Hello, World";
%put &var1 aaa;  /* This will output: "Hello, World" aaa */

/* number as text */
%let date = 20180630;
%put table_&date;  /* This will output: table_20180630 */
%put tbl_&date._post;  /* This will output: tbl_20180630_post */

/* bquote */
%let name = World;
%put Hello, &name;

%let name = World;
%put %bquote(Hello, &name);

/* dyn libname */
libname mylib '/home/u63767787';

%let p1=/home;
%let p2=u63767787;
%put &p1./&p2.;
%put "&p1.&p2.";

libname mylib3 "&p1./&p2.";

/* macro var from another macro var */
%let p1=/home;
%let p2=&p1./u63767787;
libname mylib4 "&p2.";

/* Integer arithmetic */
%let var1 = 5;
%let var2 = 2;
%let sum = %eval(&var1 + &var2);
%put &sum;  /* This will output: 7 */

/* Floating-point arithmetic */
%let var1 = 5;
%let var2 = 2;
%let division = %sysevalf(&var1 / &var2);
%put &division;  /* This will output: 2.5 */

/* advance a month end by a month */
%let date = 31DEC2020;

DATA _NULL_;
    /* Convert the macro variable to a SAS date value */
    date_value = input(symget('date'), date9.);
    put date_value=;
    
    /* Advance to the end of the next month */
    next_month_end = intnx('month', date_value, 1, 'E');
    put next_month_end=;

    /* Convert the date value back to a date literal and store it in a macro variable */
    put next_month_end= date9.;
    call symputx('date2', put(next_month_end, date9.));
RUN;

%put &date2;  /* This will output: 31JAN2021 */

