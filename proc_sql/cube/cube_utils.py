# %%
def mkcol(col: str, alias: str = "", comma: bool = False):
    if not col:
        return ""
    col = f"{alias}.{col}" if alias else col
    return f"{col}, " if comma else col


def mkgbob(cols: list, prefix: str = "group by",order_by: bool = False):
    if not cols:
        return ""
    if not isinstance(cols, list):
        cols = [cols]
    cols = [col for col in cols if col]

    if not cols:
        return ""
    gb = f"{prefix} {', '.join(cols)}"
    return f"{gb} order by {', '.join(cols)}" if order_by else gb


def mkjoin(col: str, alias1: str, alias2: str):
    if not col:
        return ""
    return f" and {alias1}.{col} = {alias2}.{col}"


# %%
def make_cube_qry(
    tbl: str,
    cube_variables: list = None,
    custom_labels: dict = None,
    make_tbl: bool = False,
    out_tbl: str = "_tmp_cube",
):

    if custom_labels:
        pass
    else:
        custom_labels = {v: "All" for v in cube_variables}

    cube_dim_cols = [f"'{v}' as {k}" for k, v in custom_labels.items()]

    tbl_pre = f"proc sql;\n    create table {out_tbl} as" if make_tbl else ""
    tbl_post = f";\n    quit;" if make_tbl else ""

    qry = f"""
    {tbl_pre}
    select
        {", ".join(cube_dim_cols)},
        p.*
    from {tbl} p
    {tbl_post}
"""
    return qry


# %%
if __name__ == "__main__":
    import saspy

    sas = saspy.SASsession()
    sas

    # %%
    res = mkcol("col1", "a", True)
    print(res)
    res = mkcol("", "a", True)
    print(res)
    # %%
    res = mkgbob(["col1", "col2"])
    print(res)
    res = mkgbob([])
    print(res)
    # %%
    res = mkjoin("col1", "a", "b")
    print(res)
    res = mkjoin("", "a", "b")
    print(res)
    res = mkjoin(None, "a", "b")
    print(res)
    # %%
    # data for make cube
    qry = f"""
    proc sql;
    create table _tmp_grp as
        select
            smoking_status,
            count(1) as n
        from sashelp.heart
        group by 1
        order by 1;
    quit;
    """
    sas.submitLST(qry, method="listonly")

    # %%
    sas.submitLST(
        f"""
    proc sql;
    create table work._tmp_cube as
        {make_cube_qry(
            tbl="work._tmp_grp",
            cube_variables=["bp_status", "chol_status"],
            custom_labels=None,
        )};
    quit;

    proc print data=work._tmp_cube (obs=5);
    run;
    """,
        method="listandlog",
    )
    # %%
    sas.submitLST(
        f"""
    proc sql;
    create table work._tmp_cube as
        {make_cube_qry(
            tbl="work._tmp_grp",
            custom_labels={"bp_status": "High", "chol_status": "Low"},
        )};
    quit;

    proc print data=work._tmp_cube (obs=5);
    run;
    """,
        method="listandlog",
    )

    # %%
    sas.submitLST(
        f"""
    {make_cube_qry(
        tbl="work._tmp_grp",
        custom_labels={"bp_status": "High", "chol_status": "Low"},
        make_tbl=True,
        out_tbl="work._tmp_cube2",
    )}

    proc print data=work._tmp_cube2 (obs=5);
    run;
    """,
        method="listandlog",
    )

    # %%
    assert sas.saslog().count('ERROR') == 0