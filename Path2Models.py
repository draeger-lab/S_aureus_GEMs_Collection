#!/usr/bin/env python
# coding: utf-8

import sys
path_to_file = sys.argv[1]
#print(path_to_file[107:])

from libsbml import *
import libsbml
reader = SBMLReader()
writer = SBMLWriter()
sbmldoc = reader.readSBML(path_to_file)

#####Convert Model to SBML 3.1
props = libsbml.ConversionProperties()
props.addOption("convert cobra", True, "Convert Cobra model")
result = sbmldoc.convert(props)
if result != libsbml.LIBSBML_OPERATION_SUCCESS:
    print("[Error] Conversion failed... (%d)" % result)
    
model = sbmldoc.getModel()


###### Fix Bugs -> Change chemical formulas to get valid File
species_list = model.getListOfSpecies()

for species in species_list:
    splugin = species.getPlugin('fbc')
    if splugin is not None:
        if '(' in splugin.getChemicalFormula() or 'n' in splugin.getChemicalFormula() or '.' in splugin.getChemicalFormula():
            formula = splugin.getChemicalFormula()
            formula = formula.replace('(', '')
            formula = formula.replace(')', '')
            formula = formula.replace('n', '')
            formula = formula.replace('.', '')
            splugin.setChemicalFormula(formula)
            
            
####Add annotations from notes field
metabol_db_dict = {'BIGG': 'bigg.metabolite:', 'BRENDA': 'brenda:', 'CHEBI': 'chebi:','INCHI': 'inchi:', 'KEGG': 'kegg.compound:', 'METACYC': 'metacyc.compound:','MXNREF': 'metanetx.chemical:', 'SEED':'seed.compound:', 'UPA': 'unipathway.compound:', 'HMDB': 'hmdb:', 'REACTOME': 'reactome:'}

reaction_db_dict = {'BIGG': 'bigg.reaction/', 'BRENDA': 'brenda/', 'KEGG': 'kegg.reaction/', 'METACYC': 'metacyc.reaction/', 'MXNREF': 'metanetx.reaction/', 'SEED':'seed.reaction/','UPA': 'unipathway.reaction/', 'HMDB': 'hmdb/', 'REACTOME': 'reactome/', 'RHEA': 'rhea/'}

def add_cv_term_from_notes_species(entry, db_id ):
    cv = CVTerm()
    cv.setQualifierType(BIOLOGICAL_QUALIFIER)
    cv.setBiologicalQualifierType(BQB_IS)
    cv.addResource('https://identifiers.org/'+ metabol_db_dict[db_id]+entry)
    species.addCVTerm(cv)
                
def add_cv_term_from_notes_reactions(entry, db_id ):
    cv = CVTerm()
    cv.setQualifierType(BIOLOGICAL_QUALIFIER)
    cv.setBiologicalQualifierType(BQB_IS)
    cv.addResource('https://identifiers.org/'+ reaction_db_dict[db_id]+entry)
    reaction.addCVTerm(cv)


## Add species annotations
for species in species_list:
    notes_list=[]
    elem_used=[]
    notes_string = species.getNotesString().split('\n')
    for elem in notes_string:
        for db in metabol_db_dict.keys():
            if '<p>'+db in elem:
                elem_used.append(elem)
                fill_in = elem.split(db+':')[1].strip()[:-4]
                if (',')  in fill_in and db != 'INCHI':
                    entries = fill_in.split(',')
                    for entry in entries:
                        add_cv_term_from_notes_species(entry.strip(), db)
                else:
                    add_cv_term_from_notes_species(fill_in, db)
    for elem in notes_string:
        if elem not in elem_used and elem not in notes_list:
            notes_list.append(elem)
    
    ####Adding new, shortened notes
    new_notes = ' '.join([str(elem)+'\n' for elem in notes_list])
    species.unsetNotes()
    species.setNotes(new_notes)
    #print(species.getNotesString())
                    
                    
                    
## Add reaction annotations
reaction_list = model.getListOfReactions()

for reaction in reaction_list:
    notes_list=[]
    elem_used=[]
    notes_string = reaction.getNotesString().split('\n')
    for elem in notes_string:
        for db in reaction_db_dict.keys():
            if '<p>'+db in elem:
                elem_used.append(elem)
                fill_in = elem.split(db+':')[1].strip()[:-4]
                if (',')  in fill_in:
                    entries = fill_in.split(',')
                    for entry in entries:
                        add_cv_term_from_notes_reactions(entry.strip(), db)
                else:
                    add_cv_term_from_notes_reactions(fill_in, db)
    for elem in notes_string:
        if elem not in elem_used and elem not in notes_list:
            notes_list.append(elem)
    
    ####Adding new, shortened notes
    new_notes = ' '.join([str(elem)+'\n' for elem in notes_list])
    reaction.unsetNotes()
    reaction.setNotes(new_notes)

print(path_to_file[107:], 'Number of Errors: ', sbmldoc.getNumErrors())
            
### Save files
writer.writeSBML(sbmldoc, path_to_file)
