#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
GRIFFEYE-CRAWLER DEFAULT
------------------------
Asks the user for the csv file and calls gc-cli.py with the default values so that the user doesn't have to use the command line for default cases

(c) 2023, Luzerner Polizei
Author:  Michael Wicki
"""
version = "1.0"

import os

print("===== GRIFFEYE-CRAWLER {} =====".format(version))
# ask for informations
input_filename = input("Pfad/Name des Input-CSV > ")
print()
# start griffeye crawler
os.system(f"python gc-cli.py {input_filename}")

print()
input()
