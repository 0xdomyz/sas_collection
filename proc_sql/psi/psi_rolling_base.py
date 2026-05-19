import saspy

# %%
sas = saspy.SASsession()
sas
# %%
sas.submitLST(
    f"""
data heart_time_raw;
    set sashelp.heart(keep=ageatstart smoking_status);
    where not missing(ageatstart);
    if missing(smoking_status) then smoking_status = 'MISSING';
run;

proc rank data=heart_time_raw groups=10 out=heart_time;
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
sas.submitLST(
    f"""
proc freq data=heart_time;
    tables age_decile * smoking_status / missing;
run;
""",
    method="listonly",
)

# %%
PSI_IN_TABLE = "heart_time"
PSI_OUT_TABLE = "psi_by_period_rolling"
PSI_EPS = 1e-6

# %%
sas.submitLST(
    f"""
proc sql;
    create table period_dist as
    select
        age_decile,
        smoking_status,
        count(*) as n_t,
        calculated n_t / (select count(*) from {PSI_IN_TABLE} h2 where h2.age_decile=h1.age_decile) as p_t
    from {PSI_IN_TABLE} h1
    group by age_decile, smoking_status;

    create table psi_detail as
    select
        p.age_decile,
        coalesce(p.smoking_status, b.smoking_status) as smoking_status length=16,
        coalesce(b.p_t, 0) as p_base,
        coalesce(p.p_t, 0) as p_t,
        (
            (max(calculated p_t, {PSI_EPS}) - max(calculated p_base, {PSI_EPS}))
            * log(max(calculated p_t, {PSI_EPS}) / max(calculated p_base, {PSI_EPS}))
        ) as psi_component
    from period_dist p
    full join period_dist b
        on p.smoking_status = b.smoking_status
       and b.age_decile = p.age_decile - 1
    where p.age_decile >= 1;

    create table {PSI_OUT_TABLE} as
    select
        age_decile,
        sum(psi_component) as psi format=8.4
    from psi_detail
    group by age_decile
    order by age_decile;
quit;
    """,
    method="listonly",
)

# %%
_lib, _tbl = f"work.{PSI_OUT_TABLE}".split(".")
df = sas.sd2df(_tbl, _lib)
df

# %%
df.plot(
    x="age_decile",
    y="psi",
    kind="line",
    title="PSI by Age Decile (Rolling Base)",
    legend=False,
)
