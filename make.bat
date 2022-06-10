:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: LICENSING                                                                    :
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::
:: Copyright 2020 Esri
::
:: Licensed under the Apache License, Version 2.0 (the "License"); You
:: may not use this file except in compliance with the License. You may
:: obtain a copy of the License at
::
:: http://www.apache.org/licenses/LICENSE-2.0
::
:: Unless required by applicable law or agreed to in writing, software
:: distributed under the License is distributed on an "AS IS" BASIS,
:: WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
:: implied. See the License for the specific language governing
:: permissions and limitations under the License.
::
:: A copy of the license is available in the repository's
:: LICENSE file.

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: VARIABLES                                                                    :
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

SETLOCAL
SET PROJECT_DIR=%cd%
SET PROJECT_NAME=d4_accessibility
SET SUPPORT_LIBRARY = d4_accessibility
SET ENV_NAME=d4_accessibility

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: COMMANDS                                                                     :
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

:: Jump to command
GOTO %1


:: Build the local environment from the environment file
:env
    ENDLOCAL & (
        :: Install MAMBA for faster solves
        CALL conda install -c conda-forge mamba yaml -y
        :: update environment with package dependencies
        CALL python check_package_deps.py
        :: Create new environment from environment file
        CALL mamba env create -f build_environment.yml
        :: Activate the environment so you can get to work
        CALL activate "%ENV_NAME%"
        :: Install the local package in development (experimental) mode
        CALL python -m pip install -e .
    )
    EXIT /B

:: Activate the environment
:env_activate
    ENDLOCAL & CALL activate "%ENV_NAME%"
    EXIT /B


:: Remove the environment
:env_remove
    ENDLOCAL & (
        CALL conda deactivate
        CALL conda env remove --name "%ENV_NAME%" -y
    )
    EXIT /B