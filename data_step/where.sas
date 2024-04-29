/* first 4 rows of a table */
proc print data=sashelp.class(obs=4);

proc sql outobs=4;
  select * from sashelp.class;
quit;

/* filter to where column col is A */
proc print data=sashelp.class(where=(col='A'));
proc sql noprint;
  select * from sashelp.class where col='A';
quit;


