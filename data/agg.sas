/* proc sql group by*/
PROC SQL;
    CREATE TABLE aggregated AS
    SELECT 
        id,
        name,
        address,
        AVG(score) AS avg_score
    FROM sashelp.class
    GROUP BY 1,2,3;
QUIT;

PROC SQL;
    CREATE TABLE aggregated AS
    SELECT 
        id,
        name,
        address,
        AVG(score) AS avg_score
    FROM sashelp.class
    GROUP BY 1;
QUIT;

PROC SQL;
    CREATE TABLE aggregated AS
    SELECT 
        id,
        name,
        address,
        AVG(score) AS avg_score
    FROM sashelp.class
    GROUP BY calculated avg_score;
QUIT;

/* proc summary */
proc summary data=sashelp.class nway missing;
    class id name address;
    var score;
    output out=aggregated mean=avg_score drop=_type_ _freq_;

