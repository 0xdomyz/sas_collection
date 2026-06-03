# %%


def make_subset_qry(
    tbl: str,
    where_clause: str = "",
    tbl_out: str = "_tmp_psi_in",
):
    if where_clause.strip() == "":
        return "", tbl

    qry = f"""
proc sql;
    create table {tbl_out} as
    select *
    from {tbl}
    where {where_clause};
quit;
"""
    return qry, tbl_out


# %%
def mkcol(col: str, alias: str = "", comma: bool = False):
    if not col:
        return ""
    col = f"{alias}.{col}" if alias else col
    return f"{col}, " if comma else col


def mkgb(cols: list, order_by: bool = False):
    if not cols:
        return ""
    if not isinstance(cols, list):
        cols = [cols]
    cols = [col for col in cols if col]
    if not cols:
        return ""
    gb = f"group by {', '.join(cols)}"
    return f"{gb} order by {', '.join(cols)}" if order_by else gb


def mkjoin(col: str, alias1: str, alias2: str):
    if not col:
        return ""
    return f" and {alias1}.{col} = {alias2}.{col}"


# %%


def make_cube_qry(
    tbl: str,
    cube_variables: list,
    custom_labels: dict = None,
    tbl_out: str = "_test_res",
):

    if custom_labels:
        pass
    else:
        custom_labels = {v: "All" for v in cube_variables}

    cube_dim_cols = [f"'{v}' as {k}" for k, v in custom_labels.items()]

    qry = f"""
proc sql;
    create table {tbl_out} as
    select
        {", ".join(cube_dim_cols)},
        p.*
    from {tbl} p
    ;
quit;
"""
    return qry
