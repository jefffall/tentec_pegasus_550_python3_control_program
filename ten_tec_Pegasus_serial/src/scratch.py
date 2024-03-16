

def determine_tx_course_fine(Tfreq):

    myfloat =(Tfreq / .0025)
    myint = int((Tfreq / .00250))
    if Tfreq < 4.0:
        keeper = int((Tfreq / .002503))
    elif Tfreq < 20.0:
        keeper = int((Tfreq / .0025004))
    else:
        keeper = int((Tfreq / .0025002))
    diff = (myfloat - myint)  * 2500
    fine = int(diff) + bool(diff%1)
    if fine == 2500:
        fine = 0
    coarse = keeper+18000
    
    return coarse, fine 

coarse, fine = determine_tx_course_fine(7.300000)
print (coarse, fine)


