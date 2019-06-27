
import pandas as pd
import numpy as np


from patterns.base import BasePattern



df = pd.DataFrame({'open':[30.000,18.000,20.000],'high':[18.000,15.000,33.000],'low':[33.000,15.000,18.000],'close':[20.000,18.000,30.000]},index=pd.to_datetime(['2012-11-1','2012-11-2','2012-11-3']))



class MorningStar(BasePattern):
    
    def confirm_pattern(self,*args):
        pt_open,pt_high,pt_low,pt_close = args[0]
        lt_open,lt_high,lt_low,lt_close = args[1]
        rt_open,rt_high,rt_low,rt_close = args[2]
        lt_cond = args[3]
        
        if lt_cond == 'Bullish':
            if lt_close <= pt_close:
                if rt_close > 0.5*(pt_open + pt_close):
                    return 1
        elif lt_cond == 'Bearish':
            if lt_open <= pt_close:
                if rt_close > 0.5*(pt_open + pt_close):
                    return 1
        elif lt_cond == 'Indecisive':
            if lt_open <= pt_close:
                if rt_close > 0.5*(pt_open + pt_close):
                    return 1
        return 0
            
        
        
    
    def iterate(self):
        self.truth = []
        ad = self.df
        for x,y in enumerate(ad):
            
            if x-1 == -1 or x-2 == -1:
                self.truth.append(0)
                continue
                
            prev = ad[x-2]
            last = ad[x-1]
            current = y
            
            prev_op,prev_high,prev_low,prev_close = prev[0],prev[1],prev[2],prev[3]
            last_op,last_high,last_low,last_close = last[0],last[1],last[2],last[3]
            current_op,current_high,current_low,current_close = current[0],current[1],current[2],current[3]
            
            pt = self.f(prev_op,prev_close)
            lt = self.f(last_op,last_close)
            ct = self.f(current_op,current_close)

            # This block below was the only thing I changed
            if pt == 'Bearish' and ct == 'Bullish':
                integer = self.confirm_pattern(
                    (prev_op,prev_high,prev_low,prev_close),
                    (last_op,last_high,last_low,last_close),
                    (current_op,current_high,current_low,current_close),
                    lt
                )

                self.truth.append(integer)
            else:
                self.truth.append(0)
            
        return np.array(self.truth)

class EveningStar(BasePattern):
    
    def confirm_pattern(self,*args):
        pt_open,pt_high,pt_low,pt_close = args[0]
        lt_open,lt_high,lt_low,lt_close = args[1]
        rt_open,rt_high,rt_low,rt_close = args[2]
        lt_cond = args[3]
        
        if lt_cond == 'Bullish':
            if lt_open >= pt_close:
                if rt_close < 0.5*(pt_open+pt_close):
                    return 1
        elif lt_cond == 'Bearish':
            if lt_close >= pt_close:
                if rt_close < 0.5*(pt_open+pt_close):
                    return 1
        elif lt_cond == 'Indecisive':
            if lt_close >= pt_close:
                if rt_close < 0.5*(pt_open+pt_close):
                    return 1
        return 0
 
    
    def iterate(self):
        self.truth = []
        ad = self.df
        for x,y in enumerate(ad):
            
            if x-1 == -1 or x-2 == -1:
                self.truth.append(0)
                continue
                
            prev = ad[x-2]
            last = ad[x-1]
            current = y
            
            prev_op,prev_high,prev_low,prev_close = prev[0],prev[1],prev[2],prev[3]
            last_op,last_high,last_low,last_close = last[0],last[1],last[2],last[3]
            current_op,current_high,current_low,current_close = current[0],current[1],current[2],current[3]
            
            pt = self.f(prev_op,prev_close)
            lt = self.f(last_op,last_close)
            ct = self.f(current_op,current_close)

            # This block below was the only thing I changed
            if pt == 'Bullish' and ct == 'Bearish':
                integer = self.confirm_pattern(
                    (prev_op,prev_high,prev_low,prev_close),
                    (last_op,last_high,last_low,last_close),
                    (current_op,current_high,current_low,current_close),
                    lt
                )

                self.truth.append(integer)
            else:
                self.truth.append(0)
            
        return np.array(self.truth)

