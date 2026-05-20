import saspy

# %%
sas = saspy.SASsession()
sas
# %%
sas.submitLST(
    f"""
proc rank data=sashelp.heart groups=10 out=heart_time;
    var ageatstart;
    ranks age_decile;
run;
""",
    method="listonly",
)

# %%
_lib, _tbl = "work.heart_time".split(".")
df_h = sas.sasdata(_tbl, _lib).head()
df_h


# %%
psi_in_table = "heart_time"
psi_time_var = "age_decile"
psi_cat_var = "smoking_status"
psi_out_table = "psi_by_period1"
psi_base_cls = f"{psi_time_var} between 0 and 9"
psi_eps = 1e-6

# %%
sas.submitLST(
    f"""
proc sql;
    create table base_dist as
    select
        {psi_cat_var},
        count(*) as n_base,
        calculated n_base / (select count(*) from {psi_in_table} where {psi_base_cls}) as p_base
    from {psi_in_table}
    where {psi_base_cls}
    group by {psi_cat_var};

    create table period_dist as
    select
        {psi_time_var},
        {psi_cat_var},
        count(*) as n_t,
        calculated n_t / (select count(*) from {psi_in_table} h2 where h2.{psi_time_var}=h1.{psi_time_var}) as p_t
    from {psi_in_table} h1
    group by {psi_time_var}, {psi_cat_var};

    create table psi_detail as
    select
        p.{psi_time_var},
        coalesce(p.{psi_cat_var}, b.{psi_cat_var}) as {psi_cat_var} length=16,
        coalesce(b.p_base, 0) as p_base,
        coalesce(p.p_t, 0) as p_t,
        (
            (max(calculated p_t, {psi_eps}) - max(calculated p_base, {psi_eps}))
            * log(max(calculated p_t, {psi_eps}) / max(calculated p_base, {psi_eps}))
        ) as psi_component
    from period_dist p
    full join base_dist b
        on p.{psi_cat_var} = b.{psi_cat_var};

    create table {psi_out_table} as
    select
        {psi_time_var},
        sum(psi_component) as psi format=8.4
    from psi_detail
    group by {psi_time_var}
    order by {psi_time_var};
quit;
    """,
    method="listonly",
)

# %%
_lib, _tbl = f"work.{psi_out_table}".split(".")
df = sas.sd2df(_tbl, _lib)
df

# %%
df.plot(
    x=psi_time_var,
    y="psi",
    kind="line",
    title=f"PSI by {psi_time_var.replace('_', ' ').title()}",
    legend=False,
)

# %%
