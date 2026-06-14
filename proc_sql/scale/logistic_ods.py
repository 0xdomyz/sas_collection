# %%
import saspy

sas = saspy.SASsession()
sas
# %%
qry = f"""
ods select none;
ods output 
    ParameterEstimates = work._ParameterEstimates
;
proc logistic data=sashelp.heart;
    model status(event='Dead') = ageatstart;
    output out=work._pred p=phat;
run;
ods output close;
ods select all;
"""
sas.submitLST(qry, method="listandlog")

# %%
sas.submitLST(
    f"""
proc print data=work._ParameterEstimates;
run;
""",
    method="listonly",
)