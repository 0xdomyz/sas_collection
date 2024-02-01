data europeancars;
    set sashelp.cars;
    where origin = 'Europe';
run;

proc print data = europeancars;
run;

data highchol;
    set sashelp.heart;
    where Chol_Status = 'High';
run;

proc print data = highchol;
run;
