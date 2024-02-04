proc sql noprint;
	create table work.filter_baseball as select * from SASHELP.BASEBALL 
		where(Salary LT 750 AND League EQ 'American');
quit;

proc print data=work.filter_baseball(obs=20);
	title "Filtered data set - work.filter_baseball";
run;

title;
