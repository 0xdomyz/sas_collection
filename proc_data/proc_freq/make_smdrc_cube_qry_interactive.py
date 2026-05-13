# %%
import saspy

sas = saspy.SASsession()
sas

# %% [markdown]
# ## data
# ####################################################################################################

# %%
tbl = "work.heart2"

# %%
# make such time var by deciling
sas.submitLST(
    f"""
proc rank
    data=sashelp.heart(where=(status in ('Alive','Dead')))
    out={tbl}
    groups=10;
    var height;
    ranks height_decile;
run;
""",
    method="listonly",
)

# %%
_lib, _tbl = tbl.split(".")
df_h1 = sas.sasdata(_tbl, _lib).head(1)
print(df_h1.T.to_string())


# %% [markdown]
# ## cube func
# ####################################################################################################
# %%
varis = ["chol_status", "bp_status", "weight_status", "smoking_status"]
# vari = "weight_status"
vari = ""
# custom_spec = None
custom_spec = {
    # "chol_status": "High or Borderline",
    "chol_status": "(High, Borderline)",
    "bp_status": "High",
    "weight_status": "All",
    "smoking_status": "All",
    "WHERE_CLAUSE": "chol_status in ('High','Borderline') and bp_status='High'",
}

factors = ["smoking", "ageatstart"]
target_col = "status"
target_lvl_text = "'Dead'"
row_col = "height_decile"
tbl_out = "_test_res"

# %%
# test stat qry

# spec
if custom_spec is not None:
    cube_dim_cols = ", ".join([f"'{custom_spec[v]}' as {v}" for v in varis])
    freq_cls = ""
    join_cls = ""
elif vari == "":
    cube_dim_cols = ", ".join([f"'All' as {v}" for v in varis])
    freq_cls = ""
    join_cls = ""
elif vari in varis:
    other_varis = [v for v in varis if v != vari]
    cube_dim_cols = ", ".join([f"a.{vari}"] + [f"'All' as {v}" for v in other_varis])
    freq_cls = f"{vari},"
    join_cls = f"and a.{vari} = b.{vari}"
else:
    raise ValueError("Invalid vari or custom_spec")

# filter
if custom_spec is not None:
    where = custom_spec["WHERE_CLAUSE"]
    filter_code = f"""
    proc sql;
    create table _tmp5 as
        select *
        from {tbl}
        where {where};
    quit;
"""
    tbl_in = "_tmp5"
else:
    filter_code = ""
    tbl_in = tbl


qry = f"""
{filter_code}

proc sort data={tbl_in};
    by {vari} {row_col};

ods select none;
ods output Measures=work._measures5 CrossTabFreqs=work._crossfreq5;
proc freq data={tbl_in};
    by {vari} {row_col};
    tables ({' '.join(factors)}) * {target_col} / measures;
run;
ods output close;
ods select all;

proc sql;
create table work._cnt5 as
    select
        {freq_cls}
        {row_col},
        strip(tranwrd(scan(table, 1, '*'), 'Table ', '')) as factor length=50,
        sum(frequency) as n_total,
        sum(case when {target_col}={target_lvl_text} then frequency else 0 end) as n_target
    from work._crossfreq5
    where _TYPE_ = '11'
    group by {freq_cls} {row_col}, calculated factor
;

proc sql;
create table {tbl_out} as
    select
        {cube_dim_cols},
        a.{row_col},
        a.factor,
        a.value as smdrc,
        b.n_total,
        b.n_target
    from (
        select a.*, strip(tranwrd(scan(a.table, 1, '*'), 'Table ', '')) as factor length=50 
        from work._measures5 a
        where Statistic="Somers' D R|C"
    ) a
    left join work._cnt5 b
        on a.factor = b.factor and a.{row_col} = b.{row_col} {join_cls}
    ;
quit;
"""

# %%
sas.submitLST(qry, method="listandlog")

df = sas.sasdata(tbl_out, "work").to_df()
df["odr"] = df["n_target"] / df["n_total"]
df

# %% [markdown]
# ## test gini
# ####################################################################################################
# %%
df.iloc[-1, :].to_dict()

# %%
sas.submitLST(
    f"""
proc logistic data={tbl_in} (where = (
    chol_status in ('High','Borderline') and bp_status='High'
    and height_decile=9
));
    where status in ('Dead','Alive');
    model status(event='Dead') = smoking;
    output out=work._pred p=phat;
run;
""",
    method="listonly",
)

# %% [markdown]
# ## test total should be the same as freq total
# ####################################################################################################

# %%
# use set up where vari is weight_status and custom_spec is None as example

# # %%
# sas.submitLST(
#     f"""
# proc sql;
# create table _tmp_grp as
#     select
#         {vari},
#         {row_col},
#         {factors[0]},
#         {target_col},
#         count(1) as n
#     from {tbl_in}
#     where weight_status = 'Normal' and height_decile = 0
#     group by 1,2,3,4
#     order by 1,2,3,4;
# quit;
# """,
#     method="listandlog",
# )
# df2 = sas.sasdata("_tmp_grp", "work").to_df()
# df2["n"].sum()

# # %%
# sas.submitLST(
#     f"""
# proc freq data={tbl_in} (where = (weight_status = 'Normal' and height_decile = 0));
#     tables smoking * {target_col} / missing measures;
# run;
# """,
#     method="listandlog",
# )

# %%
