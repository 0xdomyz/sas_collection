libname libsas '/home/u63767787';

/* data from csv */

data libsas.sataddress;
    infile '/home/u63767787/sataddress.csv'
    dlm = ',' firstobs=2;
    input id name $ address $;
    run; 

data libsas.testscores;
    infile '/home/u63767787/testscores.csv'
    dlm = ',' firstobs=2;
    input char $ score id date $;
run;

/* sort and merge */

proc sort data = libsas.testscores out=work.testsort;
by id;
run;

proc sort data = libsas.sataddress out=work.sataddress;
by id;
run;
    
data work.satscoreaddress;
    merge work.sataddress work.testsort;
    by id;
run;
