
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
#  ## features - general
#  ####################################################################################################

# %%
# tables

# %%
sas.submitLST(
    f"""
proc freq data={tbl};
    tables smoking_status;
run;
""",
    method="listonly",
)

# %%
sas.submitLST(
    f"""
proc freq data={tbl};
    tables smoking_status * status / chisq;
run;
""",
    method="listonly",
)

# %%
# plots
sas.submitLST(
    f"""
proc freq data={tbl};
    tables sex * smoking_status * status / 
    chisq cmh plots(only)=freqplot;
run;
""",
    method="listonly",
)

# %%
# measures
sas.submitLST(
    f"""
proc freq data={tbl};
    tables smoking_status * status / measures;
run;
""",
    method="listonly",
)

# %%
# test
sas.submitLST(
    f"""
proc freq data={tbl};
    tables smoking_status * status;
    test smdrc;
run;
""",
    method="listonly",
)

# %%
# cross all and extract df

# %%
sas.submitLST(
    f"""
proc freq data={tbl};
    tables smoking_status * status / all;
    output out=work._tmp_freq measures;
run;
""",
    method="listonly",
)
_lib, _tbl = "work._tmp_freq".split(".")
df = sas.sd2df(_tbl, _lib)
df.T

# %%
# cross all and plot

# %%
sas.submitLST(
    f"""
proc freq data={tbl};
    tables smoking_status * status / chisq plots(only)=freqplot out=work._freq outpct;
run;
""",
    method="listonly",
)

# %%
sas.submitLST(
    f"""
proc freq data={tbl};
    tables smoking_status / chisq plots(only)=freqplot;
run;
""",
    method="listonly",
)
