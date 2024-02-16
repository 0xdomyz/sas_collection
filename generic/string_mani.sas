/* macro variable resolve with double quotes but not with single quotes */
%let var1 = World;
%put "Hello, &var1";  /* This will output: Hello, World */
%put 'Hello, &var1';  /* This will output: Hello, &var1 */

/* concatenating str by || or just together */
%let var1 = Hello;
%let var2 = World;
%let var3 = &var1 &var2;
%put &var3;  /* This will output: HelloWorld */

/* escape quote by %str */
%let var1 = %str("Hello, World");
%put &var1;  /* This will output: "Hello, World" */

/* processor treates al text as string */


