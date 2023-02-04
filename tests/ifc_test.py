import cocotb
from cocotb.triggers import Timer, RisingEdge, ReadOnly, NextTimeStep, FallingEdge
from cocotb_bus.drivers import BusDriver
from cocotb_coverage.coverage import CoverCross, CoverPoint, coverage_db
from cocotb_bus.monitors import BusMonitor
import os
import random

global case
case=2
def sb_fn(actual_value):
    print("Recived value=",actual_value)
    


@CoverPoint("top.write_cover",  # noqa F405
            xf=lambda write_cover, b: write_cover,
            bins=[0, 1],
            bins_labels=['True', 'False']
            )
@CoverPoint("top.b",  # noqa F405
            xf=lambda write_cover, b: b,
            bins=[0, 1],
            bins_labels=['True', 'False']
            )
@CoverCross("top.cross.ab",
            items=["top.b",
                   "top.write_cover"
                   ]
            )
def cover(write_cover, b):
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
    InputMonitor(dut, 'write', dut.CLK, callback=write_cover)
    readdrv=OutputDriver(dut, 'read', dut.CLK, sb_fn)
    
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
        if case==1:
            assert self.bus.data.value==1,f"incorrect case 1"
        if case==2 | case==3:
            assert self.bus.data.value==0,f"incorrect case 2"
        await RisingEdge(self.clk)
        await NextTimeStep()
        self.bus.en.value = 0

class InputMonitor(BusMonitor):
    _signals = ['rdy', 'en', 'data']

    async def _monitor_recv(self):
        fallingedge = FallingEdge(self.clock)
        rdonly = ReadOnly()
        prev_state = 'Idle'
        state = {
            0: 'Idle',
            1: 'RDY',
            2: 'Error',
            3: "Txn"
        }
        while True:
            await fallingedge
            await rdonly
            s = state[self.bus.rdy.value | (self.bus.en.value << 1)]
            self._recv({'current': s, 'previous': prev_state})
            prev_state = s


@CoverPoint(f"top.write.ifc_state",  # noqa F405
            xf=lambda x: x['current'],
            bins=['Idle', 'RDY', 'Txn'],
            )
@CoverPoint(f"top.write.previfc_state",  # noqa F405
            xf=lambda x: x['previous'],
            bins=['Idle', 'RDY', 'Txn'],
            )
@CoverCross("top.cross.ifc.write",
            items=[
                "top.write.previfc_state", "top.write.ifc_state"
            ]
            )
def a_cover(state):
    cocotb.log.warning(f"state={state}")
    pass
