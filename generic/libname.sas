
/* sas lib creation and reference, can be used to store data in phy location */

libname libsas '/home/u63767787/cars';
/* libname libsas2 'S:/datafiles/cars'; */

data libsas.europeancars;
    set sashelp.cars;
    where origin = 'Europe';
run;

proc print data=libsas.europeancars;
run;


