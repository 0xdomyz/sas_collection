# %%
import saspy

sas = saspy.SASsession()
sas

# %% [markdown]
# ### data

# %%
sas.submitLST(f"""
    proc logistic data=sashelp.cars order=freq noprint;
        model origin (event='Asia') = mpg_city mpg_highway weight / link=glogit;
        ouput out=cars_est predprobs=INDIVIDUAL;
    run;
    
    title;
    proc print data=cars_est (obs=5);
        var origin mpg_city mpg_highway weight _from_ _into_;
    run;
""")


# %%

_lib, _tbl = "work._pred".split(".")
sd = sas.sasdata(_tbl, _lib)
_shape, df_h = (sd.obs(), len(sd.columnInfo())), sd.head()
print(_shape)
df_h

# %% [markdown]
# ### proc freq
#

# %%
# tables
sas.submitLST(f"""
proc freq data=cars_est;
    tables _from_ / missing;
run;
title;
""")


# %%
# tables w/ interaction
sas.submitLST(f"""
PROC FREQ DATA = cars_est; 
    TABLES _from_ * _into_ / missing; 
RUN;
""")

# %%
# statistical options to control outputs
sas.submitLST(f"""
PROC FREQ DATA = cars_est; 
    TABLES _from_ * _into_ / missing nocum norow nocol nopercent;
RUN;
""")

# %%
# long format via LIST
sas.submitLST(
    f"""
PROC FREQ DATA = cars_est noprint;
    TABLES _from_ * _into_ / LIST MISSING out = df; 
RUN;
              
PROC PRINT DATA = df ;
RUN;
""",
    method="listorlog",
)


# %%
# somers d
sas.submitLST(
    f"""
title;
proc freq data=sashelp.heart;
    tables weight_status * status;
    test smdcr;
run;
""",
    method="listonly",
)
