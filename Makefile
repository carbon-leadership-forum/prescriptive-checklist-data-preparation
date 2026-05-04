.PHONY: requirements create_environment test_environment virtual organize test clean combine process_data

#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_DIR := $(realpath $(lastword $(MAKEFILE_LIST)))
PROFILE = default
PROJECT_NAME = scripts
PYTHON_INTERPRETER = python3
VENV_PYTHON = venv-data-prep\Scripts\python

#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Install Python Dependencies
requirements: test_environment
	$(VENV_PYTHON) -m pip install -r requirements.txt

## Set up python interpreter environment
create_environment: virtual
	$(PYTHON_INTERPRETER) -m virtualenv venv

## Test python environment is setup correctly
test_environment:
	$(VENV_PYTHON) test_environment.py

virtual:
	pip install virtualenv

#run organizing script
organize_metadata:
	$(VENV_PYTHON) -m scripts.metadata.1_organize

#run testing script 
test_metadata:
	$(VENV_PYTHON) -m scripts.metadata.2_test

#run cleaning script
clean_metadata:
	$(VENV_PYTHON) -m scripts.metadata.3_clean

#run merging script
merge_metadata:
	$(VENV_PYTHON) -m scripts.metadata.4_merge

#run combining script
combine_metadata: 
	$(VENV_PYTHON) -m scripts.metadata.5_combine

finalize_metadata:
	$(VENV_PYTHON) -m scripts.metadata.6_finalize

## clean lca_results
clean_lca_results: 
	$(VENV_PYTHON) -m scripts.lca_results.1_clean

## add stored carbon to lca_results
stored_carbon_lca_results:
	$(VENV_PYTHON) -m scripts.lca_results.2_add_stored_carbon

## map elements for lca_results
map_elements_lca_results:
	$(VENV_PYTHON) -m scripts.lca_results.3_map_elements

## map materials for lca_results
map_materials_lca_results:
	$(VENV_PYTHON) -m scripts.lca_results.4_map_materials

## map elements after material mapping for lca_results
map_elements_refined_lca_results:
	$(VENV_PYTHON) -m scripts.lca_results.5_map_elements_refined

## combine lca_results
combine_lca_results: 
	$(VENV_PYTHON) -m scripts.lca_results.6_combine

## harmonize lca_results
harmonize_lca_results:
	$(VENV_PYTHON) -m scripts.lca_results.7_harmonize

## baseline lca_results
baseline_lca_results:
	$(VENV_PYTHON) -m scripts.lca_results.8_baseline

## harmonize lca_results
complete_lca_results:
	$(VENV_PYTHON) -m scripts.lca_results.9_complete

## Create internal_data excel
internal_data_record:
	$(VENV_PYTHON) -m scripts.data_record.1_internal_data

## Create buildings_metadata excel
buildings_metadata_data_record:
	$(VENV_PYTHON) -m scripts.data_record.2_buildings_metadata

## Create lca_full_results excel
lca_full_results_data_record:
	$(VENV_PYTHON) -m scripts.data_record.3_lca_full_results

## Create all public dataset files
data_record_creation:
	$(VENV_PYTHON) -m scripts.data_record.1_internal_data
	$(VENV_PYTHON) -m scripts.data_record.2_buildings_metadata
	$(VENV_PYTHON) -m scripts.data_record.3_lca_full_results

## run all harmonization of tally and one click entries
lca_results_harmonization:
	$(VENV_PYTHON) -m scripts.lca_results.1_clean
	$(VENV_PYTHON) -m scripts.lca_results.1b_add_ex_bio
	$(VENV_PYTHON) -m scripts.lca_results.2_add_stored_carbon
	$(VENV_PYTHON) -m scripts.lca_results.3_map_elements
	$(VENV_PYTHON) -m scripts.lca_results.4_map_materials
	$(VENV_PYTHON) -m scripts.lca_results.5_map_elements_refined
	$(VENV_PYTHON) -m scripts.lca_results.6_combine
	$(VENV_PYTHON) -m scripts.lca_results.7_harmonize
	$(VENV_PYTHON) -m scripts.lca_results.8_baseline
	$(VENV_PYTHON) -m scripts.lca_results.9_complete

#run all data processing of data entry templates
metadata_preparation: 
	$(VENV_PYTHON) -m scripts.metadata.1_organize
	$(VENV_PYTHON) -m scripts.metadata.2_test
	$(VENV_PYTHON) -m scripts.metadata.3_clean
	$(VENV_PYTHON) -m scripts.metadata.4_merge
	$(VENV_PYTHON) -m scripts.metadata.5_combine
	$(VENV_PYTHON) -m scripts.metadata.6_finalize

# runs all the commands
all_data_commands:
	$(VENV_PYTHON) -m scripts.metadata.1_organize
	$(VENV_PYTHON) -m scripts.metadata.2_test
	$(VENV_PYTHON) -m scripts.metadata.3_clean
	$(VENV_PYTHON) -m scripts.metadata.4_merge
	$(VENV_PYTHON) -m scripts.metadata.5_combine
	$(VENV_PYTHON) -m scripts.metadata.6_finalize
	$(VENV_PYTHON) -m scripts.lca_results.1_clean
	$(VENV_PYTHON) -m scripts.lca_results.1b_add_ex_bio
	$(VENV_PYTHON) -m scripts.lca_results.2_add_stored_carbon
	$(VENV_PYTHON) -m scripts.lca_results.3_map_elements
	$(VENV_PYTHON) -m scripts.lca_results.4_map_materials
	$(VENV_PYTHON) -m scripts.lca_results.5_map_elements_refined
	$(VENV_PYTHON) -m scripts.lca_results.6_combine
	$(VENV_PYTHON) -m scripts.lca_results.7_harmonize
	$(VENV_PYTHON) -m scripts.lca_results.8_baseline
	$(VENV_PYTHON) -m scripts.lca_results.9_complete
	$(VENV_PYTHON) -m scripts.data_record.1_internal_data
	$(VENV_PYTHON) -m scripts.data_record.2_buildings_metadata
	$(VENV_PYTHON) -m scripts.data_record.3_lca_full_results
