# %%
import saspy

sas = saspy.SASsession()
sas

# %%
_lib, _tbl = "sashelp.heart".split(".")
sd = sas.sasdata(_tbl, _lib)
_shape, df_h = (sd.obs(), len(sd.columnInfo())), sd.head()
print(_shape)
df_h


# %% [markdown]
# ## process
# ####################################################################################################

# %%
input_data = "sashelp.heart"
cols = ["bp_status", "weight_status"]
id_col = "concat_id"
interm_dim_tbl = "work._interm_dim"
interm_tbl = "work._interm"

# %%
col_list = ", ".join(cols)
col_sas_list = " ".join(cols)
join_condition = " and ".join([f"a.{col} = b.{col}" for col in cols])

# %%
qry = f"""
proc sort data={input_data} (keep={col_sas_list}) nodupkey out={interm_dim_tbl};
by {col_sas_list};
run;

data {interm_dim_tbl};
    set {interm_dim_tbl};
    {id_col} = _n_;
run;
"""

sas.submitLST(
    qry,
    method="listandlog",
)

_lib, _tbl = interm_dim_tbl.split(".")
sd = sas.sasdata(_tbl, _lib)
_shape, df_h = (sd.obs(), len(sd.columnInfo())), sd.head()
print(_shape)
df_h

# %%
qry = f"""
proc sql;
    create table {interm_tbl} as
    select a.*, b.{id_col}
    from {input_data} as a
    left join {interm_dim_tbl} as b
    on {join_condition};
quit;

"""

sas.submitLST(
    qry,
    method="listandlog",
)


_lib, _tbl = interm_tbl.split(".")
sd = sas.sasdata(_tbl, _lib)
_shape, df_h = (sd.obs(), len(sd.columnInfo())), sd.head()
print(_shape)
df_h


# %% [markdown]
# ## simulate work on interm data
# ####################################################################################################
# %%
sas.submitLST(
    f"""
proc sql;
create table _tmp_grp as
    select
        {id_col},
        count(1) as n
    from {interm_tbl}
    group by 1
    order by 1;
quit;
""",
    method="listonly",
)

result_table = "work._tmp_grp"

# %%
_lib, _tbl = result_table.split(".")
sd = sas.sasdata(_tbl, _lib)
_shape, df_h = (sd.obs(), len(sd.columnInfo())), sd.head()
print(_shape)
df_h


# %% [markdown]
# ## restore
# ####################################################################################################


# %%
input_data = result_table
input_dim_data = interm_dim_tbl
output_data = "work.restored"
id_col = "concat_id"

# %%
qry = f"""
proc sql;
    create table {output_data} as
    select f.*, d.*
    from {input_data} as f
    left join {input_dim_data} as d
    on f.{id_col} = d.{id_col};
quit;

"""

sas.submitLST(
    qry,
    method="listandlog",
)


_lib, _tbl = output_data.split(".")
sd = sas.sasdata(_tbl, _lib)
_shape, df_h = (sd.obs(), len(sd.columnInfo())), sd.head()
print(_shape)
df_h
