PROC SQL;
    CREATE TABLE new_table AS
    SELECT 
        case when age LT 14 then '< 14'
                when age GE 14 then '>= 14'
                else 'MISSING'
        end as age_group1,
        case 
            when age LE 14 then '<= 14'
            when age GT 14 then '> 14'
            else 'MISSING'
        end as age_group2,
        case when age EQ 14 then '14'
            else 'NOT 14'
        end as age_group3,
        case when age NE 14 then 'NOT 14'
            else '14'
        end as age_group4
    FROM sashelp.class;
QUIT;