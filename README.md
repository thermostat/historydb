
# History DB

Usage:

    dwhist ()
    {
        HISTFILE=/tmp/dwhist;
        python3 ${PWD}/histdb/histdb.py;
        history -r
    }
                