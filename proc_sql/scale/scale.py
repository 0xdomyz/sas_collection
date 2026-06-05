# %%
import saspy

sas = saspy.SASsession()
sas
# %%
qry = f"""
ods trace on;
proc logistic data=sashelp.heart plots(only)=roc;
    model status(event='Dead') = ageatstart;
    output out=work._pred p=phat;
run;
ods trace off;
"""
sas.submitLST(qry, method="listandlog")
# %%
qry = f"""
ods select none;
ods output 
    ModelInfo = work._ModelInfo
    NObs = work._NObs
    ResponseProfile = work._ResponseProfile
    ConvergenceStatus = work._ConvergenceStatus
    FitStatistics = work._FitStatistics
    GlobalTests = work._GlobalTests
    ParameterEstimates = work._ParameterEstimates
    OddsRatios = work._OddsRatios
    Association = work._Association
;
proc logistic data=sashelp.heart plots(only)=roc;
    model status(event='Dead') = ageatstart;
    output out=work._pred p=phat;
run;
ods output close;
ods select all;
"""
sas.submitLST(qry, method="listandlog")

# %%
tbls = [
    'work._ModelInfo',
    'work._NObs',
    'work._ResponseProfile',
    'work._ConvergenceStatus',
    'work._FitStatistics',
    'work._GlobalTests',
    'work._ParameterEstimates',
    'work._OddsRatios',
    'work._Association',
]
for tbl in tbls:
    _lib, _tbl = tbl.split(".")
    df = sas.sd2df(_tbl, _lib)
    print(f"Table: {_tbl}")
    print(df.to_string())
    print("\n\n")

# %%
_lib, _tbl = "work._ParameterEstimates".split(".")
df = sas.sd2df(_tbl, _lib)
df