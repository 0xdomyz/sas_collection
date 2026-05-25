# %%
import saspy

sas = saspy.SASsession()

# %%
_lib, _tbl = "sashelp.heart".split(".")
df_h1 = sas.sasdata(_tbl, _lib).head(1)
print(df_h1.T.to_string())

# %%
_lib, _tbl = "sashelp.heart".split(".")
sd = sas.sasdata(_tbl, _lib)
_shape = (sd.obs(), len(sd.columnInfo()))
print(_shape)

# %%
qry = f"""
proc rank
    data=sashelp.heart
    out=_tmp_h_dec
    groups=10;
    var smoking;
    ranks decile0;
run;

proc sql;
create table _tmp_rates as
select
    case
        when missing(decile0) then 'NA'
        else strip(put(decile0, 2.))
    end as decile,
    count(*) as n,
    mean(status='Dead') as rate
from _tmp_h_dec
group by decile0
order by decile;
quit;

proc sgplot data=_tmp_rates;
    vbarparm category=decile response=n / datalabel transparency=0.15;
    series x=decile y=rate / y2axis markers lineattrs=(thickness=2);
    yaxis  label='Volume';
    y2axis label='Rate' values=(0 to 1 by 0.1);
    xaxis  label='Decile' integer;
run;
    """
sas.submitLST(qry, method="listonly")
