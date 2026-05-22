

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
    # cube spec (vanilla, by one vari, or full custom labels)
    if custom_spec is not None:
        cube_dim_cols = ", ".join([f"'{custom_spec[v]}' as {v}" for v in varis])
        grp_cls = ""
        h1_grp_cls = ""
        p_grp_cls = ""
        join_cls_1 = ""
        join_cls_2 = ""
    elif vari == "":
        cube_dim_cols = ", ".join([f"'All' as {v}" for v in varis])
        grp_cls = ""
        h1_grp_cls = ""
        p_grp_cls = ""
        join_cls_1 = ""
        join_cls_2 = ""
    elif vari in varis:
        other_varis = [v for v in varis if v != vari]
        cube_dim_cols = ", ".join(
            [f"p.{vari}"] + [f"'All' as {v}" for v in other_varis]
        )
        grp_cls = f"{vari},"
        h1_grp_cls = f"h1.{vari},"
        p_grp_cls = f"p.{vari},"
        join_cls_1 = f"and h1.{vari} = h2.{vari}"
        join_cls_2 = f"and p.{vari} = b.{vari}"
    else:
        raise ValueError("Invalid vari or custom_spec")

    # optional filter for custom run
    if custom_spec is not None:
        where = custom_spec["WHERE_CLAUSE"]
        filter_code = f"""
proc sql;
create table _tmp_psi_in as
    select *
    from {tbl}
    where {where};
quit;
"""
        tbl_in = "_tmp_psi_in"
    else:
        filter_code = ""
        tbl_in = tbl

    qry = f"""
{filter_code}

proc sql;
    create table _base_dist as
    select
        {h1_grp_cls}
        h1.{psi_cat_var},
        h1.n as n_base,
        h1.n / h2.n as p_base
    from (
        select {grp_cls} {psi_cat_var}, count(*) as n
        from {tbl_in}
        where {psi_base_cls}
        group by {grp_cls} {psi_cat_var}
    ) h1
    left join (
        select
            {grp_cls}
            count(*) as n
        from {tbl_in}
        where {psi_base_cls}
        group by {grp_cls}
    ) h2
    on 1=1
    {join_cls_1}
    ;

    create table _period_dist as
    select
        {h1_grp_cls}
        h1.{row_col},
        h1.{psi_cat_var},
        h1.n as n_t,
        h1.n / h2.n as p_t
    from (
        select {grp_cls} {row_col}, {psi_cat_var}, count(*) as n
        from {tbl_in}
        group by {grp_cls} {row_col}, {psi_cat_var}
    ) h1
    left join (
        select
            {grp_cls}
            {row_col},
            count(*) as n
        from {tbl_in}
        group by {grp_cls} {row_col}
    ) h2
    on h1.{row_col} = h2.{row_col}
    {join_cls_1}
    ;

    create table _psi_detail as
    select
        {p_grp_cls}
        p.{row_col},
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
       {join_cls_2}
    ;

    create table {tbl_out} as
    select
        {cube_dim_cols},
        p.{row_col},
        '{psi_cat_var}' as psi_variable,
        sum(p.psi_component) as psi
    from _psi_detail p
    group by {grp_cls} p.{row_col}, psi_variable
    order by {grp_cls} p.{row_col}, psi_variable
    ;
quit;
"""
    return qry


# %%
if __name__ == "__main__":

    import saspy

    sas = saspy.SASsession()
    sas

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
    print("Test 1 (all dims):", df1.shape)

    # by 1 factor
    qry2 = make_psi_fixed_base_qry(
        tbl="work.heart2",
        vari="weight_status",
        varis=["chol_status", "bp_status", "weight_status"],
        psi_cat_var="smoking_status",
        row_col="age_decile",
        psi_base_cls="age_decile between 0 and 2",
    )
    sas.submitLST(qry2, method="listonly")
    df2 = sas.sasdata("_test_res", "work").to_df()
    print("Test 2 (weight_status):", df2.shape)

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
            "weight_status": "Normal",
            "WHERE_CLAUSE": "chol_status in ('High','Borderline') and bp_status='High'",
        },
    )
    sas.submitLST(qry3, method="listonly")
    df3 = sas.sasdata("_test_res", "work").to_df()
    print("Test 3 (custom where):", df3.shape)
