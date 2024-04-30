
PROC REG DATA=sashelp.cars OUTEST=estimates;
    MODEL MPG_City = Horsepower;
RUN;
QUIT;

DATA scored;
    SET sashelp.cars;
    IF (_N_ = 1) THEN SET estimates;
    PRED_MPG_City = INTERCEPT + Horsepower*Horsepower;
RUN;

