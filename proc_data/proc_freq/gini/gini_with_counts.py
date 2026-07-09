# %%
import saspy

sas = saspy.SASsession()
sas
# %%
def make_somersd_qry(pred_vars, target_var, in_table, out_table='work._gini_out_5',target_lvl_text='1'):

    qry = f"""

    ods select none;
    ods output Measures=work._measures_5 CrossTabFreqs=work._crossfreq5;
    proc freq data={in_table};
        tables ({' '.join(pred_vars)}) * {target_var} / missing all;
    run;
    ods output close;
    ods select all;

    proc sql;
    create table work._cnt5 as
        select
            strip(tranwrd(scan(table, 1, '*'), 'Table ', '')) as factor length=50,
            sum(frequency) as n_total,
            sum(case when {target_var}={target_lvl_text} then frequency else 0 end) as n_target
        from work._crossfreq5
        where _TYPE_ = '11'
        group by calculated factor
    ;

    proc sql;
    create table {out_table} as
        select
            a.factor,
            a.value as smdrc,
            b.n_total,
            b.n_target
        from (
            select a.*, strip(tranwrd(scan(a.table, 1, '*'), 'Table ', '')) as factor length=50 
            from work._measures_5 a
            where Statistic="Somers' D R|C"
        ) a
        left join work._cnt5 b
            on a.factor = b.factor
        ;
    quit;
    """
    return qry

# %%
pred_vars = ["ageatstart",'smoking_status','bp_status',]
# pred_vars = ["ageatstart",]
in_table = "sashelp.heart"
target_var = "status"
out_table = "work.res_0"

sas.submitLST(f"proc sql;drop table {out_table};quit;", method="listonly")

qry = make_somersd_qry(pred_vars, target_var, in_table, out_table, target_lvl_text="'Alive'")
sas.submitLST(qry, method="listandlog")

# %%
_lib, _tbl = out_table.split(".")
df = sas.sd2df(_tbl, _lib)
df
