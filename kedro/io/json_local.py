# Copyright 2018-2019 QuantumBlack Visual Analytics Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND
# NONINFRINGEMENT. IN NO EVENT WILL THE LICENSOR OR OTHER CONTRIBUTORS
# BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF, OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# The QuantumBlack Visual Analytics Limited ("QuantumBlack") name and logo
# (either separately or in combination, "QuantumBlack Trademarks") are
# trademarks of QuantumBlack. The License does not grant you any right or
# license to the QuantumBlack Trademarks. You may not use the QuantumBlack
# Trademarks or any confusingly similar mark as a trademark for your product,
#     or use the QuantumBlack Trademarks in any other manner that might cause
# confusion in the marketplace, including but not limited to in advertising,
# on websites, or on software.
#
# See the License for the specific language governing permissions and
# limitations under the License.

"""``JSONLocalDataSet`` encodes a given object to json and saves it to a local
file.
"""
import json
from pathlib import Path
from typing import Any, Dict

import pandas as pd

from kedro.io.core import AbstractDataSet, DataSetError, FilepathVersionMixIn, Version


class JSONLocalDataSet(AbstractDataSet, FilepathVersionMixIn):
    """``JSONLocalDataSet`` encodes data as json and saves it to a local file
    or reads in and decodes an existing json file. The encoding/decoding
    functionality is provided by Python's ``json`` library.

    Example:
    ::

        >>> from kedro.io import JSONLocalDataSet
        >>> my_dict = {
        >>>     'a_string': 'Hello, World!',
        >>>     'a_list': [1, 2, 3]
        >>> }
        >>> data_set = JSONLocalDataSet(filepath="test.json")
        >>> data_set.save(my_dict)
        >>> reloaded = data_set.load()
        >>> assert my_dict == reloaded

    """

    def _describe(self) -> Dict[str, Any]:
        return dict(
            filepath=self._filepath,
            load_args=self._load_args,
            save_args=self._save_args,
            version=self._version,
        )

    def __init__(
        self,
        filepath: str,
        load_args: Dict[str, Any] = None,
        save_args: Dict[str, Any] = None,
        version: Version = None,
    ) -> None:
        """Creates a new instance of ``JSONLocalDataSet`` pointing to a concrete
        filepath.

        Args:
            filepath: path to a local json file.
            load_args: Arguments passed on to ```json.load``.
                See https://docs.python.org/3/library/json.html for details.
                All defaults are preserved.
            save_args: Arguments passed on to ```json.dump``.
                See https://docs.python.org/3/library/json.html
                for details. All defaults are preserved.
            version: If specified, should be an instance of
                ``kedro.io.core.Version``. If its ``load`` attribute is
                None, the latest version will be loaded. If its ``save``
                attribute is None, save version will be autogenerated.

        """
        default_save_args = {"indent": 4}
        default_load_args = {}
        self._filepath = filepath
        self._load_args = (
            {**default_load_args, **load_args}
            if load_args is not None
            else default_load_args
        )
        self._save_args = (
            {**default_save_args, **save_args}
            if save_args is not None
            else default_save_args
        )
        self._version = version

    def _load(self) -> Any:
        load_path = self._get_load_path(self._filepath, self._version)
        with open(load_path, "r") as local_file:
            return json.load(local_file, **self._load_args)

    def _save(self, data: pd.DataFrame) -> None:
        save_path = Path(self._get_save_path(self._filepath, self._version))
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with save_path.open("w") as local_file:
            json.dump(data, local_file, **self._save_args)

        load_path = Path(self._get_load_path(self._filepath, self._version))
        self._check_paths_consistency(
            str(load_path.absolute()), str(save_path.absolute())
        )

    def _exists(self) -> bool:
        try:
            path = self._get_load_path(self._filepath, self._version)
        except DataSetError:
            return False
        return Path(path).is_file()