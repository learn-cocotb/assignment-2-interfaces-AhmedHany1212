import FIFOF::*;

interface Ifc_dut;
	(*ready="write_rdy",enable="write_en"*)
	method Action write (Bit#(3) address,Bool data);
	(*ready="read_rdy",enable="read_en",result="read_data"*)
	method ActionValue#(Bool) read(Bit#(3) address);
endinterface

(*synthesize*)
module dut(Ifc_dut);
	FIFOF#(Bool) a_ff <- mkFIFOF();
	FIFOF#(Bool) b_ff <- mkFIFOF1();
	FIFOF#(Bool) y_ff <- mkFIFOF();
	Wire#(Bool) a_data <-mkWire();
	Wire#(Bool) b_data <-mkWire();
	rule orit;
		Bool x=a_ff.first();
		Bool z=b_ff.first();
		y_ff.enq(x||z);
		a_ff.deq();
		b_ff.deq();
	endrule
	rule enq_aff;
		a_ff.enq(a_data);
	endrule
	rule enq_bff;
		b_ff.enq(b_data);
	endrule
	PulseWire pwyff_deq <- mkPulseWire();
	Wire#(Bool) yff_first <- mkDWire(False);
	rule yff_deq(pwyff_deq);
		y_ff.deq();
	endrule
	rule ryff_first;
		yff_first<=y_ff.first();
	endrule

	method Action write (Bit#(3) address,Bool data);
		if (address ==4)
			a_data <=data;
		if (address ==5)
			b_data <= data;
	endmethod
	method ActionValue#(Bool) read(Bit#(3) address);
		let rv=case (address) matches
			0: return a_ff.notFull();
			1: return b_ff.notFull();
			2: return y_ff.notEmpty();
			3: return yff_first;
			default:return False;
		endcase;
		if (address==3) begin
 		       	pwyff_deq.send();
		end
		return rv;
	endmethod
endmodule
