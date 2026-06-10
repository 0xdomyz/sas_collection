# %%
import saspy

sas = saspy.SASsession()
sas

# %%
sas.submitLST(
    f"""
proc rank data=sashelp.heart groups=20 out=heart_time;
    var ageatstart;
    ranks age_decile;
run;

proc print data=heart_time(obs=10);
run;
""",
    method="listonly",
)

# %%
psi_in_table = "heart_time"
psi_cat_var = "smoking_status"
psi_base_cls = f"age_decile between 0 and 9"

sas.submitLST(
    f"""
proc sql;
    create table base_dist as
    select
        {psi_cat_var},
        count(*) as n_base,
        calculated n_base / (
            select count(*) from {psi_in_table} where {psi_base_cls}
        ) as p_base
    from {psi_in_table}
    where {psi_base_cls}
    group by {psi_cat_var};
quit;

proc print data=base_dist;
run;
""",
    method="listonly",
)

# %%
psi_t_cls = f"age_decile = 10"

sas.submitLST(
    f"""
proc sql;
    create table t_dist as
    select
        {psi_cat_var},
        count(*) as n_t,
        calculated n_t / (
            select count(*) from {psi_in_table} where {psi_t_cls}
        ) as p_t
    from {psi_in_table}
    where {psi_t_cls}
    group by {psi_cat_var};
quit;

proc print data=t_dist;
run;
""",
    method="listonly",
)

# %%
psi_eps = 1e-6

sas.submitLST(f"""
proc sql;
    create table psi_detail as
    select
        coalesce(b.{psi_cat_var}, t.{psi_cat_var}) as {psi_cat_var},
        coalesce(b.p_base, 0) as p_base,
        coalesce(t.p_t, 0) as p_t,
        (
            (max(calculated p_t, {psi_eps}) - max(calculated p_base, {psi_eps}))
            * log(max(calculated p_t, {psi_eps}) / max(calculated p_base, {psi_eps}))
        ) as psi_component
    from base_dist b
    full outer join t_dist t
        on b.{psi_cat_var} = t.{psi_cat_var};

    create table work._psi_out_tbl as
    select
        sum(psi_component) as psi format=8.4
    from psi_detail;

    proc print data=work._psi_out_tbl;
    run;
quit;
    """
    ,method="listandlog",)

# %%
_lib, _tbl = "work._psi_out_tbl".split(".")
df = sas.sd2df(_tbl, _lib)
assert df.iloc[0, 0] - 0.045331 < 1e-4, "not match"