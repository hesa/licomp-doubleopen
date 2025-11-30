#!/bin/env python3

# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import yaml

import logging
logging.basicConfig(level=logging.DEBUG)
from matrix.licenses import LICENSES

category_matrix = {
    'public-domain': True,
    'copyleft-file-level': True,
    'property:network-clause': True,
    'include-in-notice-file': True,
    'permissive': True,
    'property:creativecommons': False,
    'property:antitivo-clause': False,
    'copyleft-LGPL': True,
    'property:include-in-notice-file': True,
    'property:patent-clause': False,
    'copyleft-strong': False,
    'property:distribute-source-code': True,
}

YES = 'yes'
NO = 'no'
DEPENDS = 'depends'
UNKNOWN = 'unknown'
UNSUPPORTED = 'unsupported'

COMPAT_LEVELS = {
    YES: 0,
    DEPENDS: 1,
    UNKNOWN: 2,
    NO: 3,
    UNSUPPORTED: 4,
}

COMPATS = {
    0: YES,
    1: DEPENDS,
    2: UNKNOWN,
    3: NO,
    4: UNSUPPORTED,
}

NO_FURTHER_RESTRICTION_LICENSES = [
    'AGPL-3.0-only',
    'AGPL-3.0-or-later',
    'GPL-1.0-only',
    'GPL-1.0-or-later',
    'GPL-2.0-only',
    'GPL-2.0-or-later',
]

# init
def _read_classifications():
    with open('matrix/license-classifications.yml') as fp:
        data = yaml.safe_load(fp)
    return data
def _categories():
    return [x['name'] for x in classifications['categories']]
classifications = _read_classifications()
categories = _categories()


def _licenses():
    return classifications['categorizations']

def _check_licenses_supported(licenses):
    license_ids = [x['id'] for x in _licenses()]
    for lic in licenses:
        if not lic in license_ids:
            panic(f'License "{lic}" not supported')
    for lic_object in _licenses():
        if lic_object['id'] not in LICENSES:
            #logging.debug("ignore .. " + lic_object['id'])
            continue
        for cat in lic_object['categories']:
            if cat not in _licenses_categories(LICENSES):
                panic(f'Category "{cat}", in {lic_object["id"]}, not supported')
    logging.debug("checks passed")

def _license_object(license_name):
    return [x for x in _licenses() if x['id'] == license_name][0]
    
def _license_categories(license_name):
    return _license_object(license_name)['categories']

def _licenses_categories(license_names):
    cats = set()
    for license_name in license_names:
        for cat in _license_categories(license_name):
            cats.add(cat)
            #if "creative" in cat:
            #    logging.debug(f'{license_name} has {cat}')
    return list(cats)

def _check_further_restriction_general(outbound_category, outbound,
                                       inbound_category, inbound):
    if outbound in NO_FURTHER_RESTRICTION_LICENSES:
        outbound_object = _license_object(outbound)
        outbound_categories = outbound_object['categories']
        if not inbound_category in outbound_categories:
            reason = f'Inbound license "{inbound}" has "{inbound_category}", but outbound license "{outbound}" does not.'
            return NO, reason
        else:
            logging.debug(f'Inbound license "{inbound}" has "{inbound_category}" as do outbound license "{outbound}" ({outbound_categories}).')
            return YES, None

    return YES, None
    
def _check_further_restriction_patent(outbound_category, outbound,
                                      inbound):
    return  _check_further_restriction_general(outbound_category, outbound,
                                               'property:patent-clause', inbound)

def _check_further_restriction_tivo(outbound_category, outbound,
                                    inbound):
    return  _check_further_restriction_general(outbound_category, outbound,
                                               'property:antitivo-clause', inbound)

def panic(msg=''):
    import sys
    print(f'PANIC: {msg}.')
    sys.exit(1)
        
def category_compatibile_with_category(outbound_category, outbound,
                                       inbound_category, inbound):

    # If the inbound category always is compatible:
    if category_matrix[inbound_category]:
        return YES, None

    # ... else, check specific rules
    if inbound_category == 'property:creativecommons':
        if inbound == 'CC0-1.0':
            return YES, None
        return UNKNOWN, "TODO"
    elif inbound_category == 'property:antitivo-clause':
        ret, reason = _check_further_restriction_tivo(outbound_category, outbound, inbound)
        if ret:
            return ret, reason
        return YES, None
    elif inbound_category == 'property:patent-clause':
        ret, reason = _check_further_restriction_patent(outbound_category, outbound, inbound)
        if ret:
            return ret, reason
        return YES, None
    elif inbound_category == 'copyleft-strong':
        if outbound.startswith('AGPL-3') and inbound.startswith('AGPL-3'):
            if not (outbound.endswith('-or-later') and inbound.endswith('-only')):
                return YES, None
        if outbound.startswith('GPL-2') and inbound.startswith('GPL-2'):
            if not (outbound.endswith('-or-later') and inbound.endswith('-only')):
                return YES, None
        if (outbound.startswith('GPL-3') or outbound.startswith('AGPL-3')) and inbound.startswith('GPL-3'):
            if not (outbound.endswith('-or-later') and inbound.endswith('-only')):
                return YES, None

        return NO, f'The inbound license "{inbound}" is a copyleft license so you cannot use "{outbound}" as outbound license.'
    panic("unknown ...")

def license_compatible_with_license(outbound, inbound):
    if outbound == inbound:
        return []
    
    outbound_object = _license_object(outbound)
    outbound_categories = outbound_object['categories']
    
    inbound_object = _license_object(inbound)
    inbound_categories = inbound_object['categories']

    category_compats = []
    for outbound_category in outbound_categories:
        for inbound_category in inbound_categories:
            val, reason = category_compatibile_with_category(outbound_category, outbound, inbound_category, inbound)
            if val != "yes":
                category_compats.append((val, reason))
    category_compats = list(set(category_compats))
    return category_compats

def _worst_compat_level(compats):
    worst = COMPAT_LEVELS[YES]
    for compat, reason in compats:
        compat_level = COMPAT_LEVELS[compat]
        if compat_level > worst:
            worst = compat_level
    return worst



# main
_check_licenses_supported(LICENSES)

matrix = {
    'meta': {
    },
    'licenses': {},
}
for outbound in LICENSES:
    matrix['licenses'][outbound] = {}
    for inbound in LICENSES:
        compats = license_compatible_with_license(outbound, inbound)
        compatible = _worst_compat_level(compats)
        logging.debug(f'{outbound} <--- {inbound}: {compatible}: {compatible} {compats}')
        matrix['licenses'][outbound][inbound] = {
            'compatibility': COMPATS[compatible],
            'comment': [reason for compat, reason in compats],
        }
import json
print(json.dumps(matrix))
#compat = category_compatibile_with_category('property:distribute-source-code', 'GPL-2.0-or-later', 'property:patent-clause', 'Apache-2.0')

#compat = category_compatibile_with_category('property:distribute-source-code', 'GPL-2.0-or-later',  'property:antitivo-clause', 'GPL-3.0-or-later')



