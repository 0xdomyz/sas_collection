# %%
import saspy

sas = saspy.SASsession()

# %% [markdown]
# ### data

tbl = "work.heart2"

# %%
qry = f"""
proc sql;
create table {tbl} as
    select
        a.*,
        case when status = "Dead" then 1 else 0 end as dead
    from sashelp.heart a
    ;
quit;
"""
sas.submitLST(qry, method="listonly")

# %%
_lib, _tbl = tbl.split(".")
df_h1 = sas.sasdata(_tbl, _lib).head(1)
print(df_h1.T.to_string())

# %%
sas.submitLST(
    f"""
proc freq data={tbl};
    tables (chol_status smoking_status weight_status status bp_status) / missing;
run;
""",
    method="listonly",
)

# %% [markdown]
# ### tests

# %%
sas.submitLST(
    f"""
proc univariate data={tbl};
    class bp_status;
    var dead;
    histogram dead;
run;
""",
    method="listandlog",
)

# %%
sas.submitLST(
    f"""
PROC TTEST H0 = 0.36 data = {tbl}; 
    VAR dead; 
run;
""",
    method="listorlog",
)

# %%
sas.submitLST(
    f"""
PROC TTEST data = {tbl} (where = (bp_status in ('High', 'Normal'))); 
    class bp_status;
    VAR dead; 
run;
""",
    method="listorlog",
)
