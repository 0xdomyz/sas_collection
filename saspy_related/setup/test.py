# %%
import saspy

sas = saspy.SASsession()

# %%
qry = f"""
proc sql;
create table _tmp_qry as
    select
        *
    from sashelp.cars a
    ;
quit;
"""
sas.submitLST(qry, method="listonly")
df = sas.sasdata("_tmp_qry", "work").to_df()
print(qry)
df

# %%
import xlwings as xw

ws = xw.sheets.active
ws["A1"].value = df
ws.tables.add(source=ws["A1"].expand())

# %%
