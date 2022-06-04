#!/bin/env python

from amaranth import *
from amaranth_cfu import InstructionBase, InstructionTestBase, simple_cfu, CfuTestBase, all_words, pack_vals
import unittest

# See proj_example for further example instructions


class SimdMac(InstructionBase):
    def __init__(self, input_offset=128) -> None:
        super().__init__()

        self.input_offset = C(input_offset, signed(9))

    # `elab` method implements the logic of the instruction.
    def elab(self, m: Module) -> None:
        words = lambda s: all_words(s, 8)

        # SIMD multiply step:
        self.prods = [Signal(signed(16)) for _ in range(4)]
        for prod, w0, w1 in zip(self.prods, words(self.in0), words(self.in1)):
            m.d.comb += prod.eq(
                (w0.as_signed() + self.input_offset) * w1.as_signed())

        m.d.sync += self.done.eq(0)
        # self.start signal high for one cycle when instruction started.
        with m.If(self.start):
            with m.If(self.funct7):
                m.d.sync += self.output.eq(0)
            with m.Else():
                # Accumulate step:
                m.d.sync += self.output.eq(self.output + sum(self.prods))
            # self.done signal indicates instruction is completed.
            m.d.sync += self.done.eq(1)

class SimdAdd(InstructionBase):
    
    def elab(self, m: Module):
        words = lambda s: all_words(s, 8)
        
        self.results = [Signal(signed(16)) for _ in range(4)] #Result of 8-bit + 8-bit is  8-bit + carry = 9-bit, but use 16-bit for compatibility
        for res, operand0, operand1 in zip(self.results, words(self.in0), words(self.in1)):
            m.d.comb += res.eq(
                operand0.as_signed() + operand1.as_signed()
            )            
    
        m.d.sync += self.done.eq(0)
        with m.If(self.start):
            
            m.d.sync += [
                self.output[0:8].eq(self.results[0]),
                self.output[8:16].eq(self.results[1]),
                self.output[16:24].eq(self.results[2]),
                self.output[24:32].eq(self.results[3]),
                ]
            
            m.d.sync += self.done.eq(1)
            

class SimdMult(InstructionBase):
    def elab(self, m: Module):
        words = lambda s: all_words(s, 8)
        
        self.results = [Signal(signed(16)) for _ in range(4)] #Result of 8-bit * 8-bit is  16-bit
        for res, operand0, operand1 in zip(self.results, words(self.in0), words(self.in1)):
            m.d.comb += res.eq(
                operand0.as_signed() * operand1.as_signed()
            )

        m.d.sync += self.done.eq(0)
        with m.If(self.start):
            #The result of four multiplications is 16-bit wide each (64-bit in total), and we can't use any register pairs as in x86
            #We output either the lower or upper 32-bit parts of 64-bit result conditionally, based on the value of funct7
            #Therefore, the instruction must be executed twice, turning it into a de-facto 16-bit SIMD instead of 32-bit.
            with m.If(self.funct7): #Return the upper two results packed into 32-bit register. ret = (in0[24:31] * in1[24:31]) << 8 | (in0[16:23] * in1[16:23]) 
                m.d.sync += [
                    self.output[0:16].eq(self.results[2]),
                    self.output[16:32].eq(self.results[3])
                    ]
            
            with m.Else(): #Return the lower two results packed into 32-bit register. ret = (in0[8:15] * in1[8:15]) << 8 | (in0[0:7] * in1[0:7]) 
                m.d.sync += [
                    self.output[0:16].eq(self.results[0]),
                    self.output[16:32].eq(self.results[1])
                    ]
            m.d.sync += self.done.eq(1)
            
            
class SimdAccum16(InstructionBase):
    
    def elab(self, m: Module):
        dwords = lambda x: all_words(x, 16)
        
        
        self.result = [Signal(signed(16)) for _ in range(2)] #
        for res, operand0, operand1 in zip(self.result, dwords(self.in0), dwords(self.in1)):
            m.d.comb += res.eq(
                operand0.as_signed() + operand1.as_signed()
            )

        m.d.sync += self.done.eq(0)
        with m.If(self.start):
            
            m.d.sync += self.output.eq(sum(self.result))
            m.d.sync += self.done.eq(1)
    
def make_cfu():
    return simple_cfu({
        # Add instructions here...
        1: SimdMult(),
        0: SimdAdd(),
        2: SimdAccum16(),
    })

# 16-bit SIMD case:
# Add: 8-bit + 8-bit = 9 bit; 9 bit -> promote to 16-bit. Two 9-bit = 32-bit
