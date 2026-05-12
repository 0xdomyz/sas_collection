# %%
import saspy

sas = saspy.SASsession()
sas
# %% [markdown]
# ## data
# ####################################################################################################
# %%
sas.submitLST(
    """
proc sql;
    /* Monthly snapshot source from SASHELP */
    create table work.input_data as
    select
        month as event_dt format=date9.,
        actual as metric
    from sashelp.prdsale;
quit;
""",
    method="listonly",
)

df = sas.sasdata("input_data", "work").to_df()
df

# %% [markdown]
# ## process
# ####################################################################################################
# %%
# expansion
sas.submitLST(
    f"""
proc sql;
    create table work.expanded_3yr as
        select
            a.event_dt as window_dt,
            b.event_dt,
            b.metric
        from (
            select distinct event_dt from work.input_data
        ) as a
        inner join work.input_data as b
            on b.event_dt between intnx('month', a.event_dt, -2, 'b') and a.event_dt
    ;
quit;
""",
    method="listandlog",
)
# %%
_lib, _tbl = "work.expanded_3yr".split(".")
df = sas.sd2df(_tbl, _lib)
df

# %% [markdown]
# ## test and metric
# ####################################################################################################


# %%
sas.submitLST(
    f"""
proc sql;
create table _tmp_grp as
    select
        event_dt,
        count(1) as n,
        mean(metric) as avg_metric
    from work.input_data
    group by 1
    order by 1;
quit;
""",
    method="listandlog",
)
df = sas.sasdata("_tmp_grp", "work").to_df()
df

# %%
sas.submitLST(
    f"""
proc sql;
create table _tmp_grp as
    select
        window_dt,
        event_dt,
        count(1) as n,
        mean(metric) as avg_metric
    from work.expanded_3yr
    group by 1,2
    order by 1,2;
quit;
""",
    method="listandlog",
)
df = sas.sasdata("_tmp_grp", "work").to_df()
df

# %%
sas.submitLST(
    f"""
proc sql;
create table _tmp_grp as
    select
        window_dt,
        count(1) as n,
        mean(metric) as avg_metric
    from work.expanded_3yr
    group by 1
    order by 1
    ;
quit;
""",
    method="listandlog",
)
df = sas.sasdata("_tmp_grp", "work").to_df()
df
