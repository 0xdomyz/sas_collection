/* A macro variable in SAS is a type of variable that is used in macro programming to
automate repetitive code or tasks. Macro variables are resolved to their values during
the execution of the program.  */

/* string quote issue */
%let var1=World;
%put Hello, &var1;

%let var1="World";
%put Hello, &var1;

%let var1='World';
%put Hello, &var1;



libname mylib '/home/u63767787';

%let p1='/home/u63767787';
%let p2='u63767787';
%put &p1.&p2.;
%put "&p1.&p2.";

libname mylib2 "&p1.&p2.";
%put &mylib2.;

