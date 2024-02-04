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

/* re-order ranges */
proc sql;
    create table bmi_groups_number_names as
    select *,
        case
            when bmi_range = "Underweight" then "1. Underweight"
            when bmi_range = "Normal" then "2. Normal"
            when bmi_range = "Overweight" then "3. Overweight"
            when bmi_range = "Obese" then "4. Obese"
            else "5. Other"
        end as bmi_range_number_names
    from bmi_groups;
quit;

proc freq data=bmi_groups_number_names;
    tables bmi_range_number_names;
    title "Frequency Distribution of BMI Ranges 2";
