# %%
import saspy

sas = saspy.SASsession()
sas
# %%
sas.submitLST(
    f"""
ods select none;
ods output Measures=work._measures5 CrossTabFreqs=work._crossfreq5;
proc freq data=sashelp.heart;
    tables ageatstart * status / missing all;
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
assert df.loc[df['Statistic'] == "Somers' D R|C",'Value'].values[0] - 0.509876 < 0.00001, 'not match'

# %%
qry = f"""
proc logistic data=sashelp.heart plots(only)=roc;
    model status(event='Dead') = ageatstart;
    output out=work._pred p=phat;
run;
"""
sas.submitLST(qry, method="listonly")