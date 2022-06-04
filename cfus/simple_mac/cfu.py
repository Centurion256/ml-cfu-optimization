#!/bin/env python

from amaranth import *
from amaranth_cfu import InstructionBase, InstructionTestBase, simple_cfu, CfuTestBase, all_words, pack_vals
import unittest

# See proj_example for further example instructions

#This implementation is similar to SIMD MAC. All credit for that implementation goes to CFU playground team developers
class SimpleMac(InstructionBase):
    def __init__(self) -> None:
        super().__init__()

        self.bias = C(128, signed(9)) #Hardcoded, add another if in sychronous code to change that

    def elab(self, m: Module) -> None:

        self.prod = Signal(signed(32))
        m.d.comb += self.prod.eq(
            (self.in0.as_signed() + self.bias) * self.in1.as_signed())

        m.d.sync += self.done.eq(0)
        # self.start signal high for one cycle when instruction started.
        with m.If(self.start):
            with m.If(self.funct7):
                m.d.sync += self.output.eq(0)
            with m.Else():
                # Accumulate step:
                m.d.sync += self.output.eq(self.output + self.prod)

            m.d.sync += self.done.eq(1)

def make_cfu():
    return simple_cfu({
        # Add instructions here...
        0: SimpleMac(),
    })
