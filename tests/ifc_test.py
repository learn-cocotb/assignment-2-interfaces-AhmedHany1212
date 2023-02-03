import cocotb
from cocotb.triggers import Timer, RisingEdge, ReadOnly, NextTimeStep, FallingEdge
from cocotb_bus.drivers import BusDriver
from cocotb_coverage.coverage import CoverCross, CoverPoint, coverage_db
from cocotb_bus.monitors import BusMonitor
import os
import random

@cocotb.test()
async def ifc_test(dut):
    dut.RST_N.value = 1
    await Timer(1, 'ns')
    dut.RST_N.value = 0
    await Timer(1, 'ns')
    await RisingEdge(dut.CLK)
    dut.RST_N.value = 1
    writedrv = InputDriver(dut, 'write', dut.CLK)
    OutputDriver(dut, 'read', dut.CLK, sb_fn)
    
    for i in range(20):
    writelist=[]
    writeaddr = random.randint(0,5)
    writelist.append(writeaddr)
    writedata = random.randint(0, 1)
    writelist.append(writedata)    
    writedrv.append(writelist)
    
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
        
 class OutputDriver(BusDriver):
    _signals = ['address', 'data', 'en', 'rdy']

    def __init__(self, dut, name, clk, sb_callback):
        BusDriver.__init__(self, dut, name, clk)
        self.bus.en.value = 0
        self.clk = clk
        self.callback = sb_callback
        self.append(0)

    async def _driver_send(self, value, sync=True):
        while True:
            for i in range(random.randint(0, 20)):
                await RisingEdge(self.clk)
            if self.bus.rdy.value != 1:
                await RisingEdge(self.bus.rdy)
            self.bus.en.value = 1
            await ReadOnly()
            self.callback(self.bus.data.value)
            await RisingEdge(self.clk)
            await NextTimeStep()
            self.bus.en.value = 0
               



