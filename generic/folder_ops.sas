/* where work is */
%put %sysfunc(pathname(work));

/* create a new directory (folder)*/
data _null_;
    rc = dmkdir('C:\path\to\new\folder');
run;

/* list out fodler anad files*/
libname mylib 'C:\path\to\directory';

data _null_;
    dirid = dopen('mylib');
    if dirid > 0 then do;
        total = dnum(dirid);
        do i = 1 to total;
            file = dread(dirid, i);
            put file;
        end;
    end;
    rc = dclose(dirid);
run;

/* delete a file*/
data _null_;
    rc = ddelete('C:\path\to\file.txt');
run;

/* delete a directory*/
data _null_;
    rc = ddelete('C:\path\to\directory');
run;

/* rename a file*/
data _null_;
    rc = drename('C:\path\to\file.txt', 'C:\path\to\new\file.txt');
run;

/* rename a directory*/
data _null_;
    rc = drename('C:\path\to\directory', 'C:\path\to\new\directory');
run;
    
/* copy a file*/
data _null_;
    rc = dcopy('C:\path\to\file.txt', 'C:\path\to\new\file.txt');
run;
    
/* copy a directory*/
data _null_;
    rc = dcopy('C:\path\to\directory', 'C:\path\to\new\directory');
run;

/* move a file*/
data _null_;
    rc = dmove('C:\path\to\file.txt', 'C:\path\to\new\file.txt');
run;

/* move a directory*/
data _null_;
    rc = dmove('C:\path\to\directory', 'C:\path\to\new\directory');
run;

/* get the current working directory*/
data _null_;
    cwd = dgetcwd();
    put cwd;
run;

/* change the current working directory*/
data _null_;
    rc = dchdir('C:\path\to\new\directory');
run;

/* get the current directory*/
data _null_;
    dir = dgetdir();
    put dir;
run;

/* change the current directory*/
data _null_;
    rc = dsetdir('C:\path\to\new\directory');
run;


