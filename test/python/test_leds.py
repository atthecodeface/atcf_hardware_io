#a Copyright
#  
#  This file 'bfm.py' copyright Gavin J Stark 2017-2020
#  
#  This program is free software; you can redistribute it and/or modify it under
#  the terms of the GNU General Public License as published by the Free Software
#  Foundation, version 2.0.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even implied warranty of MERCHANTABILITY
#  or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
#  for more details.

#a Imports
from regress.io.led import t_led_ws2812_data, t_led_ws2812_request
from cdl.sim     import ThExecFile, LogEventParser
from cdl.sim     import HardwareThDut
from cdl.sim     import TestCase
from typing import Optional

#a WS2812 classes
#c Ws2812Led
class Ws2812Led(object):
    def __init__(self, next_led=None):
        self.data_sr = 0 # right shift, green/red/blue 8 bits each
        self.green = 0
        self.red = 0
        self.blue = 0
        self.next_led = next_led
        pass
    def load(self):
        self.green = (self.data_sr>>16)&0xff
        self.red   = (self.data_sr>> 8)&0xff
        self.blue  = (self.data_sr>> 0)&0xff
        pass
    def shift(self, data_in:int) -> int:
        data_out = (self.data_sr>>23) & 1
        self.data_sr = (self.data_sr<<1) | (data_in & 1)
        if self.next_led:
            return self.next_led.shift(data_out)
        return data_out
    def __str__(self):
        return "(%02x,%02x,%02x)"%(self.red, self.green, self.blue)
    pass

#c Ws2812LedChain
class Ws2812LedChain(object):
    #f __init__
    def __init__(self, chain_length, cycles_for_period, loaded):
        self.leds = []
        next_led = None
        for i in range(chain_length):
            led = Ws2812Led(next_led=next_led)
            self.leds.append(led)
            next_led = led
            pass
        self.leds.reverse()
        self.data_in = 0
        self.last_falling_cycle = 0
        self.last_rising_cycle = 0
        self.load_pending = False
        self.cycles_for_period = cycles_for_period
        self.cycles_to_load    = 120*self.cycles_for_period
        self.loaded = loaded
        self.first_edge = True
        pass
    #f shift - shift data in to the chain
    def shift(self, data_in):
        return self.leds[0].shift(data_in)
    #f load - load the whole chain
    def load(self):
        for l in self.leds: l.load()
        self.loaded(self.leds)
        pass
    #f data_change - report a change in the data in pin
    def data_change(self, cycle, data=None):
        if data is None: data = self.data_in
        errors = []
        if (self.data_in==0) and ((cycle-self.last_falling_cycle)>self.cycles_to_load):
            if self.load_pending: self.load()
            self.load_pending = False
            pass
        if data==self.data_in: return errors
        self.data_in = data
        if data==1:
            cycles_low     = cycle-self.last_falling_cycle # Could be a lot if just loaded
            cycles_for_bit = cycle-self.last_rising_cycle
            if (cycles_for_bit > 5 * self.cycles_for_period) and not self.first_edge:
                if self.load_pending: errors.append("Have not loaded but should have done, gap was %f periods"%(cycles_for_bit / self.cycles_for_period))
                pass
            self.last_rising_cycle = cycle
            bit_accuracy = abs(cycles_for_bit/self.cycles_for_period-3)
            if (bit_accuracy>0.1) and (not self.first_edge) and self.load_pending:
                errors.append("Cycles for period should be 3, got %f"%(cycles_for_bit/self.cycles_for_period))
            pass
        else:
            cycles_high    = cycle-self.last_rising_cycle # Should be 1 or 2
            self.last_falling_cycle = cycle
            low_bit_accuracy  = abs(cycles_high/self.cycles_for_period-1)
            high_bit_accuracy = abs(cycles_high/self.cycles_for_period-2)
            if (low_bit_accuracy>0.1) and (high_bit_accuracy>0.1):
                errors.append("Cycles for clock high should be 1 or 2, got %f"%(cycles_high/self.cycles_for_period))
                pass
            if (low_bit_accuracy<=0.1):  self.shift(0)
            if (high_bit_accuracy<=0.1): self.shift(1)
            self.load_pending = True
            pass
        self.first_edge = False
        return errors
    pass
#a Test classes
#c LedChainTest_Base
class LedChainTest_Base(ThExecFile):
    th_name = "LED chain test harness"
    cfg_divider_400ns = 19
    chain_length=8
    #f exec_init
    def exec_init(self) -> None:
        self.toggle_log_event  = self.log_event("toggle", "n", "arg")
        super(LedChainTest_Base,self).exec_init()
        pass
    #f drive_led
    def drive_led(self, rgb, n=0):
        last = (n==self.chain_length-1)
        first = (n==0)
        self.led_data__valid.drive(1)
        self.led_data__last.drive(int(last))
        self.led_data__red.drive(rgb[0])
        self.led_data__green.drive(rgb[1])
        self.led_data__blue.drive(rgb[2])
        self.bfm_wait(1)
        self.led_request__ready.wait_for_value(1)
        self.compare_expected("'first' field of request",self.led_request__first.value(),first & 1)
        self.compare_expected("'led_number' field of request",self.led_request__led_number.value(),n)
        self.led_data__valid.drive(0)
        self.bfm_wait(1)
        self.compare_expected("valid taken away after request",self.led_request__ready.value(),0)
        self.expected_led_values.append(rgb)
        pass
    #f drive_leds
    def drive_leds(self, led_values):
        self.verbose.info("Drive %s"%(str(led_values)))
        for i in range(len(led_values)):
            self.drive_led(n=i, rgb=led_values[i])
            pass
        pass
    #f led_chain_loaded
    def led_chain_loaded(self, leds):
        leds_r = leds[:]
        leds_r.reverse()
        for l in leds_r:
            if self.expected_led_values==[]:
                self.failtest("Unexpected loading of LED value")
                continue
            (r,g,b) = self.expected_led_values.pop(0)
            self.compare_expected("red of loaded LED",l.red,r)
            self.compare_expected("green of loaded LED",l.green,g)
            self.compare_expected("blue of loaded LED",l.blue,b)
            pass
        pass
    #f handle_led_chain_log
    def handle_led_chain_log(self):
        while self.log_data.num_events()>0:
            l = self.log_data_parser.parse_log_event(self.log_data.event_pop())
            if l is None: continue
            e = self.led_chain.data_change(cycle=l.global_cycle, data=l.data)
            if len(e)>0:
                for s in e:
                    self.failtest(s)
                    pass
                pass
            pass
        self.led_chain.data_change(cycle=self.global_cycle())
    #f run__init
    def run__init(self) -> None:
        self.bfm_wait(10)
        self.divider_400ns.drive(self.cfg_divider_400ns)
        self.log_data         = self.log_recorder("dut") # Log events from led_ws2812_chain
        self.log_data_parser  = DataLogParser()
        self.bfm_wait(10)
        self.led_chain        = Ws2812LedChain(self.chain_length, (1+self.cfg_divider_400ns)*self.ticks_per_cycle(), self.led_chain_loaded)
        self.expected_led_values = []
        pass
    #f run
    def run(self) -> None:
        for l in self.led_values:
            self.drive_leds(l)
            self.handle_led_chain_log()
            pass
        self.bfm_wait(3*150*self.cfg_divider_400ns)
        self.handle_led_chain_log()
        self.passtest("Test completed")
        pass
    #f run__finalize
    def run__finalize(self) -> None:
        self.passtest("Test completed")
        pass
    pass

#c DataLogParser - log event parser for LED chain bit toggling
class DataLogParser(LogEventParser):
    def filter_module(self, module_name:str) -> bool : return module_name=="dut"
    def map_log_type(self, log_type:str) -> Optional[str] :
        if log_type in self.attr_map: return log_type
        return None
    attr_map = {"data change":{"data":1}}
    pass

#c LedChainTest_0
class LedChainTest_0(LedChainTest_Base):
    cfg_divider_400ns = 2
    chain_length=3
    led_values = [ [(0,0,0),(255,255,255),(128,64,32)],
                   [(1,2,3),(4,5,6),(7,8,9)],
                   ]

#c LedChainTest_1
class LedChainTest_1(LedChainTest_Base):
    cfg_divider_400ns = 30
    chain_length=2
    led_values = [ [(1,2,3),(4,5,6)],
                   [(11,12,13),(14,15,16)],
                   [(21,22,23),(24,25,26)],
                   [(31,32,33),(34,35,36)],
                   ]

#c LedChainTest_2
class LedChainTest_2(LedChainTest_Base):
    cfg_divider_400ns = 3
    chain_length=10
    led_values = [ [(1,2,3)]*10,
                   [(11,12,13)]*10,
                   [(21,22,23)]*10,
                   [(31,32,33)]*10,
                   ]

#a Hardware and test instantiation
#c LedChainHardware
class LedChainHardware(HardwareThDut):
    clock_desc = [("clk",(0,1,1))]
    reset_desc = {"name":"reset_n", "init_value":0, "wait":5}
    module_name = "led_ws2812_chain"
    dut_inputs  = {"divider_400ns":8,
                   "led_data":t_led_ws2812_data,
    }
    dut_outputs = {"led_request":t_led_ws2812_request,
                   "led_chain":1
    }
    loggers = { # "led_pin": {"modules":"dut", "verbose":0, "filename":"led.log"}
                }
    pass

#c TestLedChain
class TestLedChain(TestCase):
    hw = LedChainHardware
    _tests = {"0": (LedChainTest_0, 10*1000, {"verbosity":0}),
              "1": (LedChainTest_1, 200*1000, {"verbosity":0}),
              "2": (LedChainTest_2, 200*1000, {"verbosity":0}),
    }
