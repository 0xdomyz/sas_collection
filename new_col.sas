data work.cardata;
    set sashelp.cars;
    Markup = MSRP - Invoice;
    Make_Model = catx('_', make, model);
run;

proc print data=work.cardata;
    