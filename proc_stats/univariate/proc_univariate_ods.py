# %%
import saspy

sas = saspy.SASsession()


# %%
# ods
sas.submitLST(
    f"""
ods trace on;
proc univariate data=sashelp.heart;
    var ageatstart;
run;
ods trace off;
""",
    method="listandlog",
)
