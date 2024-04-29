/* Generated Code (IMPORT) */
/* Source File: SampleData.xlsx */
/* Source Path: /home/u63767787 */
/* Code generated on: 2/4/24, 6:00 PM */

%web_drop_table(LIBSAS.IMPORT);


FILENAME REFFILE '/home/u63767787/SampleData.xlsx';

PROC IMPORT DATAFILE=REFFILE
	DBMS=XLSX
	OUT=LIBSAS.IMPORT;
	GETNAMES=YES;
	SHEET="SalesOrders";
RUN;

PROC CONTENTS DATA=LIBSAS.IMPORT; RUN;


%web_open_table(LIBSAS.IMPORT);


/* csv */

/* Generated Code (IMPORT) */
/* Source File: customers.csv */
/* Source Path: /home/u63767787 */
/* Code generated on: 2/4/24, 6:07 PM */

%web_drop_table(WORK.IMPORT);


FILENAME REFFILE '/home/u63767787/customers.csv';

PROC IMPORT DATAFILE=REFFILE
	DBMS=CSV
	OUT=WORK.IMPORT;
	GETNAMES=YES;
	DATAROW=2;
RUN;

PROC CONTENTS DATA=WORK.IMPORT; RUN;


%web_open_table(WORK.IMPORT);

