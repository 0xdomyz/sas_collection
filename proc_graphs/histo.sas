/*
 *
 * Task code generated by SAS Studio 3.8 
 *
 * Generated on '2/5/24, 9:16 PM' 
 * Generated by 'u63767787' 
 * Generated on server 'ODAWS01-APSE1-2.ODA.SAS.COM' 
 * Generated on SAS platform 'Linux LIN X64 3.10.0-1062.12.1.el7.x86_64' 
 * Generated on SAS version '9.04.01M7P08062020' 
 * Generated on browser 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0' 
 * Generated on web client 'https://odamid-apse1-2.oda.sas.com/SASStudio/main?locale=en_US&zone=GMT%252B11%253A00&ticket=ST-71525-H4saNN9JGjMhc05MvDjB-cas' 
 *
 */

ods graphics / reset width=6.4in height=4.8in imagemap;

proc sgplot data=SASHELP.CARS (where=(type ne "Hybrid"));
	title height=14pt "distribution of mileage";
	histogram MPG_City / showbins nbins=20;
	density MPG_City;
	density MPG_City / type=Kernel;
	yaxis grid;
run;

ods graphics / reset;
title;
