
# %%
import saspy

sas = saspy.SASsession()
sas

# %% [markdown]
#  ## example data
#  ####################################################################################################

# %%
tbl = "sashelp.heart"

# %%
_lib, _tbl = tbl.split(".")
sd = sas.sasdata(_tbl, _lib)
_shape, df_h = (sd.obs(), len(sd.columnInfo())), sd.head()
print(_shape)
df_h


# %% [markdown]
#  ## features - stats
#  ####################################################################################################

# %%
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
""",
    method="listandlog",
)

sas.submitLST(
    f"""
proc print data=work._measures5 (obs=20 where=(Statistic="Somers' D R|C"));
run;
""",
    method="listonly",
)

# %%
# smdrc output
sas.submitLST(
    f"""
proc freq data={tbl} noprint;
    tables smoking * status / measures;
    output out=work._measures5 smdrc;
run;
""",
    method="listandlog",
)
sas.submitLST(
    f"""
proc print data=work._measures5 (obs=20);
run;
""",
    method="listonly",
)

# %%
# check
sas.submitLST(
    f"""
proc logistic data={tbl} plots(only)=roc;
    where status in ('Alive', 'Dead');
    model status(event='Dead') = smoking;
    output out=work._pred p=phat;
run;
""",
    method="listonly",
)

