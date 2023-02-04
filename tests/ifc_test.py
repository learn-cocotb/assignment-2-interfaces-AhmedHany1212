import cocotb
from cocotb.triggers import Timer, RisingEdge, ReadOnly, NextTimeStep, FallingEdge
from cocotb_bus.drivers import BusDriver
from cocotb_coverage.coverage import CoverCross, CoverPoint, coverage_db
from cocotb_bus.monitors import BusMonitor
import os
import random

global case
case=4
def sb_fn(actual_value):
    print("Recived value=",actual_value)
    



@CoverPoint("top.a",  # noqa F405
            xf=lambda a, b: a,
            bins=[0, 1],
            bins_labels=['True', 'False']
            )
@CoverPoint("top.b",  # noqa F405
            xf=lambda a, b: b,
            bins=[0, 1],
            bins_labels=['True', 'False']
            )
@CoverCross("top.cross.ab",
            items=["top.b",
                   "top.a"
                   ]
            )
def cover(a, b):
    cocotb.log.info(f"AB={a} {b}")
    pass


@cocotb.test()
async def ifc_test(dut):
    dut.RST_N.value = 1
    await Timer(1, 'ns')
    dut.RST_N.value = 0
    await Timer(1, 'ns')
    await RisingEdge(dut.CLK)
    dut.RST_N.value = 1
    writedrv = InputDriver(dut, 'write', dut.CLK)
    InputMonitor(dut, 'write', dut.CLK, callback=a_cover)
    readdrv=OutputDriver(dut, 'read', dut.CLK, sb_fn)
    
    if case==4:
        dut.write_en.value=1
        dut.read_en.value=1
        dut.write_address.value=4
        dut.write_data.value=1      
        await RisingEdge(dut.CLK)
        dut.write_address.value=4
        dut.write_data.value=0 
        await RisingEdge(dut.CLK)
        dut.write_address.value=5
        dut.write_data.value=0
        dut.read_address.value=3
        await RisingEdge(dut.CLK)
        await RisingEdge(dut.CLK)
        await RisingEdge(dut.CLK)
        assert dut.read_data.value==1,f"CASE 4 failed"

    if case==5:
        dut.write_en.value=1
        dut.read_en.value=1
        dut.write_address.value=4
        dut.write_data.value=1      
        await RisingEdge(dut.CLK)
        dut.write_address.value=5
        dut.write_data.value=0 
        await RisingEdge(dut.CLK)
        dut.read_address.value=3
        dut.RST_N.value=0
        assert dut.read_data.value==0,f"CASE 5 failed"
        
    for i in range(50):
        writelist=[]
        writeaddr = random.randint(0,5)
        writelist.append(writeaddr)
        writedata = random.randint(0, 1)
        writelist.append(writedata)    
        writedrv.append(writelist)
        
        readaddr = random.randint(0,5)        
        if case==1:
            readaddr = 0
        if case==2 | case==3:
            readaddr = 3

        readdrv.append(readaddr)
        
        await FallingEdge(dut.CLK)

    coverage_db.report_coverage(cocotb.log.info, bins=True)
    coverage_file = os.path.join(
        os.getenv('RESULT_PATH', "./"), 'coverage.xml')
    coverage_db.export_to_xml(filename=coverage_file)


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
        if case==1:
            self.bus.en.value = 0
        self.bus.address.value = value[0]
        if case==2:
            self.bus.address.value = 7
        if case==3:
            self.bus.address.value = 0
        self.bus.data.value = value[1]        
        await ReadOnly()
        await RisingEdge(self.clk)
        self.bus.en.value = 0
        await NextTimeStep()
        
class InputMonitor(BusMonitor):
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
        #if self.bus.address.value:
         #   assert self.bus.data.value== A|b
        if case==1:
            assert self.bus.data.value==1,f"incorrect case 1"
        if case==2 | case==3:
            assert self.bus.data.value==0,f"incorrect case 2"
        await RisingEdge(self.clk)
        await NextTimeStep()
        self.bus.en.value = 0



@CoverPoint(f"top.a.ifc_state",  # noqa F405
            xf=lambda x: x['current'],
            bins=['Idle', 'rdy', 'Txn'],
            )
@CoverPoint(f"top.a.previfc_state",  # noqa F405
            xf=lambda x: x['previous'],
            bins=['Idle', 'Rdy', 'Txn'],
            )
@CoverCross("top.cross.ifc.a",
            items=[
                "top.a.previfc_state", "top.a.ifc_state"
            ]
            )
def a_cover(state):
    cocotb.log.warning(f"state={state}")
    pass

