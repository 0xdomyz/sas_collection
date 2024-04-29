/* import from csv */

data testscores;
    infile '/home/u63767787/testscores.csv'
    dlm = ',' firstobs=2;
    input char $ score id date $;
run;

/* save to csv */

proc export data=testscores
    outfile='/home/u63767787/testscores2.csv'
    dbms=csv replace;
run;

/* use proc import to save a dataframe into a csv in local machine */
/* proc import datafile='/home/u63767787/testscores.csv'
    out=work.testscores
    dbms=csv replace;
run; */
