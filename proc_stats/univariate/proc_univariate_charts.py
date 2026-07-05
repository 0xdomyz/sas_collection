# %%
import saspy

sas = saspy.SASsession()


# %% [markdown]
# ### stat graphs

# %%
# cdf
# distributions incl: normal beta exponential gamma lognormal weibull
# noprint for chart only
sas.submitLST(
f"""
proc univariate data=sashelp.cars noprint;
    var msrp;
    cdfplot msrp / lognormal;
run;
""", method="listorlog")

# %%
# histogram
sas.submitLST(
f"""
proc univariate data=sashelp.cars noprint;
    var msrp;
    histogram msrp / lognormal;
run;
""", method="listorlog")

# %%
# qqplot
sas.submitLST(
f"""
proc univariate data=sashelp.cars noprint;
    var msrp;
    qqplot msrp / lognormal(scale=est shape=est threshold=est);
run;
""", method="listorlog")

# %%
# ppplot
sas.submitLST(
f"""
proc univariate data=sashelp.cars noprint;
    var msrp;
    ppplot msrp / lognormal;
run;
""", method="listorlog")

# %%
# probplot
sas.submitLST(
f"""
proc univariate data=sashelp.cars noprint;
    var msrp;
    probplot msrp / lognormal(shape=est);
run;
""", method="listorlog")

# %%


# %%


# %%



