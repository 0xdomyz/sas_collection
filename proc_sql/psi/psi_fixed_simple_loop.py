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

def make_fixed_simple_psi_qry(psi_cat_var, in_table, base_cls, t_cls, out_table="work._psi_out_tbl_5", psi_eps = 1e-6):

    qry = f"""
proc sql;
    create table _base_dist_5 as
    select
        {psi_cat_var},
        count(*) as n_base,
        calculated n_base / (
            select count(*) from {in_table} where {base_cls}
        ) as p_base
    from {in_table}
    where {base_cls}
    group by {psi_cat_var};

    create table _t_dist_5 as
    select
        {psi_cat_var},
        count(*) as n_t,
        calculated n_t / (
            select count(*) from {in_table} where {t_cls}
        ) as p_t
    from {in_table}
    where {t_cls}
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

    create table {out_table} as
    select
        '{psi_cat_var}' as variable,
        sum(psi_component) as psi format=8.4
    from _psi_detail_5;
quit;

/*proc print data={out_table};*/
/*run;*/
"""
    return qry

# %%
sas.submitLST(f"proc datasets lib=work nolist; delete res_:; quit;", method="listandlog")

psi_vars = ["smoking_status", "bp_status"]
in_table = "heart_time"
base_cls = f"age_decile between 0 and 9"
t_cls = f"age_decile = 10"

for i, psi_cat_var in enumerate(psi_vars):
    out_table = f"work.res_{i}"
    qry = make_fixed_simple_psi_qry(psi_cat_var, in_table, base_cls, t_cls, out_table=out_table)
    sas.submitLST(qry, method="listonly")

qry = f"""
data work.res_final;
    length
        variable $50;
    set work.res_:;
run;

proc print data=work.res_final;
run;
"""
sas.submitLST(qry, method="listandlog")

