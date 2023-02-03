import cocotb
from cocotb.triggers import Timer, RisingEdge, ReadOnly, NextTimeStep, FallingEdge
from cocotb_bus.drivers import BusDriver
from cocotb_coverage.coverage import CoverCross, CoverPoint, coverage_db
from cocotb_bus.monitors import BusMonitor
import os
import random

def sb_fn(actual_value):
    print("Recived value=",actual_value)
@cocotb.test()
async def ifc_test(dut):
    dut.RST_N.value = 1
    await Timer(1, 'ns')
    dut.RST_N.value = 0
    await Timer(1, 'ns')
    await RisingEdge(dut.CLK)
    dut.RST_N.value = 1
    writedrv = InputDriver(dut, 'write', dut.CLK)
    readdrv=OutputDriver(dut, 'read', dut.CLK, sb_fn)
    
    for i in range(50):
        writelist=[]
        writeaddr = random.randint(0,5)
        writelist.append(writeaddr)
        writedata = random.randint(0, 1)
        writelist.append(writedata)    
        writedrv.append(writelist)
        
        readaddr = random.randint(0,5)        
        readdrv.append(readaddr)
        
        await FallingEdge(dut.CLK)
    
class InputDriver(BusDriver):
    _signals = ['address', 'data', 'en', 'rdy']

    def __init__(self, dut, name, clk):
        BusDriver.__init__(self, dut, name, clk)
        self.bus.en.value = 0
        self.clk = clk

     
    async def _driver_send(self, value, sync=True):
        for i in range(random.randint(0, 20)):
            await RisingEdge(self.clk)
        if self.bus.rdy.value != 1:
            await RisingEdge(self.bus.rdy)
        self.bus.en.value = 1
        self.bus.address.value = value[0]
        self.bus.data.value = value[1]        
        await ReadOnly()
        await RisingEdge(self.clk)
        self.bus.en.value = 0
        await NextTimeStep()
        
class IO_Monitor(BusMonitor):
    _signals = ['address', 'data', 'en', 'rdy']

    async def _monitor_recv(self):
        fallingedge = FallingEdge(self.clock)
        rdonly = ReadOnly()
        phases = {
            0: 'Idle',
            1: 'Rdy',
            3: 'Txn'
        }
        prev = 'Idle'
        while True:
            await fallingedge
            await rdonly
            txn = (self.bus.en.value << 1) | self.bus.rdy.value
            self._recv({'previous': prev, 'current': phases[txn]})
            prev = phases[txn]

class OutputDriver(BusDriver):
    _signals = ['address', 'data', 'en', 'rdy']
    def __init__(self, dut, name, clk,sb_callback):
        BusDriver.__init__(self, dut, name, clk)
        self.bus.en.value = 0
        self.clk = clk
        self.callback = sb_callback
        

    async def _driver_send(self, value, sync=True):

        for i in range(random.randint(0, 20)):
            await RisingEdge(self.clk)
        if self.bus.rdy.value != 1:
            await RisingEdge(self.bus.rdy)
        self.bus.en.value = 1
        self.bus.address.value = value     
        await ReadOnly()
        self.callback(self.bus.data.value)
        await RisingEdge(self.clk)
        await NextTimeStep()
        self.bus.en.value = 0


