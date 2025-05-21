proc export data=my_data
  outfile="/home/u13181/data.csv"
  dbms=csv
  replace;
run;
