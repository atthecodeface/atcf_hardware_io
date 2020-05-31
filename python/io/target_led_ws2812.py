#a Copyright
#  
#  This file 'target_timer.py' copyright Gavin J Stark 2020
#  
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

#a Imports
from cdl.utils.csr   import Csr, CsrField, CsrFieldZero, Map, MapCsr, CsrFieldResvd

#a CSRs
class ConfigCsr(Csr):
    _fields = {0:  CsrField(width=8, name="divider", brief="divider", doc="400ns clock divider value"),
               8:  CsrFieldResvd(width=8),
               16: CsrField(width=4, name="last_led", brief="last", doc="Last LED in the chain"),
               20:  CsrFieldResvd(width=12),
              }
class LedCsr(Csr):
    _fields = {0:  CsrField(width=8, name="red",   brief="r", doc="8-bit Red value for LED"),
               8:  CsrField(width=8, name="green", brief="g", doc="8-bit Green value for LED"),
               8:  CsrField(width=8, name="blue",  brief="b", doc="8-bit Blue value for LED"),
               24:  CsrFieldResvd(width=8),
              }

class LedWs2812AddressMap(Map):
    _map = [ MapCsr(reg=0,  name="config", brief="cfg", csr=ConfigCsr, doc=""),
             MapCsr(reg=16, name="led0", brief="led0", csr=LedCsr, doc=""), # write only
             MapCsr(reg=17, name="led1", brief="led1", csr=LedCsr, doc=""), # write only
             MapCsr(reg=18, name="led2", brief="led2", csr=LedCsr, doc=""), # write only
             MapCsr(reg=19, name="led3", brief="led3", csr=LedCsr, doc=""), # write only
             ]
             
