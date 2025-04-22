import os
import logging
import utils
from validator.validator_base import ValidatorBase
from constants import ItemResultFormat, line_delimiter, Signs
from utils import indent
from severity import Severity
import yaml


class RemoteBuildValidator(ValidatorBase):
    def __init__(
        self,
        validatorCatalog,
        folderPath,
        severity=Severity.LOW,
    ):
        super().__init__("RemoteBuildValidator", validatorCatalog, severity)
        self.folderPath = folderPath

    def validate(self):
        self.result = True
        self.messages = []
        self.subMessages = []

        # find full path for azure.yaml or azure.yml file from the folder path and it's subfolder.
        azure_yaml_path = []
        for root, dirs, files in os.walk(self.folderPath):
            for file in files:
                if file.lower() == "azure.yaml" or file.lower() == "azure.yml":
                    azure_yaml_path.append(os.path.join(root, file))

        if not azure_yaml_path:
            self.result = False
            self.subMessages.append(f"azure.yaml or azure.yml file not found in {self.folderPath}.")
        else:
            for azure_yaml in azure_yaml_path:
                logging.debug(f"Validating remote build in {azure_yaml}")
                self.result = self.result and self.validateRemoteBuildinFile(azure_yaml)
                if not self.result:
                    self.subMessages.append(
                        f"RemoteBuild is not enabled in " + utils.formatPathwithOS(azure_yaml)
                    )
                else:
                    self.subMessages.append(
                        f"RemoteBuild is enabled in " + utils.formatPathwithOS(azure_yaml)
                    )

        if self.result:
            self.messages.append(
                ItemResultFormat.PASS.format(
                    message=f"Remote build"
                )
            )
        else:
            self.messages.append(
                ItemResultFormat.FAIL.format(
                    sign=Signs.BLOCK
                    if Severity.isBlocker(self.severity)
                    else Signs.WARNING,
                    message=f"Remote build",
                    detail_messages=line_delimiter.join(self.subMessages),
                )
            )

        self.resultMessage = line_delimiter.join(self.messages)
        return self.result, self.resultMessage

    def validateRemoteBuildinFile(self, filePath):
        logging.debug(f"Validating remote build in {filePath}")
        self.result = True
        with open(filePath, "r") as file:
            # read the yaml file from filePath and check each service in services secton.
            # if it's host is 'containerapp' and remoteBuild under docker section is not set to true, then return false.
            # if it's host is 'containerapp' and remoteBuild under docker section is set to true, then return true.
            content = yaml.safe_load(file)
            if "services" in content:
                for service in content["services"]:
                    if "host" in content["services"][service]:
                        if content["services"][service]["host"] == "containerapp" or content["services"][service]["host"] == "aks":
                            if "docker" in content["services"][service]:
                                if "remoteBuild" in content["services"][service]["docker"]:
                                    if content["services"][service]["docker"]["remoteBuild"] == "false":
                                        self.result = self.result & False
                                else:
                                    self.result = self.result & False
                            else:
                                if "language" in content["services"][service]:
                                    if content["services"][service]["language"] != "dotnet":
                                        self.result = self.result & False
                                else:
                                    self.result = self.result & False

            file.close()
        return self.result

