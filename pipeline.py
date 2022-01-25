# To make a self launching package
# Creating a pipeline of instructions named pipeline.py
import pandas as pd
import sys

print(sys.agrv)
day = sys.argv[1]
#some fancy stuff with pandas

print(f"job done for day={day}")