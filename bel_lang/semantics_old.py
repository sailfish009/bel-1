#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This file defines the semantic class used in our parser for BEL statements.
"""

import collections
import math
import os
import requests

import yaml

from bel_lang.exceptions import *


###################
# SEMANTICS CLASS #
###################


class BELSemantics(object):
    def __init__(self, version='2_0_0'):

        # load the dict from yaml file here

        current_directory = os.path.dirname(__file__)
        path_to_yaml_file = '{}/versions/bel_v{}.yaml'.format(current_directory, version)

        yaml_file = open(path_to_yaml_file, 'r').read()
        yaml_dict = yaml.load(yaml_file)

        self.abbre_to_name = self.abbreviations_to_names(yaml_dict)
        self.name_to_abbre = self.names_to_abbreviations(yaml_dict)
        self.function_signatures = self.get_function_signatures(yaml_dict)
        self.relations = self.get_relations(yaml_dict)

        self.term_store_endpoint = 'https://api.bel.bio/v1/terms/{}'

    #######################
    # SEMANTIC RULE NAMES #
    #######################

    def function(self, ast):

        fn_given = ast.get('function', None)
        args_given = ast.get('function_args', None)

        self.check_valid_signature(fn_given, args_given)

        # print('Function found: {}().'.format(fn_given))
        # print('arguments: ')
        # pprint(args_given, indent=2)
        # print('\n')

        # for arg in args_given:
        #     if arg:  # if the given argument list is not empty
        #         if 'm_function' in arg:
        #             m_fn = arg['m_function']
        #             # print('modifier function: {}'.format(m_fn))
        #             self.check_function_modifier(fn, m_fn)
        #
        #     else:  # if the list is empty, move to the next arg
        #         continue

        return ast

    def modifier_function(self, ast):
        # mfn = ast['m_function']
        # print('Modifier function found: {}().'.format(mfn))
        return ast

    def relation(self, ast):
        # r_given = ast.get('relation', None)s
        self.check_valid_relation(ast)

        return ast

    def namespace_arg(self, ast):
        self.check_signature_args(ast)

        return ast

    def string_arg(self, ast):
        # str_arg = ast['str_arg']
        # print('String argument found: {}.'.format(str_arg))
        return ast

    ##################################
    # SEMANTIC CHECKING STAGE 1 OF 3 #
    ##################################

    def get_function_signatures(self, yaml_dict):
        """
        This is stage 1 of semantic checking. It has one argument:

        1. yaml_dict: This is the dictionary parsed from the given YAML file defined by the user.

        We are focused on the function_signature key found inside yaml_dict, as that gives us the information we need to
        build our dictionary-based signature definitions. For each signature, we store both a required_args and a
        optional_args OrderedDict(). This serves two purpose: we need to keep track of each arg type's optional and
        multiple booleans in a key/value pair, but also need to keep the dict ordered for the required args.
        """

        signature_dict = {}

        for func in yaml_dict.get('function_signatures', []):  # for each function in the yaml function signatures...
            f_name = func.get('name', 'unknown')  # get the name of the function in yaml
            f_sigs = func.get('signatures', [])  # get the signatures of the function
            signature_dict[f_name] = f_sigs  # set function name as key, and yaml's f_sigs as the value for this key

            for valid_sig in f_sigs:  # for each signature from signatures...
                args = valid_sig.get('args', None)  # get the arg types of this signature
                required_args = collections.OrderedDict()  # required arg types list (must be ordered)
                optional_args = collections.OrderedDict()  # optional arg types list (does not need to be ordered)

                for par in args:  # for each type in arg types
                    par_type = par.get('type', 'Unknown')  # get the type name
                    optional = par.get('optional', False)  # get the optional boolean
                    multiple = par.get('multiple', False)  # get the multiple boolean

                    # arg is REQUIRED AND SINGULAR
                    # set the value as the number of times this type can appear
                    if not optional and not multiple:
                        required_args[par_type] = required_args.get(par_type, 0) + 1

                    # arg is REQUIRED AND MULTIPLE
                    # set the value to infinity as we'll always have 1 or more of this type
                    elif not optional and multiple:
                        required_args[par_type] = math.inf

                    # arg is OPTIONAL AND SINGULAR
                    # set the value as the number of times this type can appear
                    elif optional and not multiple:
                        optional_args[par_type] = optional_args.get(par_type, 0) + 1

                    # arg is OPTIONAL AND MULTIPLE
                    # set the value to infinity as we'll always have 0 or more of this type
                    else:
                        optional_args[par_type] = math.inf

                # add these two OrderedDicts as key/values within valid_sig so we can refer to them later on
                valid_sig['required'] = required_args
                valid_sig['optional'] = optional_args

            # clone the value of f_name into its respective abbreviation key
            # e.g. signature_dict[activity] == signature_dict[act]; signature_dict[pathology] == signature_dict[path]
            signature_dict[self.name_to_abbre[f_name]] = f_sigs

        return signature_dict

    ##################################
    # SEMANTIC CHECKING STAGE 2 OF 3 #
    ##################################

    def check_valid_signature(self, fn_given, args_given):
        """
        This is stage 2 of semantic checking. It has three arguments:

        1. fn_given: This is the given function from the BEL statement.

        For example, consider the following BEL statement:

        tloc(p(HGNC:SGK1), fromLoc(MESHCS:Cytoplasm), toLoc(MESHCS:"Cell Nucleus")) association bp(GOBP:"cell cycle")

        The functions present above are p(), tloc(), and bp(), and thus this BEL statement will require three calls to
        check_valid_signature(), once for each of the present BEL functions.

        2. args_given: These are the arguments given with each respective fn_given from above in the form of an AST.
        3. function_signatures: The signatures defined from stage 1 above.

        The purpose of check_valid_signature is to check that the function given from the BEL statement matches one of
        the function signatures defined from stage 1. Specifically, it first checks if the arg types (Entity,
        Modifier, Function, String, etc.), their optionality, and their multiplicity match with the args_given. Then,
        it checks to see if each given arg is valid for their respective defined arg type. In the example
        above, tloc()'s arguments match the signature definition [Function, Modifier, Modifier], but we also have to
        check that p() is a valid value for tloc()'s Function arg, fromLoc() is a valid value for tloc()'s
        Modifier arg, etc.
        """

        # these are specific functions to ignore in case their signatures are wrong or need reworking
        # if fn_given in ['activity']:
        #     return

        func_sig_detected = self.detect_function_signature(fn_given, args_given)

        if func_sig_detected is not None:
            # print('\t\033[91mIdentified signature:\033[0m {}'.format(func_sig_detected))
            return True
        else:
            # print('\t\033[91mNo function signature detected.\033[0m')
            return False

    def detect_function_signature(self, fn_given, args_given):

        msg_or_sig = None

        # check if at least one arg is given
        if not args_given:

            raise ArgeterMissing(fn_given)

        valid_sigs = self.function_signatures.get(fn_given, [])
        given_arg_list = self.args_to_given_sig_list(args_given)

        for v_sig in valid_sigs:

            valid, msg_or_sig = self.check_valid_sig_given_args(v_sig, given_arg_list)
            if valid:  # if valid is true, return message back
                return msg_or_sig

        # this exception will be raised if valid is False
        raise InvalidArgeter(msg_or_sig)

    def check_valid_sig_given_args(self, v_sig, given_arg_list):

        required = v_sig.get('required', [])
        optional = v_sig.get('optional', [])

        idx = 0  # keeps track of our given arg index we're currently checking

        required_count = len(required)  # number of required arg TYPES (not total, as types can have multiples)
        given_arg_count = len(given_arg_list)  # number of args given

        if given_arg_count < required_count:
            exception_msg = '{} arg type(s) are required. {} given.'.format(required_count, given_arg_count)
            return False, exception_msg

        for required_arg_type in required:
            if required[required_arg_type] == 1:  # singular arg
                if required_arg_type == given_arg_list[idx]:  # if the given arg at the index == required type
                    idx += 1
                    continue  # continue to the next required arg type
                else:  # given arg at index is not a required type. set matched to False and break out of loop
                    exception_msg = 'A required \"{}\" type was expected, but \"{}\" type was given instead.'.format(
                        required_arg_type, given_arg_list[idx])
                    return False, exception_msg
            else:  # this arg type can have multiples - loop until end or diff type
                while idx < given_arg_count:
                    if required_arg_type == given_arg_list[idx]:
                        idx += 1
                    else:  # break the loop because we encountered a arg that is not our multiple arg type
                        break

        if idx < given_arg_count:  # there are still optional args given that have not been accounted for
            remaining_args = given_arg_list[idx:]
            for remain in remaining_args:
                if remain in optional:

                    # check occurences of this optional arg is less than the max allowed
                    if remaining_args.count(remain) <= optional[remain]:
                        continue
                    else:
                        exception_msg = 'Too many optional args of type \"{}\" in statement. ' \
                                        'Does not match any function signatures.'.format(remain)
                        return False, exception_msg

                else:
                    exception_msg = '\"{}\" is not a valid optional arg type for this function.'.format(remain)
                    return False, exception_msg

        return True, v_sig

    ##################################
    # SEMANTIC CHECKING STAGE 3 OF 3 #
    ##################################

    def check_signature_args(self, ast):
        # Stage 3 of 3: check each of the args in the function call to see if they are valid
        ns_arg = ast.get('ns_arg', {})

        ns = ns_arg.get('nspace', '')
        nsv = ns_arg.get('ns_value', '')

        term = '{}:{}'.format(ns, nsv)
        r_url = self.term_store_endpoint.format(term)

        r = requests.get(r_url)
        if r.status_code == 404:
            print('WARNING: {} is not a valid namespace in your TermStore API!'.format(term))

        #  can't check this until TermStore is ready

        return

    ##############################
    # VALID RELATIONSHIP CHECKER #
    ##############################

    def check_valid_relation(self, given):
        # checks against all relations in YAML to make sure the given one is valid

        if given not in self.relations:
            raise InvalidRelationship(given)

        return

    ###############################
    # SEMANTIC HELPER DEFINITIONS #
    ###############################

    def abbreviations_to_names(self, yaml_dict):
        # uses YAML to translate from abbreviated name to actual full-length name

        abbreviations = {}

        for fn in yaml_dict.get('functions', []):
            f_name = fn.get('name', 'unknown')
            f_abbr = fn.get('abbreviation', 'unknown')
            abbreviations[f_abbr] = f_name

        for m_fn in yaml_dict.get('modifier_functions', []):
            mf_name = m_fn.get('name', 'unknown')
            mf_abbr = m_fn.get('abbreviation', 'unknown')
            abbreviations[mf_abbr] = mf_name

        return abbreviations

    def names_to_abbreviations(self, yaml_dict):
        # uses YAML to translate from full-length name to abbreviated name.

        names = {}

        for fn in yaml_dict.get('functions', []):
            f_name = fn.get('name', 'unknown')
            f_abbr = fn.get('abbreviation', 'unknown')
            names[f_name] = f_abbr

        for m_fn in yaml_dict.get('modifier_functions', []):
            mf_name = m_fn.get('name', 'unknown')
            mf_abbr = m_fn.get('abbreviation', 'unknown')
            names[mf_name] = mf_abbr

        return names

    def args_to_given_sig_list(self, args_given):
        signature_list = []

        for arg in args_given:
            for arg_type in arg:
                if arg_type == 'ns_arg':
                    signature_list.append('Entity')
                elif arg_type == 'function':
                    signature_list.append('Function')
                elif arg_type == 'm_function':
                    signature_list.append('Modifier')
                elif arg_type == 'str_arg':
                    signature_list.append('String')
                else:  # else could simply be an argument of a function, we don't need to include this in signature
                    pass

        return signature_list

    def get_relations(self, yaml_dict):
        """
        Retrieves all valid relations specified in the YAML and returns a list of unique relations.
        """

        relations = set()

        for relation in yaml_dict.get('relations', []):
            r_name = relation.get('name', None)
            r_abbr = relation.get('abbreviation', None)

            relations.add(r_name)
            relations.add(r_abbr)

        return list(relations)