# %%
import saspy

sas = saspy.SASsession()
sas

# %%
sas.submitLST(
    f"""
proc rank data=sashelp.heart groups=20 out=heart_time;
    var ageatstart;
    ranks age_decile;
run;

proc print data=heart_time(obs=10);
run;
""",
    method="listonly",
)

# %%
psi_in_table = "heart_time"
psi_base_cls = f"age_decile between 0 and 9"
psi_t_cls = f"age_decile = 10"
psi_eps = 1e-6


def make_fixed_simple_psi_qry(psi_cat_var, psi_in_table, psi_base_cls, psi_t_cls, psi_eps):

    qry = f"""
proc sql;
    create table _base_dist_5 as
    select
        {psi_cat_var},
        count(*) as n_base,
        calculated n_base / (
            select count(*) from {psi_in_table} where {psi_base_cls}
        ) as p_base
    from {psi_in_table}
    where {psi_base_cls}
    group by {psi_cat_var};

    create table _t_dist_5 as
    select
        {psi_cat_var},
        count(*) as n_t,
        calculated n_t / (
            select count(*) from {psi_in_table} where {psi_t_cls}
        ) as p_t
    from {psi_in_table}
    where {psi_t_cls}
    group by {psi_cat_var};

    create table _psi_detail_5 as
    select
        coalesce(b.{psi_cat_var}, t.{psi_cat_var}) as {psi_cat_var},
        coalesce(b.p_base, 0) as p_base,
        coalesce(t.p_t, 0) as p_t,
        (
            (max(calculated p_t, {psi_eps}) - max(calculated p_base, {psi_eps}))
            * log(max(calculated p_t, {psi_eps}) / max(calculated p_base, {psi_eps}))
        ) as psi_component
    from _base_dist_5 b
    full outer join _t_dist_5 t
        on b.{psi_cat_var} = t.{psi_cat_var};

    create table work._psi_out_tbl_5 as
    select
        '{psi_cat_var}' as variable,
        sum(psi_component) as psi format=8.4
    from _psi_detail_5;
quit;

proc print data=work._psi_out_tbl_5;
run;
"""
    return qry


# %%
psi_vars = ["smoking_status", "bp_status"]

for psi_cat_var in psi_vars:
    qry = make_fixed_simple_psi_qry(psi_cat_var, psi_in_table, psi_base_cls, psi_t_cls, psi_eps)
    sas.submitLST(qry, method="listonly")
