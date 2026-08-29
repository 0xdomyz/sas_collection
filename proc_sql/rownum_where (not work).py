# %%
import saspy

sas = saspy.SASsession()

# %%
import seaborn as sns

df = sns.load_dataset('titanic')
df['id'] = df.index
print(f"{df.shape = }")
print(df.head().to_string())

# %%
tbl = "work.test"
_lib, _tbl = tbl.split(".")
sas.df2sd(df, _tbl, _lib, index=False, if_exists="replace")
sd = sas.sasdata(_tbl, _lib)
_shape = (sd.obs(), len(sd.columnInfo()))
print(_shape)

# %% [markdown]
# ## analysis
# ####################################################################################################

# %%
import xlwings as xw

# xw.Book()
ws = xw.sheets.active
if ws["A1"].value is not None:
    ws["A1"].expand().clear()
ws["A1"].value = df
ws.tables.add(source=ws["A1"].expand())

# %%
id_col = 'who'
dedup_id_col = 'id'
time_col = 'fare'
value_col = 'deck'

qry = f"""
proc sort data={tbl} out=have_sorted;
    by {id_col} {time_col};
run;

* previous-value pass: nearest earlier non-missing value within same id;
data prev;
    set have_sorted;
    by {id_col};
    retain _prev_time _prev_value;

    prev_dist = .;
    prev_value = .;

    if not first.{id_col} and not missing(_prev_value) then do;
        prev_dist = abs({time_col} - _prev_time);
        prev_value = _prev_value;
    end;

    if not missing({value_col}) then do;
        _prev_time = {time_col};
        _prev_value = {value_col};
    end;

    keep {id_col} {time_col} prev_dist prev_value;
run;

* next-value pass: nearest later non-missing value within same id;
proc sort data=have_sorted out=have_sorted_rev;
    by {id_col} descending {time_col};
run;

data next;
    set have_sorted_rev;
    by {id_col};
    retain _next_time _next_value;

    next_dist = .;
    next_value = .;

    if not first.{id_col} and not missing(_next_value) then do;
        next_dist = abs({time_col} - _next_time);
        next_value = _next_value;
    end;

    if not missing({value_col}) then do;
        _next_time = {time_col};
        _next_value = {value_col};
    end;

    keep {id_col} {time_col} next_dist next_value;
run;

* combine previous and next, choose the smaller distance;
data {tbl}_closest;
    merge
        have_sorted (keep={id_col} {time_col} {value_col})
        prev
        next
    ;
    by {id_col} {time_col};

    if missing(prev_dist) and missing(next_dist) then do;
        closest_dist = .;
        closest_value = .;
    end;
    else if missing(prev_dist) then do;
        closest_dist = next_dist;
        closest_value = next_value;
    end;
    else if missing(next_dist) then do;
        closest_dist = prev_dist;
        closest_value = prev_value;
    end;
    else if prev_dist <= next_dist then do;
        closest_dist = prev_dist;
        closest_value = prev_value;
    end;
    else do;
        closest_dist = next_dist;
        closest_value = next_value;
    end;

    keep {id_col} {time_col} {value_col} closest_dist closest_value;
run;
"""
sas.submitLST(qry, method="listandlog")

df = sas.sasdata(f"{_tbl}_closest", _lib).to_df()
df