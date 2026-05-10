# %%
import saspy

sas = saspy.SASsession()
sas

# %% [markdown]
# ### data

# %%
sas.submitLST(f"""
    proc logistic data=sashelp.cars order=freq noprint;
        model origin (event='Asia') = mpg_city mpg_highway weight / link=glogit;
        ouput out=cars_est predprobs=INDIVIDUAL;
    run;
    
    title;
    proc print data=cars_est (obs=5);
        var origin mpg_city mpg_highway weight _from_ _into_;
    run;
""")


# %%

_lib, _tbl = "work._pred".split(".")
sd = sas.sasdata(_tbl, _lib)
_shape, df_h = (sd.obs(), len(sd.columnInfo())), sd.head()
print(_shape)
df_h

# %% [markdown]
# ### proc freq
#

# %%
# tables
sas.submitLST(f"""
proc freq data=cars_est;
    tables _from_ / missing;
run;
title;
""")


# %%
# tables w/ interaction
sas.submitLST(f"""
PROC FREQ DATA = cars_est; 
    TABLES _from_ * _into_ / missing; 
RUN;
""")

# %%
# statistical options to control outputs
sas.submitLST(f"""
PROC FREQ DATA = cars_est; 
    TABLES _from_ * _into_ / missing nocum norow nocol nopercent;
RUN;
""")

# %%
# long format via LIST
sas.submitLST(
    f"""
PROC FREQ DATA = cars_est noprint;
    TABLES _from_ * _into_ / LIST MISSING out = df; 
RUN;
              
PROC PRINT DATA = df ;
RUN;
""",
    method="listorlog",
)


# %%
# somers d
sas.submitLST(
    f"""
title;
proc freq data=sashelp.heart;
    tables weight_status * status;
    test smdcr;
run;
""",
    method="listonly",
)

# %% [markdown]
# ### stas on subsets

# %%
# prep sfa
sas.submitLST(
    f"""
proc rank
    data=sashelp.heart(where=(status in ('Alive','Dead')))
    out=_tmp_h_dec
    groups=10;
    var height;
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
    """,
    method="listonly",
)

# %%
sas.submitLST(
    f"""
proc rank
    data=sashelp.heart(where=(status in ('Alive','Dead')))
    out=work.heart2
    groups=10;
    var height;
    ranks height_decile;
run;
""",
    method="listonly",
)
df_h1 = sas.sasdata(f"heart2", "work").head(1)
print(df_h1.T.to_string())

# %%
tbl = "work.heart2"
target = "status"
var = "ageatstart"
time_var = "height_decile"

# %%
sas.submitLST(
    f"""
title;
proc freq data={tbl};
    tables chol_status;
run;
""",
    method="listonly",
)
# %%
sas.submitLST(
    f"""
title;
proc freq data={tbl};
    tables bp_status;
run;
""",
    method="listonly",
)
# %%
sas.submitLST(
    f"""
title;
proc freq data={tbl};
    tables weight_status;
run;
""",
    method="listonly",
)

# %%
sas.submitLST(
    f"""
proc sql;
create table _test1 as
select * from {tbl}
where bp_status = 'High' and {time_var} = 5; 
quit;
    
proc freq data=work._test1;
    tables {var} * {target};
    test smdrc;
run;
""",
    method="listonly",
)
# %%
sas.submitLST(
    f"""
proc logistic data=work._test1 plots(only)=roc;
    where status in ('Alive','Dead');
    model status(event='Dead') = {var};
run;
""",
    method="listonly",
)

# %%
sas.submitLST(
    f"""
proc sort data={tbl};
    by {time_var};
run;
""",
    method="listonly",
)

# %%
sas.submitLST(
    f"""
proc sql;
create table _tmp_satrrst as
select * from {tbl}
where bp_status = 'High'; 
quit;
    
proc freq data=work._tmp_satrrst noprint;
    by {time_var};
    tables {var} * {target} / out =_test2_vols;
    test smdrc;
    output out=_test3 smdrc;
run;
""",
    method="listonly",
)
# %%
_lib, _tbl = "work._test3".split(".")
df = sas.sd2df(_tbl, _lib)
df

# %% [markdown]
# ## func
# ####################################################################################################


# %%
def freq_by_time(
    seg_id: int,
    tbl: str,
    target: str,
    var: str,
    time_var: str,
    where_clause: str,
    test_option: str = "smdrc",
):
    code = f"""
    proc sql;
    create table _seg as
    select * from {tbl}
    where {where_clause};
    quit;

    proc sort data=_seg;
        by {time_var};
    run;

    proc freq data=_seg noprint;
        by {time_var};
        tables {var} * {target} / out=_cells;
        test {test_option};
        output out=_stats {test_option};
    run;

    proc summary data=_cells nway;
        class {time_var};
        var count;
        output out=_vol(drop=_type_ _freq_) sum=volume;
    run;

    data _res;
        length segment_id 8 where_clause $400;
        merge _stats(in=a) _vol;
        by {time_var};
        if a;
        segment_id = {seg_id};
        where_clause = "{where_clause}";
    run;
    """
    sas.submit(code, results="text")
    df = sas.sd2df("_res", "work")
    return df


# %%
import saspy

sas = saspy.SASsession()
sas

# %%
sas.submitLST(
    f"""
proc rank
    data=sashelp.heart(where=(status in ('Alive','Dead')))
    out=work.heart2
    groups=10;
    var height;
    ranks height_decile;
run;
""",
    method="listonly",
)
df_h1 = sas.sasdata(f"heart2", "work").head(1)
print(df_h1.T.to_string())

# %%
tbl = "work.heart2"
target = "status"
var = "ageatstart"
time_var = "height_decile"
# %%
df = freq_by_time(
    seg_id=1,
    tbl=tbl,
    target=target,
    var=var,
    time_var=time_var,
    where_clause="bp_status = 'High'",
)
df
# %%
df = freq_by_time(
    seg_id=1,
    tbl=tbl,
    target=target,
    var=var,
    time_var=time_var,
    where_clause="bp_status = 'Normal'",
)
df
# %%
df = freq_by_time(
    seg_id=1,
    tbl=tbl,
    target=target,
    var=var,
    time_var=time_var,
    where_clause="bp_status = 'Optimal'",
)
df

# %%
