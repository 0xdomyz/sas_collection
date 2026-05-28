# %%
# %%
import saspy
from cube_utils import make_cube_qry, mkcol, mkgbob

sas = saspy.SASsession()

# %%
_lib, _tbl = "sashelp.heart".split(".")
df_h1 = sas.sasdata(_tbl, _lib).head(1)
print(df_h1.T.to_string())

# %% [markdown]
# ## non func example
# ####################################################################################################


# %%
# col = "bp_status"
col = None
tbl = "sashelp.heart"
cube_variables = [i for i in ["smoking_status", "bp_status", "chol_status"] if i != col]

sas.submitLST(
    f"""
proc sql;
create table _tmp_qry as
    select
        {mkcol(col, "a", True)}
        count(1) as n
    from {tbl} a
    {mkgbob(col)}
    {mkgbob(col, prefix="order by")}
    ;
quit;

proc sql;
create table _tmp_cube as
    {make_cube_qry("work._tmp_qry",cube_variables=cube_variables,)};
quit;
""",
    method="listandlog",
)
_lib, _tbl = "work._tmp_cube".split(".")
df = sas.sd2df(_tbl, _lib)
df

# %% [markdown]
# ## func example
# ####################################################################################################


# %%
def make_freq_tbl_qry(
    tbl,
    col=None,
):
    qry = f"""
    proc sql;
    create table _tmp_qry as
        select
            {mkcol(col, "a", True)}
            count(1) as n
        from {tbl} a
        {mkgbob(col)}
        {mkgbob(col, prefix="order by")}
        ;
    quit;
    """
    return qry


# %%
sas.submitLST(
    f"""
{make_freq_tbl_qry(tbl, None)}
{make_cube_qry("work._tmp_qry",cube_variables=["smoking_status", "chol_status", 'bp_status'],make_tbl=True, out_tbl="work._tmp_cube_0",)}

{make_freq_tbl_qry(tbl, 'bp_status')}
{make_cube_qry("work._tmp_qry",cube_variables=["smoking_status", "chol_status"],make_tbl=True, out_tbl="work._tmp_cube_1",)}

{make_freq_tbl_qry(tbl, 'chol_status')}
{make_cube_qry("work._tmp_qry",cube_variables=["smoking_status", "bp_status"],make_tbl=True, out_tbl="work._tmp_cube_2" ,)}

{make_freq_tbl_qry(tbl, 'smoking_status')}
{make_cube_qry("work._tmp_qry",cube_variables=["bp_status", "chol_status"],make_tbl=True, out_tbl="work._tmp_cube_3" ,)}

data work._tmp_cube_99;
    length smoking_status $50 
           bp_status $50
           chol_status $50
           n 8
    ;
    set work._tmp_cube_0 work._tmp_cube_1 work._tmp_cube_2 work._tmp_cube_3;
run;
""",
    method="listandlog",
)
_lib, _tbl = "work._tmp_cube_99".split(".")
df = sas.sd2df(_tbl, _lib)
df
