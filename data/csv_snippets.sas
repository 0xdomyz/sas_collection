/** FOR CSV Files uploaded from Windows **/

FILENAME CSV "/home/u63767787/customers.csv" TERMSTR=CRLF;

/** FOR CSV Files uploaded from Unix/MacOS **/

/* FILENAME CSV "<Your CSV File>" TERMSTR=LF; */

/** Import the CSV file.  **/

PROC IMPORT DATAFILE=CSV
		    OUT=WORK.MYCSV
		    DBMS=CSV
		    REPLACE;
RUN;

/** Print the results. **/

PROC PRINT DATA=WORK.MYCSV; RUN;

/** Unassign the file reference.  **/

FILENAME CSV;



/* Stream a CSV representation of SASHELP.CARS directly to the user's browser. */

proc export data=sashelp.cars
            outfile=_dataout
            dbms=csv replace;
run;

%let _DATAOUT_MIME_TYPE=text/csv;
%let _DATAOUT_NAME=cars.csv;

