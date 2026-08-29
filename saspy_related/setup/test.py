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
import seaborn as sns

df = sns.load_dataset('titanic')
print(f"{df.shape = }")
print(df.head().to_string())

# %%
import xlwings as xw

# xw.Book()
ws = xw.sheets.active
if ws["A1"].value is not None:
    ws["A1"].expand().clear()
ws["A1"].value = df
ws.tables.add(source=ws["A1"].expand())
# %%
