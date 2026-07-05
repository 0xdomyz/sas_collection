# %%
import saspy

sas = saspy.SASsession()

# %%
# percentiles
sas.submitLST(
    f"""
proc univariate data=sashelp.heart;
    var ageatstart;
    output out=work.percentiles pctlpts=3.2 4.8 9.2 pctlpre=P_;
run;
""",
    method="listandlog",
)
_lib, _tbl = "work.percentiles".split(".")
df = sas.sd2df(_tbl, _lib)
df
# %%
[float(i.removeprefix("P_").replace('_','.')) for i in df.columns]
# %%
df.iloc[0].to_list()