# SPDX-FileCopyrightText: 2024 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
import logging

from licomp.interface import Licomp
from licomp.interface import UseCase
from licomp.interface import Provisioning
from licomp.interface import CompatibilityStatus

from licomp_doubleopen.doubleopen import LicompDoubleOpen

lo = LicompDoubleOpen()

def test_supported():
    assert len(lo.supported_licenses()) == 26
    
def test_license_is_supported():
    assert lo.license_supported("BSD-3-Clause")
    
def test_license_is_not_supported():
    assert not lo.license_supported("Some-license-that-does-not-exist")
    
def test_usecase_is_supported():
    assert lo.usecase_supported(UseCase.LIBRARY)
    
def test_usecase_is_not_supported():
    assert not lo.usecase_supported(UseCase.SNIPPET)
    
def test_provisioning_is_supported():
    assert lo.provisioning_supported(provisioning=Provisioning.BIN_DIST)
    
def test_provisioning_is_not_supported():
    assert not lo.provisioning_supported(provisioning=Provisioning.WEBUI)
    
def test_compat():
    ret = lo.outbound_inbound_compatibility("GPL-2.0-only", "BSD-3-Clause", usecase=UseCase.LIBRARY, provisioning=Provisioning.BIN_DIST)
    logging.debug("ret: " + str(ret))
    assert ret['compatibility_status'] == "yes"
    assert ret['status'] == "success"

def test_incompat_1():
    ret = lo.outbound_inbound_compatibility("BSD-3-Clause", "GPL-2.0-only", usecase=UseCase.LIBRARY, provisioning=Provisioning.BIN_DIST)
    logging.debug("ret: " + str(ret))
    assert ret['compatibility_status'] == "no"
    assert ret['status'] == "success"

def test_incompat_2():
    ret = lo.outbound_inbound_compatibility("BSD-3-Clause", "GPL-2.0-only", usecase=UseCase.LIBRARY, provisioning=Provisioning.BIN_DIST)
    logging.debug("ret: " + str(ret))
    assert ret['status'] == 'success'
    assert ret['compatibility_status'] == 'no'

def test_incompat_3():
    ret = lo.outbound_inbound_compatibility("BSD-3-Clause", "DO_NO_EXIST", usecase=UseCase.LIBRARY, provisioning=Provisioning.BIN_DIST)
    logging.debug("ret: " + str(ret))
    assert ret['compatibility_status'] == None
    assert ret['status'] == "failure"

def test_incompat_4():
    ret = lo.outbound_inbound_compatibility("DO_NO_EXIST", "GPL-2.0-only", usecase=UseCase.LIBRARY, provisioning=Provisioning.BIN_DIST)
    logging.debug("ret: " + str(ret))
    assert ret['compatibility_status'] == None
    assert ret['status'] == "failure"

def test_api_version():
    licomp_api_version = lo.api_version()
    lo_api_version = lo.supported_api_version()
    logging.debug(f'versions: {licomp_api_version} {lo_api_version}')
    assert licomp_api_version.split('.')[0] == lo_api_version.split('.')[0]
    assert licomp_api_version.split('.')[1] == lo_api_version.split('.')[1]
