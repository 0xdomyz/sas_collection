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
# histogram with bin
sas.submitLST(
f"""
proc sgplot data=sashelp.cars;
    histogram msrp / nbins={20};
    density msrp / type=normal;
run;
""", method="listorlog")

# %%
# 2-set histogram (overlay)
sas.submitLST(
f"""
proc sgplot data=sashelp.cars;
    histogram mpg_city / nbins={30} transparency=0.45 legendlabel="MPG City";
    histogram mpg_highway / nbins={30} transparency=0.45 legendlabel="MPG Highway";
    density mpg_city / type=normal legendlabel="City Normal";
    density mpg_highway / type=normal legendlabel="Highway Normal";
    keylegend / position=topright location=inside down=2;
run;
""",
    method="listorlog",
)


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


# %%



