/* conditional */
data bmi_groups;
    set sashelp.heart;
    BMI = weight / (height**2) * 703;
    length bmi_range $ 30;
    keep weight height bmi bmi_range;

    if BMI < 18.5 then bmi_range = "Underweight";
    else if BMI < 25 and BMI >= 18.5 then bmi_range = "Normal";
    else if BMI < 30 then bmi_range = "Overweight";
    else bmi_range = "Obese";
run;

proc freq data=bmi_groups;
    tables bmi_range;
    title "Frequency Distribution of BMI Ranges";
run;

/* output to table within condition */
data bmi_high bmi_low;
    set sashelp.heart;
    length bmi_range $ 30;
    keep weight height bmi bmi_range;
    bmi = weight / (height**2) * 703;

    /* multiple statements */
    if bmi < 18.5 then do;
        bmi_range = "Underweight";
        output bmi_low;
    end;
    else if bmi >= 30 then do;
        bmi_range = "Obese";
        output bmi_high;
    end;
run;

/* print out count of records in high and low tables */
proc sql;
    select count(*) as count_of_underweight from bmi_low;
    select count(*) as count_of_obese from bmi_high;
quit;