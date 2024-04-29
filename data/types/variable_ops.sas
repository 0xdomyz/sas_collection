/* A variable in SAS is a placeholder that contains data.
This data can be numeric or character. Variables are used in DATA steps and PROC
steps to manipulate data and generate results. */

/* data are creeted as columns in a table */
data example;
    /* Number */
    num_var=123;

    /* String */
    char_var="Hello, world!";

    /* Date as number */
    date_num_var='01JAN2022'd;

    /* Date as string */
    date_str_var='01JAN2022';

    /* Date formatted */
    date_formatted_var=put('01JAN2022'd, date9.);

    /* Creating strings from other variables */
    string_var=catx(", ", char_var, put(num_var, best.), date_str_var);
run;

/* show the variables */
proc print data=example;
run;

/* variables in a proc step */
proc means data=example;
    var num_var;
run;
