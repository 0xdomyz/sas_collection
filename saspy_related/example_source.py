# %%
import saspy

sas = saspy.SASsession()

# %%
with open("example_macro.sas", "r") as f:
    sascode = f.read()
with open("example_macro.sas", "r") as f:
    sascode2 = f.read()
with open("example_macro.sas", "r") as f:
    sascode3 = f.read()

# %%
sas.submitLST(
    f"""
{sascode}
{sascode2}
{sascode3}
run;
"""
)
# %%
sas.sasdata("table_202201", "work").head()
# %%
df = sas.sasdata("table_202201", "work").to_df()
df
# %%
with open("example_macro.sas", "r") as f:
    code1 = f.read()
print(code1)
