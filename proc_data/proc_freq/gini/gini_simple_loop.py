# %%
import saspy

sas = saspy.SASsession()
sas

# %%
def make_somersd_qry(pred_vars, target_var, in_table, out_table):
    qry = f"""
ods select none;
ods output Measures=work._measures_5;
proc freq data={in_table};
    tables ({' '.join(pred_vars)}) * {target_var} / missing all;
run;
ods output close;
ods select all;

data {out_table};
    length
        variable $64;
    set work._measures_5(where=(Statistic="Somers' D R|C"));
    variable = strip(tranwrd(scan(table, 1, '*'), 'Table ', ''));
    gini = Value;
    keep variable gini;
run;
"""
    return qry

# %%
# pred_vars = ["ageatstart",'smoking_status','bp_status',]
pred_vars = ["ageatstart",]
in_table = "sashelp.heart"
target_var = "status"
out_table = "work.res_0"

sas.submitLST(f"proc sql;drop table {out_table};quit;", method="listonly")

qry = make_somersd_qry(pred_vars, target_var, in_table, out_table)
sas.submitLST(qry, method="listandlog")

# %%
_lib, _tbl = out_table.split(".")
df = sas.sd2df(_tbl, _lib)
df
