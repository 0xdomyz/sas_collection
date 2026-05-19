# %% [markdown]
# ## freq_by_time via test option
# ####################################################################################################


# %%
def freq_by_time(
    seg_id: int,
    tbl: str,
    target: str,
    var: str,
    time_var: str,
    where_clause: str,
    test_option: str = "smdrc",
):
    code = f"""
    proc sql;
    create table _seg as
    select * from {tbl}
    where {where_clause};
    quit;

    proc sort data=_seg;
        by {time_var};
    run;

    proc freq data=_seg noprint;
        by {time_var};
        tables {var} * {target} / out=_cells;
        test {test_option};
        output out=_stats {test_option};
    run;

    proc summary data=_cells nway;
        class {time_var};
        var count;
        output out=_vol(drop=_type_ _freq_) sum=volume;
    run;

    data _res;
        length segment_id 8 where_clause $400;
        merge _stats(in=a) _vol;
        by {time_var};
        if a;
        segment_id = {seg_id};
        where_clause = "{where_clause}";
    run;
    """
    sas.submit(code, results="text")
    df = sas.sd2df("_res", "work")
    return df


# %%
import saspy

sas = saspy.SASsession()
sas

# %%
sas.submitLST(
    f"""
proc rank
    data=sashelp.heart(where=(status in ('Alive','Dead')))
    out=work.heart2
    groups=10;
    var height;
    ranks height_decile;
run;
""",
    method="listonly",
)
df_h1 = sas.sasdata(f"heart2", "work").head(1)
print(df_h1.T.to_string())

# %%
tbl = "work.heart2"
target = "status"
var = "ageatstart"
time_var = "height_decile"
# %%
df = freq_by_time(
    seg_id=1,
    tbl=tbl,
    target=target,
    var=var,
    time_var=time_var,
    where_clause="bp_status = 'High'",
)
df
# %%
df = freq_by_time(
    seg_id=1,
    tbl=tbl,
    target=target,
    var=var,
    time_var=time_var,
    where_clause="bp_status = 'Normal'",
)
df
# %%
df = freq_by_time(
    seg_id=1,
    tbl=tbl,
    target=target,
    var=var,
    time_var=time_var,
    where_clause="bp_status = 'Optimal'",
)
df

# %%
