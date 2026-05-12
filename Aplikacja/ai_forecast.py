from datetime import datetime, timedelta
import numpy as np

def predict(times, tmax, tmin, prec):
    last_date = datetime.fromisoformat(times[-1])
    ai_times = [(last_date + timedelta(days=i+1)).date().isoformat() for i in range(7)]

    tmax_array = np.array(tmax[-7:])
    tmin_array = np.array(tmin[-7:])
    
    x = np.arange(len(tmax_array))
    coef_max = np.polyfit(x, tmax_array, 1)
    coef_min = np.polyfit(x, tmin_array, 1)
    
    ai_tmax = [float(np.polyval(coef_max, len(tmax_array) + i) + np.random.normal(0, 1)) for i in range(7)]
    ai_tmin = [float(np.polyval(coef_min, len(tmin_array) + i) + np.random.normal(0, 1)) for i in range(7)]

    last_prec_mean = np.mean(prec[-3:])
    ai_prec = []
    for _ in range(7):
        p = np.random.normal(last_prec_mean, 1)
        p = max(0, min(10, p))
        ai_prec.append(round(p, 1))

    return ai_times, ai_tmax, ai_tmin, ai_prec
