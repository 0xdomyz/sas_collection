import saspy

# %%
sas = saspy.SASsession()
sas
# %%
sas.submitLST(
    f"""
proc rank data=sashelp.heart groups=20 out=heart_time;
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


# %% [markdown]
# ## func
# ####################################################################################################

# %%
psi_in_table = "heart_time"
psi_time_var = "age_decile"
psi_cat_var = "smoking_status"
psi_out_table = "psi_by_period1"
psi_base_cls = f"{psi_time_var} between 0 and 9"
psi_eps = 1e-6

# %%
qry = f"""
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

    create table time_levels as
    select distinct {psi_time_var}
    from {psi_in_table};

    create table cat_levels as
    select {psi_cat_var}
    from base_dist
    union
    select distinct {psi_cat_var}
    from period_dist;

    create table period_grid as
    select
        t.{psi_time_var},
        c.{psi_cat_var}
    from time_levels t
    cross join cat_levels c;

    create table psi_detail as
    select
        g.{psi_time_var},
        g.{psi_cat_var},
        coalesce(b.p_base, 0) as p_base,
        coalesce(p.p_t, 0) as p_t,
        (
            (max(calculated p_t, {psi_eps}) - max(calculated p_base, {psi_eps}))
            * log(max(calculated p_t, {psi_eps}) / max(calculated p_base, {psi_eps}))
        ) as psi_component
    from period_grid g
    left join period_dist p
        on g.{psi_time_var} = p.{psi_time_var}
        and g.{psi_cat_var} = p.{psi_cat_var}
    left join base_dist b
        on g.{psi_cat_var} = b.{psi_cat_var};

    create table {psi_out_table} as
    select
        {psi_time_var},
        sum(psi_component) as psi format=8.4
    from psi_detail
    group by {psi_time_var}
    order by {psi_time_var};
quit;
    """
print(qry)
sas.submitLST(qry,method="listonly",)

# %% [markdown]
# ## testing
# ####################################################################################################

# %%
base_dist = sas.sd2df("base_dist", "work")
base_dist

# %%
period_dist = sas.sd2df("period_dist", "work")
period_dist

# %%
time_levels = sas.sd2df("time_levels", "work")
time_levels

# %%
cat_levels = sas.sd2df("cat_levels", "work")
cat_levels

# %%
period_grid = sas.sd2df("period_grid", "work")
period_grid

# %%
psi_detail = sas.sd2df("psi_detail", "work")
psi_detail

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
