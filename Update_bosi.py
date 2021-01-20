#!/usr/bin/env python
# coding: utf-8

import sys
path_to_models = sys.argv[1]
print(path_to_models[100:])


import cobra
from libsbml import *

#Read in model with libsbml
reader = SBMLReader()
document = reader.readSBML(path_to_models)
#print(document.getNumErrors())
model = document.getModel()


#Species
species_list = model.getListOfSpecies()
ending_list = ['_e', '_p', '_c']


added_compartment_tag = {}

for species in species_list:
    if 'DASH' in species.getId():
        species.setId(species.getId().replace('DASH', ''))
    if species.getId()[-2:] not in ending_list:
        if species.getCompartment() == 'c':
            added_compartment_tag[species.getId()] = '_c'
            species.setId(species.getId() + '_c')
            
        elif species.getCompartment() == 'e':
            added_compartment_tag[species.getId()] = '_e'
            species.setId(species.getId() + '_e')
            
        else:
            print(species.getId())
            
    species.setMetaId(species.getId())
#print(len(added_compartment_tag))



#Reactions
reaction_list = model.getListOfReactions()
for reaction in reaction_list:
    
    if 'DASH' in reaction.getId():
        reaction.setId(reaction.getId().replace('DASH', ''))
    if 'LPAREN_'in reaction.getId():
        reaction.setId(reaction.getId().replace('LPAREN_', ''))
    if 'RPAREN' in reaction.getId():
        reaction.setId(reaction.getId().replace('_RPAREN_', ''))
    
    reaction.setMetaId(reaction.getId())
    
    
for react in reaction_list:
    products = react.getListOfProducts()
    reactants = react.getListOfReactants()
        
    for elem in reactants:
        if 'DASH' in elem.getSpecies():
            elem.setSpecies(elem.getSpecies().replace('DASH', ''))
        if elem.getSpecies() in added_compartment_tag.keys():
            elem.setSpecies(elem.getSpecies() + added_compartment_tag[elem.getSpecies()])

    for elem in products:
        if 'DASH' in elem.getSpecies():
            elem.setSpecies(elem.getSpecies().replace('DASH', ''))
        if elem.getSpecies() in added_compartment_tag.keys():
            elem.setSpecies(elem.getSpecies() + added_compartment_tag[elem.getSpecies()])


# ## SBO Terms
transport = 0
for react in reaction_list:
        products = react.getListOfProducts()
        reactants = react.getListOfReactants()
        
        #Have both reactants and products in one list
        reactant_list = []
        products_list = []
        for elem in reactants:
            reactant_list.append(elem.getSpecies())
        for elem in products:
            products_list.append(elem.getSpecies())
        
        combined = reactant_list + products_list
        compartments = [elem[-1] for elem in combined]
        compartments = list(set(compartments))
        
        
        if len(combined) == 1:
            continue
        elif len(compartments) == 1:
            continue
        else:
            #Check for specific transport reactions
            if any("_e" in s for s in combined):
                #Passive transport
                if len(combined) == 2: 
                    react.setSBOTerm('SBO:0000658')
                    transport += 1
                #Active Transport
                elif 'M_atp_c' in combined:
                    react.setSBOTerm('SBO:0000657')
                    transport += 1
                #Co-transport:symporter
                elif all(['_e' in item for item in reactant_list]): 
                    react.setSBOTerm('SBO:0000659')
                    transport += 1
                #Co-transport:antiporter
                else:
                    react.setSBOTerm('SBO:0000660')
                    transport += 1
                    #print(react.getId(), combined)
            else:
                react.setSBOTerm('SBO:0000655')
#print(transport)


### Metabolic reactions
sbo_term_list = [658, 657, 659, 660, 627, 628, 630, 629, 632]


metabolic_react = 0
for react in reaction_list: 
    
    if react.isSetSBOTerm() == False:
        react.setSBOTerm('SBO:0000176')
        metabolic_react += 1
#print(metabolic_react)


###Genes
mplugin = model.getPlugin("fbc")
gene_list = mplugin.getListOfGeneProducts()
for gene in gene_list:
    gene.setMetaId(gene.getId())
    if gene.isSetSBOTerm() == False:
        gene.setSBOTerm('SBO:0000243')
        #print(gene.getSBOTerm())
    #else:
        #print(gene.getId())


###Species
for species in species_list:
    if species.isSetSBOTerm() == False:
        species.setSBOTerm('SBO:0000247')


newdocument = model.getSBMLDocument()
writeSBMLToFile(newdocument, path_to_models) # 1 means success, 0 means failure

