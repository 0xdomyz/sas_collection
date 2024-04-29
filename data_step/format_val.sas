libname libsas '/home/u63767787';

/* data from csv */

data libsas.customers;
    infile '/home/u63767787/customers.csv'
    dlm = ',' firstobs=2;
    input customer_id name $ country $ gender $ birth_date total;
run; 


proc print data=libsas.customers;
    /* format total comma12.3 birth_date date9.; */
    format total dollar12.3 birth_date mmddyy10.;
run;

data libsas.customers_new;
    set libsas.customers;
    format total dollar12.3 birth_date mmddyy10.;
run;

proc print data=libsas.customers_new;
/* proc apply formats that are stored in the data step, which are column attributes */


