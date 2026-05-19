# %%

import os
from concurrent.futures import ProcessPoolExecutor, as_completed

import pandas as pd


def _run_segment_job(args):
    import saspy

    seg_id, where_clause, tbl, var, target, time_var = args
    sas = saspy.SASsession()
    print(f"Running segment {seg_id} with where clause: {where_clause}")

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
        test smdrc;
        output out=_stats smdcr;
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


def run_all_segments_parallel(tbl, var, target, time_var, segments, max_workers=4):
    jobs = [(i + 1, wc, tbl, var, target, time_var) for i, wc in enumerate(segments)]
    out = []

    with ProcessPoolExecutor(max_workers=max_workers) as ex:
        futs = [ex.submit(_run_segment_job, j) for j in jobs]
        for f in as_completed(futs):
            out.append(f.result())

    if out:
        return pd.concat(out, ignore_index=True)
    return pd.DataFrame()


# %% [markdown]
# ## run
# ####################################################################################################

# %%
import saspy

sas = saspy.SASsession()
sas

# %%
# Example segment list (add all combinations you need)
segments = [
    "bp_status = 'High'",
    "bp_status = 'Normal'",
    "bp_status = 'Optimal'",
    "bp_status = 'High' and weight_status = 'Overweight'",
]

# %%
tbl = "work.heart2"
target = "status"
var = "ageatstart"
time_var = "height_decile"
# %%
df_all = run_all_segments_parallel(
    tbl="work.heart2",
    var=var,
    target=target,
    time_var=time_var,
    segments=segments,
    max_workers=2,
)
print(df_all.head())
