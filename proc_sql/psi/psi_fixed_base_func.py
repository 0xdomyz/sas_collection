# %%
import cube_utils as cu
from cube_utils import make_cube_qry, mkcol, mkgbob, mkjoin

# %%


def make_fixed_base_psi_tbl_qry(
    tbl: str,
    psi_cat_var: str,
    time_col: str,
    psi_base_cls: str,
    seg_col: str = "",
    tbl_out: str = "_psi_main",
    psi_eps=1e-6,
):

    qry = f"""
proc sql;
    create table _base_dist as
    select
        {mkcol(seg_col, 'h1', True)}
        h1.{psi_cat_var},
        h1.n as n_base,
        h1.n / h2.n as p_base
    from (
        select 
            {mkcol(seg_col, comma=True)}
            {psi_cat_var}, 
            count(*) as n
        from {tbl}
        where {psi_base_cls}
        {mkgbob([seg_col, psi_cat_var])}
    ) h1
    left join (
        select 
            {mkcol(seg_col, comma=True)}
            count(*) as n
        from {tbl}
        where {psi_base_cls}
        {mkgbob([seg_col])}
    ) h2
    on 1=1
    {mkjoin(seg_col, 'h1', 'h2')}
    ;

    create table _period_dist as
    select
        {mkcol(seg_col, 'h1', True)}
        h1.{time_col},
        h1.{psi_cat_var},
        h1.n as n_t,
        h1.n / h2.n as p_t
    from (
        select 
            {mkcol(seg_col, comma=True)}
            {time_col}, {psi_cat_var}, count(*) as n
        from {tbl}
        {mkgbob([seg_col, time_col, psi_cat_var])}
    ) h1
    left join (
        select 
            {mkcol(seg_col, comma=True)}
            {time_col}, count(*) as n
        from {tbl}
        {mkgbob([seg_col, time_col])}
    ) h2
    on h1.{time_col} = h2.{time_col}
    {mkjoin(seg_col, 'h1', 'h2')}
    ;

    create table _psi_detail as
    select
        {mkcol(seg_col, 'p', True)}
        p.{time_col},
        coalesce(p.{psi_cat_var}, b.{psi_cat_var}) as {psi_cat_var},
        coalesce(b.p_base, 0) as p_base,
        coalesce(p.p_t, 0) as p_t,
        (
            (max(calculated p_t, {psi_eps}) - max(calculated p_base, {psi_eps}))
            * log(max(calculated p_t, {psi_eps}) / max(calculated p_base, {psi_eps}))
        ) as psi_component
    from _period_dist p
    full outer join _base_dist b
        on p.{psi_cat_var} = b.{psi_cat_var}
       {mkjoin(seg_col, 'p', 'b')}
    ;

    create table {tbl_out} as
    select
        {mkcol(seg_col, 'p', True)}
        p.{time_col},
        '{psi_cat_var}' as psi_variable,
        sum(p.psi_component) as psi
    from _psi_detail p
    {mkgbob([seg_col,f"p.{time_col}", "psi_variable"])}
    order by {", ".join([v for v in [seg_col, f"p.{time_col}", "psi_variable"] if v])}
    ;
quit;
"""
    return qry


def make_psi_fixed_base_qry(
    tbl: str,
    varis: list,
    psi_cat_var: str,
    time_col: str,
    psi_base_cls: str,
    seg_col: str = "",
    custom_spec: dict = None,
    tbl_out: str = "_test_res",
    psi_eps=1e-6,
):
    if seg_col and seg_col not in varis:
        raise ValueError("Invalid seg_col")

    if custom_spec:
        if (
            custom_spec["WHERE_CLAUSE"] is None
            or custom_spec["WHERE_CLAUSE"].strip() == ""
        ):
            where_clause = ""
        else:
            where_clause = f"where {custom_spec['WHERE_CLAUSE']}"
    else:
        where_clause = ""

    custom_labels = (
        {v: custom_spec.get(v, "All") for v in varis} if custom_spec else None
    )
    cube_variables = [v for v in varis if v != seg_col]

    main_qry = make_fixed_base_psi_tbl_qry(
        tbl="_psi_interm",
        psi_cat_var=psi_cat_var,
        time_col=time_col,
        psi_base_cls=psi_base_cls,
        seg_col=seg_col,
        tbl_out="_psi_main",
        psi_eps=psi_eps,
    )
    cube_qry = make_cube_qry(
        tbl="_psi_main",
        cube_variables=cube_variables,
        custom_labels=custom_labels,
    )
    res_qry = f"""
proc sql;
    create table _psi_interm as 
    select * from {tbl} 
    {where_clause};
quit;

{main_qry}

proc sql;
create table {tbl_out} as
{cube_qry};
quit;
"""
    return res_qry


# %%
if __name__ == "__main__":

    import saspy

    sas = saspy.SASsession()
    sas
    # %%

    tbl = "work.heart2"

    # make such time var by deciling
    sas.submitLST(
        f"""
    proc rank
        data=sashelp.heart
        out={tbl}
        groups=10;
        var ageatstart;
        ranks age_decile;
    run;
    """,
        method="listonly",
    )

    # %%

    # vanilla
    qry1 = make_psi_fixed_base_qry(
        tbl="work.heart2",
        varis=["chol_status", "bp_status", "weight_status"],
        psi_cat_var="smoking_status",
        time_col="age_decile",
        psi_base_cls="age_decile between 0 and 2",
    )
    sas.submitLST(qry1, method="listandlog")
    df1 = sas.sasdata("_test_res", "work").to_df()
    df1.to_csv("tests/psi_fixed_test1_output.tcsv", index=False)
    print("Test 1 (all dims):", df1.shape)

    # %%

    # by 1 factor
    qry2 = make_psi_fixed_base_qry(
        tbl="work.heart2",
        seg_col="weight_status",
        varis=["chol_status", "bp_status", "weight_status"],
        psi_cat_var="smoking_status",
        time_col="age_decile",
        psi_base_cls="age_decile between 0 and 2",
    )
    sas.submitLST(qry2, method="listandlog")
    df2 = sas.sasdata("_test_res", "work").to_df()
    df2.to_csv("tests/psi_fixed_test2_output.tcsv", index=False)
    print("Test 2 (weight_status):", df2.shape)

    # %%

    # custom where
    qry3 = make_psi_fixed_base_qry(
        tbl="work.heart2",
        varis=["chol_status", "bp_status", "weight_status"],
        psi_cat_var="smoking_status",
        time_col="age_decile",
        psi_base_cls="age_decile between 0 and 2",
        custom_spec={
            "chol_status": "(High, Borderline)",
            "bp_status": "High",
            "weight_status": "All",
            "WHERE_CLAUSE": "chol_status in ('High','Borderline') and bp_status='High'",
        },
    )
    sas.submitLST(qry3, method="listandlog")
    df3 = sas.sasdata("_test_res", "work").to_df()
    df3.to_csv("tests/psi_fixed_test3_output.tcsv", index=False)
    print("Test 3 (custom where):", df3.shape)

# %%
