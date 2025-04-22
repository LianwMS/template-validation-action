import os
import unittest
import utils
from validator.file_validator import FileValidator
from constants import ItemResultFormat, Signs
from severity import Severity
from validator.remote_build_validator import RemoteBuildValidator


def test_containerapp_remote_build_enabled():
    validator = RemoteBuildValidator(
        "TestCatalog", "test/data/RemoteBuildCaseData/ContainerAppEnabled", Severity.MODERATE)

    result, message = validator.validate()
    assert result is True
    assert message == ItemResultFormat.PASS.format(message="Remote build")

def test_containerapp_remote_build_disabled():
    validator = RemoteBuildValidator(
        "TestCatalog", "test/data/RemoteBuildCaseData/ContainerAppDisabled", Severity.HIGH)

    result, message = validator.validate()
    assert result is False
    assert message == ItemResultFormat.FAIL.format(
        sign=Signs.BLOCK, message="Remote build", detail_messages="RemoteBuild is not enabled in " + utils.formatPathwithOS("test/data/RemoteBuildCaseData/ContainerAppDisabled/azure.yml")
    )

def test_containerapp_nodocker_remote_build_disabled():
    validator = RemoteBuildValidator(
        "TestCatalog", "test/data/RemoteBuildCaseData/ContainerAppNoDocker", Severity.HIGH)

    result, message = validator.validate()
    assert result is False
    assert message == ItemResultFormat.FAIL.format(
        sign=Signs.BLOCK, message="Remote build", detail_messages="RemoteBuild is not enabled in " + utils.formatPathwithOS("test/data/RemoteBuildCaseData/ContainerAppNoDocker/azure.yaml")
    )

def test_aks_remote_build_disabled():
    validator = RemoteBuildValidator(
        "TestCatalog", "test/data/RemoteBuildCaseData/AksDisabled", Severity.MODERATE)

    result, message = validator.validate()
    assert result is False
    assert message == ItemResultFormat.FAIL.format(
        sign=Signs.WARNING, message="Remote build", detail_messages="RemoteBuild is not enabled in " + utils.formatPathwithOS("test/data/RemoteBuildCaseData/AksDisabled/azure.yaml")
    )