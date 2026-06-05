# %% [markdown]
# ### desc
# ods output close is needed to stop capturing output to datasets
# ods select none and all encloser supress usual displays


# %%
import saspy

sas = saspy.SASsession()
sas
# %%
sas.submitLST(
    f"""
ods output Measures=work._measures5 CrossTabFreqs=work._crossfreq5;
proc freq data=sashelp.heart;
    tables (bp_status) * status / measures missing;
run;
ods output close;

proc print data=work._measures5;
run;
""",
    method="listonly",
)

# %%
sas.submitLST(
    f"""
ods select none;
ods output Measures=work._measures5 CrossTabFreqs=work._crossfreq5;
proc freq data=sashelp.heart;
    tables bp_status * status / missing all;
run;
ods output close;
ods select all;
""",
    method="listonly",
)
_lib, _tbl = "work._measures5".split(".")
df = sas.sd2df(_tbl, _lib)
df

# %%
sas.submitLST(
    f"""
proc freq data=sashelp.heart;
    tables smoking_status * status / missing all;
    output out=work._tmp_meas measures;
run;
""",
    method="listonly",
)
_lib, _tbl = "work._tmp_meas".split(".")
df = sas.sd2df(_tbl, _lib)
df