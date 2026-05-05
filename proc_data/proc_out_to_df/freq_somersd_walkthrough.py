# %%
import matplotlib.pyplot as plt
import pandas as pd
import saspy

# Theory note: see proc_output_universal_pattern.md in this folder.
sas = saspy.SASsession()
sas

# %%
# Build a clean analysis table from sashelp.heart
sas.submitLST(
    """
data work.heart2;
    set sashelp.heart(keep=weight_status smoking_status);
    where not missing(weight_status) and not missing(smoking_status);
run;
""",
    method="listonly",
)

_lib, _tbl = "work.heart2".split(".")
df_h = sas.sasdata(_tbl, _lib).head()
df_h

# %% [markdown]
# ## Interactive cell 1: output shown in results only (no output datasets requested)
# ####################################################################################################
# %%

sas.submitLST(
    """
title "PROC FREQ with Somers' D (display only)";
proc freq data=work.heart2;
    tables weight_status*smoking_status / all;
run;
title;
""",
    method="listonly",
)

# %% [markdown]
# ## Interactive cell 2: same analysis, now also capture ODS tables as datasets (<=20 SAS lines)
# ####################################################################################################
# %%
# ods trace
sas.submitLST(
    """
ods trace on;
proc freq data=work.heart2;
    tables weight_status*smoking_status / measures;
run;
ods trace off;
""",
    method="listandlog",
)

# %%
sas.submitLST(
    """
title "PROC FREQ with Somers' D (capture ODS tables)";
ods output Measures=work.freq_measures CrosstabFreqs=work.freq_cells;
proc freq data=work.heart2;
    tables weight_status*smoking_status / measures;
run;
ods output close;
title;
""",
    method="listonly",
)

# %%
# Simple inspect cell (5 SAS lines)
sas.submitLST(
    """
proc contents data=work.freq_measures; run;
proc print data=work.freq_measures(obs=10); run;
""",
    method="listonly",
)

# %%
# Simple Python plot (~10 lines): stacked counts by weight_status and smoking_status
cells = sas.sasdata2dataframe(table="freq_cells", libref="work")
plot_df = (
    cells.loc[
        cells["_TYPE_"].eq("11"), ["Weight_Status", "Smoking_Status", "Frequency"]
    ]
    .pivot_table(
        index="Weight_Status",
        columns="Smoking_Status",
        values="Frequency",
        aggfunc="sum",
    )
    .fillna(0)
)
ax = plot_df.plot(kind="bar", stacked=True, figsize=(8, 4), colormap="tab20")
ax.set_title("Heart Dataset: Smoking Status by Weight Status")
ax.set_xlabel("Weight Status")
ax.set_ylabel("Count")
plt.tight_layout()
plt.show()

# %% [markdown]
# ## Interactive cell 3: Explicit `OUTPUT` statements (common in modeling procedures).
# ####################################################################################################
# %%
# Run PROC LOGISTIC on sashelp.heart; OUTPUT OUT= writes predicted probs row-by-row.
sas.submitLST(
    """
proc logistic data=sashelp.heart;
    where status in ('Alive', 'Dead');
    model status(event='Dead') = weight smoking;
    output out=work.heart_pred p=p_dead;
run;
""",
    method="listonly",
)

# %%
# Inspect the output dataset schema and first rows
sas.submitLST(
    """
proc contents data=work.heart_pred; run;
proc print data=work.heart_pred(obs=10); var status weight smoking p_dead; run;
""",
    method="listonly",
)

# %%
# Python plot: distribution of predicted probability of death by actual status
df_pred = sas.sasdata2dataframe(table="heart_pred", libref="work")
fig, ax = plt.subplots(figsize=(7, 4))
for label, grp in df_pred.groupby("Status"):
    ax.hist(grp["p_dead"], bins=30, alpha=0.6, label=label)
ax.set_title("Predicted P(Dead) by Actual Status — PROC LOGISTIC OUTPUT")
ax.set_xlabel("Predicted probability")
ax.set_ylabel("Count")
ax.legend()
plt.tight_layout()
plt.show()

# %%
sas.submitLST(
    f"""
proc freq data=work.heart2;
    tables weight_status*smoking_status / measures;
    output out=work.freq_measures2
        measures      /* Somers' D, Gamma, Tau-b, etc. */
        chisq         /* Chi-square statistics */
        fisher        /* Fisher's exact test */
        cmh           /* Cochran-Mantel-Haenszel */
    ;
run;
""",
    method="listonly",
)
_lib, _tbl = "work.freq_measures2".split(".")
df = sas.sd2df(_tbl, _lib)
print(df.shape)
print(df.head().to_string())
