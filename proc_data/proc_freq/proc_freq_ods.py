
# %%
import saspy

sas = saspy.SASsession()
sas

# %% [markdown]
#  ## example data
#  ####################################################################################################

# %%
tbl = "sashelp.heart"

# %%
_lib, _tbl = tbl.split(".")
sd = sas.sasdata(_tbl, _lib)
_shape, df_h = (sd.obs(), len(sd.columnInfo())), sd.head()
print(_shape)
df_h

# %% [markdown]
# ## ods
# ####################################################################################################
# %%
sas.submitLST(
    f"""
ods trace on;
ods select none;
ods output OneWayFreqs=work._OneWayFreqs OneWayChiSq=work._OneWayChiSq;
proc freq data={tbl};
    tables smoking_status / missing all;
run;
ods select all;
ods trace off;
""",
    method="listandlog",
)
# %%
_lib, _tbl = "work._OneWayFreqs".split(".")
df = sas.sd2df(_tbl, _lib)
df
# %%
_lib, _tbl = "work._OneWayChiSq".split(".")
df = sas.sd2df(_tbl, _lib)
df