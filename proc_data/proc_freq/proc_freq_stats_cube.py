# %% [markdown]
# ### stas on subsets

# %%
import saspy

sas = saspy.SASsession()
sas

# %%
from make_smdrc_cube_qry import make_smdrc_cube_qry

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
# ## spec
# ####################################################################################################

# %%
sas.submitLST(
    f"""
proc freq data={tbl};
    tables chol_status bp_status weight_status smoking_status;
run;
""",
    method="listandlog",
)

# %%
import pandas as pd

df = pd.read_csv("test.csv")
df

# %% [markdown]
# ## cube
# ####################################################################################################
# %%
varis = ["chol_status", "bp_status", "weight_status", "smoking_status"]
factors = ["smoking", "ageatstart"]
target_col = "status"
row_col = "height_decile"
res_tbl_prefix = "res_"

custom_cubes = pd.read_csv("test.csv")
custom_cubes

# %%
# delete old results
sas.submitLST(
    f"""
proc datasets lib=work nolist;
    delete {res_tbl_prefix}:;
quit;
""",
    method="listandlog",
)


# %%
# overall
qry = make_smdrc_cube_qry(
    tbl=tbl,
    vari="",
    varis=varis,
    factors=factors,
    target_col=target_col,
    row_col=row_col,
    custom_spec=None,
    tbl_out=f"{res_tbl_prefix}all",
)
sas.submitLST(qry, method="listandlog")
df = sas.sasdata(f"{res_tbl_prefix}all", "work").to_df()
df

# %%
# by each vari
for vari in varis:
    qry = make_smdrc_cube_qry(
        tbl=tbl,
        vari=vari,
        varis=varis,
        factors=factors,
        target_col=target_col,
        row_col=row_col,
        custom_spec=None,
        tbl_out=f"{res_tbl_prefix}{vari}",
    )
    sas.submitLST(qry, method="listandlog")

# %%
# by custom
for idx, row in custom_cubes.iterrows():
    qry = make_smdrc_cube_qry(
        tbl=tbl,
        vari="",
        varis=varis,
        factors=factors,
        target_col=target_col,
        row_col=row_col,
        custom_spec=row,
        tbl_out=f"{res_tbl_prefix}custom{idx}",
    )
    sas.submitLST(qry, method="listandlog")

# %%
sas.submitLST(
    f"""
data work.{res_tbl_prefix}cube;
    length {' '.join(varis)} $50
           factor $50
           {row_col} smdrc 8;
    set work.{res_tbl_prefix}:;
run;
""",
    method="listandlog",
)
# %%
_lib, _tbl = f"work.{res_tbl_prefix}cube".split(".")
df = sas.sd2df(_tbl, _lib)
df["odr"] = df["n_target"] / df["n_total"]
df

# %%
# check
# df["chol_status"].unique()
df.iloc[:, :-4].groupby(list(df.columns[:-4]), dropna=False).size().reset_index(
    name="count"
)

# %% [markdown]
# ## plots
# ####################################################################################################

# %%
import xlwings as xw
from xlwings_pivot_dashboard import PivotDashboard

wb = xw.Book()
dashboard = PivotDashboard(wb)
dashboard.write_table(df, sql="")

pivot_configs = [
    # fmt: off
    dict(row_field=row_col,col_field='factor',data_field="smdrc",chart_type="line",),
    dict(row_field=row_col,data_field="n_total",xl_func='average',chart_type="area_stacked",),
    dict(row_field=row_col,data_field="n_target",xl_func='average',chart_type="area_stacked",),
    dict(row_field=row_col,data_field="odr",xl_func='average',chart_type="line",),
    dict(row_field=row_col,col_field='factor',data_field="smdrc",xl_func='count',chart_type="line",),
    # fmt: on
]
dashboard.add_pivots(pivot_configs)

dashboard.add_slicers(
    fields=varis,
)
