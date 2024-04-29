proc sql;
    connect using oralib as oracle;
    execute(
        merge into "marketproducts" t2
        using "marketproductupdate" t1
        on (
            t2.id = t1.id
        )

        when matched then update
        set 
            t2.product = t1.product,
            t2.price = t1.cost

        when not matched then insert
        (
            t2.id,
            t2.product,
            t2.price
        )
        values
        (
            t1.id,
            t1.product,
            t1.cost
        )
    ) by oracle;
    disconnect from oracle;
quit;
run;

