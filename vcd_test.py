import sys
from vcd import VCDWriter
with open("test.vcd","w") as f:
    with VCDWriter(f, timescale='1 ns', date='today') as writer:
        counter_var = writer.register_var('a', 'counter', 'integer', size=32)
        counter_varb = writer.register_var('b', 'counter', 'integer', size=32)
        time = 0
        for value in range(10, 100, 2):
            writer.change(counter_var, time, value)
            writer.change(counter_varb, time, value*value)
            time += 1