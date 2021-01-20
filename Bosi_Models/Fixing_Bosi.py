#!/usr/bin/env python
# coding: utf-8

import sys
path_to_file = sys.argv[1]
print(path_to_file[102:])

##Fixing "-" in IDs
import re
f = open(path_to_file)
s = f.read()

s_new = re.sub(r'([A-Za-z])(-)([A-Za-z])', r'\1_\3', s)


###Fixing empty ListOfCompartments
replace = """<listOfCompartments>
          <compartment id="c" name="cytosol" constant="true"/>
          <compartment id="e" name="extracellular space" constant="true"/>
          <compartment id="p" name="periplasm" constant="true"/>
    </listOfCompartments>""" 

s_new = re.sub(r'(<listOfCompartments/>)', replace, s_new)

##Fix charges!
s_new = re.sub(r'(fbc:charge="-?[0-9]+)(\.[^"]*)(")', r'\1\3', s_new)

f_new = open(path_to_file, 'w')
f_new.write(s_new)
f_new.close()

from libsbml import *
reader = SBMLReader()
document = reader.readSBML(path_to_file)
#print(document.getNumErrors())
model = document.getModel()

###Fixing Model ID that starts with a number
ident = model.getId()
#print(ident)
if str.isdigit(ident[0]):
    model.setId('SA_' + ident)
#print(model.getId())

species_list = model.getListOfSpecies()

for species in species_list:
    if species.getCompartment() == '':
        species.setCompartment(species.getId()[-1:])
        #print(species.getId(), species.getCompartment())
    splugin = species.getPlugin('fbc')
    if splugin is not None:
        if '(' in splugin.getChemicalFormula():
            formula = splugin.getChemicalFormula()
            formula = formula.replace('(', '')
            formula = formula.replace(')', '')
            splugin.setChemicalFormula(formula)
            #print(splugin.getChemicalFormula())
            
writeSBMLToFile(document, path_to_file)
