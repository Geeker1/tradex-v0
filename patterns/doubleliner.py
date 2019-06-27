

from patterns.base import BasePattern
import numpy as np


class TwoLinePattern(BasePattern):
    
    f"""
    This class determines multiple candlesticks and if they match a peculiar pattern or not
    appends 1 or 0 depending on if condition is true or not
    
    Methods:
        
        iterate() : >>> This method loops through array of candle bars and tries to determine if
                        it falls as a pattern or not
                        
        confirm_bull_pattern(): >>> This method receives open,high,low,close values and tries to output 
        if the pattern indicates upward movement
        
        confirm_bear_pattern(): >>> This method receives open,high,low,close values and tries to output 
        if the pattern indicates downward movement
    
    
    """
    
    def confirm_bull_pattern(self,*args):
        pass
    
    def confirm_bear_pattern(self):
        pass
    
    def iterate(self):
        self.truth = []
        ad = self.df
        for x,y in enumerate(ad):
            if x-1 == -1:
                self.truth.append(0)
                continue
            
            last = ad[x-1]
            current = y
            
            last_op,last_high,last_low,last_close = last[0],last[1],last[2],last[3]
            current_op,current_high,current_low,current_close = current[0],current[1],current[2],current[3]
            
            lt = self.f(last_op,last_close)
            ct = self.f(current_op,current_close)
            
            if lt == 'Bearish'and ct == 'Bullish':
                integer = self.confirm_bull_pattern(
                    (last_op,last_high,last_low,last_close),
                    (current_op,current_high,current_low,current_close)
                )
                
                self.truth.append(integer)
            elif lt == 'Bullish' and ct == 'Bearish':
                integer = self.confirm_bear_pattern(
                    (last_op,last_high,last_low,last_close),
                    (current_op,current_high,current_low,current_close)
                )
                
                self.truth.append(integer)
                
            else:
                self.truth.append(0)
            
        return self.truth




class Tweezer(TwoLinePattern):
    
    
    def confirm_bull_pattern(self,*args):
        lt_open,lt_high,lt_low,lt_close = args[0]
        rt_open,rt_high,rt_low,rt_close = args[1]
        
        if lt_open != lt_close and rt_open != rt_close:
            
            if (lt_close == rt_open):
                if (0.7 <= abs(lt_open-lt_close)/abs(rt_open-rt_close) <= 1):
                    return 1
        return 0
    
    def confirm_bear_pattern(self,*args):
        lt_open,lt_high,lt_low,lt_close = args[0]
        rt_open,rt_high,rt_low,rt_close = args[1]
        
        if lt_open != lt_close and rt_open != rt_close:
            if (lt_close == rt_open):
                if (0.7 <= abs(lt_open-lt_close)/abs(rt_open-rt_close) <= 1):
                    return -1
        return 0
     
    
class Harami(TwoLinePattern):
    
    def confirm_bull_pattern(self,*args):
        lt_open,lt_high,lt_low,lt_close = args[0]
        rt_open,rt_high,rt_low,rt_close = args[1]
        
        lt_real = abs(lt_open-lt_close)
        rt_real = abs(rt_open-rt_close)
        
        if (lt_open > rt_high) and (lt_close < rt_low) and ((abs(lt_real)/abs(rt_real))>=2):
            return 1
        
        return 0
    
    def confirm_bear_pattern(self,*args):
        lt_open,lt_high,lt_low,lt_close = args[0]
        rt_open,rt_high,rt_low,rt_close = args[1]
        
        lt_real = abs(lt_open-lt_close)
        rt_real = abs(rt_open-rt_close)
        
        if (lt_close > rt_low) and (lt_open < rt_high) and ((abs(lt_real)/abs(rt_real))>=2):
            return -1
        
        return 0
    
class HaramiCross(TwoLinePattern):
    
    def confirm_bull_pattern(self,*args):
        lt_open,lt_high,lt_low,lt_close = args[0]
        rt_open,rt_high,rt_low,rt_close = args[1]
        
        if (lt_open > rt_high) and (lt_close < rt_low):
            return 1
        
        return 0
    
    def confirm_bear_pattern(self,*args):
        lt_open,lt_high,lt_low,lt_close = args[0]
        rt_open,rt_high,rt_low,rt_close = args[1]
        
        if (lt_close > rt_low) and (lt_open < rt_high):
            return -1
        
        return 0
    
    def iterate(self):
        self.truth = []
        ad = self.df
        for x,y in enumerate(ad):
            
            if x-1 == -1:
                self.truth.append(0)
                continue
            
            last = ad[x-1]
            current = y
            
            last_op,last_high,last_low,last_close = last[0],last[1],last[2],last[3]
            current_op,current_high,current_low,current_close = current[0],current[1],current[2],current[3]
            
            lt = self.f(last_op,last_close)
            ct = self.f(current_op,current_close)

            # This block below was the only thing I changed
            if lt == 'Bearish'and ct == 'Indecisive':
                integer = self.confirm_bull_pattern(
                    (last_op,last_high,last_low,last_close),
                    (current_op,current_high,current_low,current_close)
                )
                
                self.truth.append(integer)
            elif lt == 'Bullish' and ct == 'Indecisive':
                integer = self.confirm_bear_pattern(
                    (last_op,last_high,last_low,last_close),
                    (current_op,current_high,current_low,current_close)
                )
                self.truth.append(integer)
            else:
                self.truth.append(0)
            
        return self.truth

class Engulfing(TwoLinePattern):
    
    def confirm_bull_pattern(self,*args):
        lt_open,lt_high,lt_low,lt_close = args[0]
        rt_open,rt_high,rt_low,rt_close = args[1]
        
        if abs(lt_open - lt_close)/abs(rt_open - rt_close) > 0:
            return 1
        
        return 0
    
    def confirm_bear_pattern(self,*args):
        lt_open,lt_high,lt_low,lt_close = args[0]
        rt_open,rt_high,rt_low,rt_close = args[1]
        
        if abs(lt_open - lt_close)/abs(rt_open - rt_close) > 0:
            return -1
        
        return 0
    
class PiercingDarkCloud(TwoLinePattern):
    
    def confirm_bull_pattern(self,*args):
        lt_open,lt_high,lt_low,lt_close = args[0]
        rt_open,rt_high,rt_low,rt_close = args[1]
        
        if rt_open < lt_close and (rt_close > 0.5*(lt_open + lt_close)):
            return 1
        
        return 0
    
    def confirm_bear_pattern(self,*args):
        lt_open,lt_high,lt_low,lt_close = args[0]
        rt_open,rt_high,rt_low,rt_close = args[1]
        
        if rt_open > lt_close and (rt_close < 0.5*(lt_open + lt_close)):
            return -1
        
        return 0

