# %% [markdown]
# ### stas on subsets

# %%
import saspy

sas = saspy.SASsession()
sas

# %% [markdown]
# ## data
# ####################################################################################################

# %%
tbl = "work.heart2"

# %%
# make such time var by deciling
sas.submitLST(
    f"""
proc rank
    data=sashelp.heart(where=(status in ('Alive','Dead')))
    out={tbl}
    groups=10;
    var height;
    ranks height_decile;
run;
""",
    method="listonly",
)

# %%
sas.submitLST(
    f"""
proc freq data={tbl} noprint;
    tables height_decile * status / missing chisq plots(only)=freqplot out=work._tmp_freq outpct;
run;
""",
    method="listonly",
)
df = sas.sasdata("_tmp_freq", "work").to_df()
df

# %% [markdown]
# ## base
# ####################################################################################################
# smdrc table ods
sas.submitLST(
    f"""
ods select none;
ods output Measures=work._measures5;
proc freq data={tbl};
    tables smoking * status / measures;
run;
ods output close;
ods select all;

proc print data=work._measures5 (where=(Statistic="Somers' D R|C"));
run;
""",
    method="listandlog",
)

# %% [markdown]
# ## by
# ####################################################################################################
# %%
sas.submitLST(
    f"""
proc sort data={tbl};
    by height_decile;
run;

ods select none;
ods output Measures=work._measures5;
proc freq data={tbl};
    by height_decile;
    tables smoking * status / measures;
run;
ods output close;
ods select all;

proc print data=work._measures5 (where=(Statistic="Somers' D R|C"));
run;
""",
    method="listandlog",
)

# %%
sas.submitLST(
    f"""
proc sort data={tbl};
    by bp_status weight_status height_decile;
run;

ods select none;
ods output Measures=work._measures5;
proc freq data={tbl};
    by bp_status weight_status height_decile;
    tables smoking * status / measures;
run;
ods output close;
ods select all;

proc print data=work._measures5 (where=(Statistic="Somers' D R|C"));
run;
""",
    method="listandlog",
)

# %%
# check
sas.submitLST(
    f"""
proc sql;
create table _tmp_qry as
    select
        *
    from {tbl} a
    where bp_status = 'Optimal' and weight_status = 'Underweight' and height_decile = 5 /*-0.167*/
    ;
quit;
""",
    method="listandlog",
)
sas.submitLST(
    f"""
proc logistic data=_tmp_qry plots(only)=roc;
    where status in ('Alive','Dead');
    model status(event='Dead') = smoking;
    output out=work._pred p=phat;
run;
""",
    method="listonly",
)
