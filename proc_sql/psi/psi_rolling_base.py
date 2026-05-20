# %%

import saspy

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
category_var = "weight_status"
# category_var = None
psi_time_var = "age_decile"
psi_cat_var = "smoking_status"
psi_out_table = "psi_by_period_rolling"
time_interval = 1
early_time = 0
psi_eps = 1e-6

# %%
sas.submitLST(
    f"""
proc sql;
create table heart_time2 as
    select
        a.*
    from heart_time a
    where
        weight_status = 'Underweight'
    ;
quit;
""",
    method="listonly",
)
# psi_in_table = "heart_time2"

# %%
category_cls = "" if category_var is None else f"{category_var},"
h1_category_cls = "" if category_var is None else f"h1.{category_var},"
p_category_cls = "" if category_var is None else f"p.{category_var},"
join_cls_1 = (
    f"" if category_var is None else f"and h1.{category_var} = h2.{category_var}"
)
join_cls_2 = f"" if category_var is None else f"and p.{category_var} = b.{category_var}"

# %%
sas.submitLST(
    f"""
proc sql;
    create table period_dist as
    select
        {h1_category_cls}
        h1.{psi_time_var},
        h1.{psi_cat_var},
        h1.n as n_t,
        h1.n / h2.n as p_t
    from (
        select {category_cls} {psi_time_var}, {psi_cat_var}, count(*) as n
        from {psi_in_table}
        group by {category_cls} {psi_time_var}, {psi_cat_var}
    ) h1
    left join (
        select 
            {category_cls}
            {psi_time_var},
            count(*) as n
        from {psi_in_table}
        group by {category_cls} {psi_time_var}
    ) h2
    on h1.{psi_time_var} = h2.{psi_time_var}
    {join_cls_1}
    ;

    create table psi_detail as
    select
        {p_category_cls}
        p.{psi_time_var},
        coalesce(p.{psi_cat_var}, b.{psi_cat_var}) as {psi_cat_var},
        coalesce(b.p_t, 0) as p_base,
        coalesce(p.p_t, 0) as p_t,
        (
            (max(calculated p_t, {psi_eps}) - max(calculated p_base, {psi_eps}))
            * log(max(calculated p_t, {psi_eps}) / max(calculated p_base, {psi_eps}))
        ) as psi_component
    from period_dist p
    full outer join period_dist b
        on p.{psi_cat_var} = b.{psi_cat_var}
       and b.{psi_time_var} = p.{psi_time_var} - {time_interval}
       {join_cls_2}
    where p.{psi_time_var} > {early_time};

    create table {psi_out_table} as
    select
        {category_cls}
        {psi_time_var},
        sum(psi_component) as psi
    from psi_detail
    group by {category_cls} {psi_time_var}
    order by {category_cls} {psi_time_var};
quit;
    """,
    method="listandlog",
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
    title=f"PSI by {psi_time_var.replace('_', ' ').title()} (Rolling Base)",
    legend=False,
)

# %%
df2 = df.copy()
df2.columns = df2.columns.str.strip().str.lower()
df2.pivot_table(
    index=psi_time_var,
    columns=category_var,
    values="psi",
    dropna=False,
)

# %%
