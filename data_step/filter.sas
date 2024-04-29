data work.highchol;
    set sashelp.heart;
    /* where cholesterol > 200 and status = 'Alive'; */
    where 
        (bp_status = 'High' or chol_status = 'High');
run;

proc print data=work.highchol;

