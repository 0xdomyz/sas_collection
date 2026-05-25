# %%


def make_psi_fixed_base_qry(
    tbl: str,
    varis: list,
    psi_cat_var: str,
    row_col: str,
    psi_base_cls: str,
    vari: str = "",
    custom_spec: dict = None,
    tbl_out: str = "_test_res",
    psi_eps=1e-6,
):
    def csv(items):
        return ", ".join(items)

    def gb(items):
        return f"group by {csv(items)}" if items else ""

    if custom_spec is not None:
        dims = []
        cube_dim_cols = [f"'{custom_spec[v]}' as {v}" for v in varis]
        tbl_in = "_tmp_psi_in"
        filter_code = f"""
proc sql;
    create table _tmp_psi_in as
    select *
    from {tbl}
    where {custom_spec["WHERE_CLAUSE"]};
quit;
"""
    elif vari == "":
        dims = []
        cube_dim_cols = [f"'All' as {v}" for v in varis]
        tbl_in = tbl
        filter_code = ""
    elif vari in varis:
        dims = [vari]
        cube_dim_cols = [f"p.{vari}"] + [f"'All' as {v}" for v in varis if v != vari]
        tbl_in = tbl
        filter_code = ""
    else:
        raise ValueError("Invalid vari or custom_spec")

    dim_cols = csv(dims)
    dim_h1 = csv([f"h1.{d}" for d in dims])
    dim_p = csv([f"p.{d}" for d in dims])
    dim_join_h1_h2 = (
        " and " + " and ".join([f"h1.{d} = h2.{d}" for d in dims]) if dims else ""
    )
    dim_join_p_b = (
        " and " + " and ".join([f"p.{d} = b.{d}" for d in dims]) if dims else ""
    )
    grp_prefix = csv(dims) + ", " if dims else ""

    qry = f"""
{filter_code}
proc sql;
    create table _base_dist as
    select
        {dim_h1 + ", " if dim_h1 else ""}h1.{psi_cat_var},
        h1.n as n_base,
        h1.n / h2.n as p_base
    from (
        select {grp_prefix}{psi_cat_var}, count(*) as n
        from {tbl_in}
        where {psi_base_cls}
        {gb(dims + [psi_cat_var])}
    ) h1
    left join (
        select {dim_cols + ", " if dim_cols else ""}count(*) as n
        from {tbl_in}
        where {psi_base_cls}
        {gb(dims)}
    ) h2
    on 1=1
    {dim_join_h1_h2}
    ;

    create table _period_dist as
    select
        {dim_h1 + ", " if dim_h1 else ""}h1.{row_col},
        h1.{psi_cat_var},
        h1.n as n_t,
        h1.n / h2.n as p_t
    from (
        select {grp_prefix}{row_col}, {psi_cat_var}, count(*) as n
        from {tbl_in}
        {gb(dims + [row_col, psi_cat_var])}
    ) h1
    left join (
        select {dim_cols + ", " if dim_cols else ""}{row_col}, count(*) as n
        from {tbl_in}
        {gb(dims + [row_col])}
    ) h2
    on h1.{row_col} = h2.{row_col}
    {dim_join_h1_h2}
    ;

    create table _psi_detail as
    select
        {dim_p + ", " if dim_p else ""}p.{row_col},
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
       {dim_join_p_b}
    ;

    create table {tbl_out} as
    select
        {csv(cube_dim_cols)},
        p.{row_col},
        '{psi_cat_var}' as psi_variable,
        sum(p.psi_component) as psi
    from _psi_detail p
    {gb(dims + [f"p.{row_col}", "psi_variable"])}
    order by {csv([*dims, f"p.{row_col}", "psi_variable"])}
    ;
quit;
"""
    return qry


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
        row_col="age_decile",
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
        vari="weight_status",
        varis=["chol_status", "bp_status", "weight_status"],
        psi_cat_var="smoking_status",
        row_col="age_decile",
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
        row_col="age_decile",
        psi_base_cls="age_decile between 0 and 2",
        custom_spec={
            "chol_status": "(High, Borderline)",
            "bp_status": "High",
            "weight_status": "All",
            "WHERE_CLAUSE": "chol_status in ('High','Borderline') and bp_status='High'",
        },
    )
    sas.submitLST(qry3, method="listonly")
    df3 = sas.sasdata("_test_res", "work").to_df()
    df3.to_csv("tests/psi_fixed_test3_output.tcsv", index=False)
    print("Test 3 (custom where):", df3.shape)
