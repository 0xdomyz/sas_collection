proc rank data=sample groups=10 out=r; var score; ranks d; run;

proc sql;
    create table cut as
    select d, max(score) as cp
    from r group by d order by d;

    create table full_scored as
    select f.*,
           (select min(d) from cut where f.score <= cp) as decile
    from full f;
quit;






proc rank data=sample groups=10 out=sample_r;
    var score;
    ranks decile;
run;


proc sql;
    create table cut as
    select decile,
           max(score) as cp
    from sample_r
    group by decile
    order by decile;
quit;

proc sql;
    create table full_scored as
    select f.*,
           case
               when score <= (select cp from cut where decile=0) then 0
               when score <= (select cp from cut where decile=1) then 1
               when score <= (select cp from cut where decile=2) then 2
               when score <= (select cp from cut where decile=3) then 3
               when score <= (select cp from cut where decile=4) then 4
               when score <= (select cp from cut where decile=5) then 5
               when score <= (select cp from cut where decile=6) then 6
               when score <= (select cp from cut where decile=7) then 7
               when score <= (select cp from cut where decile=8) then 8
               else 9
           end as decile
    from full f;
quit;
