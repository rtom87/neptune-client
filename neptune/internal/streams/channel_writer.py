#
# Copyright (c) 2019, Neptune Labs Sp. z o.o.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from __future__ import unicode_literals

from datetime import datetime
import re

from neptune.internal.channels.channels import ChannelNamespace, ChannelValue, ChannelType


class ChannelWriter(object):
    __SPLIT_PATTERN = re.compile(r'[\n\r]{1,2}')

    def __init__(self, experiment, channel_name, channel_namespace=ChannelNamespace.USER):
        self._time_started = experiment.get_system_properties()['created']
        self._experiment = experiment
        self._channel_name = channel_name
        self._channel_namespace = channel_namespace
        self._data = None

    def write(self, data):
        if self._data is None:
            self._data = data
        else:
            self._data += data
        lines = self.__SPLIT_PATTERN.split(self._data)
        for line in lines[:-1]:
            value = ChannelValue(
                x=(datetime.now(tz=self._time_started.tzinfo) - self._time_started).total_seconds() * 1000,
                y=dict(text_value=str(line)),
                ts=None
            )
            # pylint: disable=protected-access
            self._experiment._channels_values_sender.send(
                channel_name=self._channel_name,
                channel_type=ChannelType.TEXT.value,
                channel_value=value,
                channel_namespace=self._channel_namespace
            )

        self._data = lines[-1]
