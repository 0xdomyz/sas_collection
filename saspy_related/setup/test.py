# %%
import saspy

sas = saspy.SASsession()

# %%
sas.sasdata("cars", "sashelp").head()
