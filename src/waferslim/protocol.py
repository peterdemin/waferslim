'''
Core protocol classes. 

See http://fitnesse.org/FitNesse.SliM.SlimProtocol for more details.
    
The latest source code is available at http://code.launchpad.net/waferslim.

Copyright 2009 by the author(s). All rights reserved 
'''

from waferslim import WaferSlimException

class UnpackingError(WaferSlimException):
    ''' An attempt was made to unpack messages that do not conform to the protocol spec '''  
    pass

class SlimProtocol(object):
    ''' Responsible for packing / unpacking messages that conform with the protocol spec '''
      
    VERSION = 'V0.0'
    _START_CHUNK = '['
    _END_CHUNK = ']'
    _SEPARATOR = ':'
    _SEPARATOR_LENGTH = len(_SEPARATOR)
    _NUMERIC_LENGTH = 6
    _NUMERIC_BLOCK_LENGTH = _NUMERIC_LENGTH + _SEPARATOR_LENGTH
    _NUMERIC_ENCODING = '%%0%sd' % _NUMERIC_LENGTH
    _ITEM_ENCODING = _NUMERIC_ENCODING + '%s%s'
    
    def unpack(self, packed_string):
        ''' Unpack a chunked-up packed string '''
        if not isinstance(packed_string, str):
            raise TypeError('%r is not a string' % packed_string)
        chunks = []
        self._unpack_chunk(packed_string, chunks)
        return chunks
        
    def _unpack_chunk(self, packed_chunk, chunks):
        ''' Unpack a packed chunk, recursively if required '''
        self._check_chunk(packed_chunk)
        pos = 1
        chunk_len = int(packed_chunk[pos:pos + SlimProtocol._NUMERIC_LENGTH])
        self._check_separator(packed_chunk, pos + SlimProtocol._NUMERIC_LENGTH)
        pos += SlimProtocol._NUMERIC_BLOCK_LENGTH 
        
        for i in range(0, chunk_len):
            item_len = int(packed_chunk[pos:pos + SlimProtocol._NUMERIC_LENGTH])
            self._check_separator(packed_chunk, pos + SlimProtocol._NUMERIC_LENGTH)
            pos += SlimProtocol._NUMERIC_BLOCK_LENGTH 
        
            item = packed_chunk[pos:pos + item_len]
            self._check_separator(packed_chunk, pos + item_len)
            pos += (item_len + SlimProtocol._SEPARATOR_LENGTH)
            
            if self._is_chunk(item):
                sub_chunk = []
                self._unpack_chunk(item, sub_chunk)
                chunks.append(sub_chunk)
            else:
                chunks.append(item)
        
    def _check_chunk(self, packed_chunk):
        ''' Verify format of an packed_chunk '''
        self._is_chunk(packed_chunk, raise_on_failure=True)
        
    def _is_chunk(self, possible_chunk, raise_on_failure=False):
        ''' Check for indicative start/end of an encoded chunk '''
        if possible_chunk.startswith(SlimProtocol._START_CHUNK):
            if possible_chunk.endswith(SlimProtocol._END_CHUNK):
                return True
            elif raise_on_failure: 
                msg = '%r has no trailing %r' % (possible_chunk, SlimProtocol._END_CHUNK)
            else:
                return False
        elif raise_on_failure: 
            msg = '%r has no leading %r' % (possible_chunk, SlimProtocol._START_CHUNK)
        else:
            return False
        raise UnpackingError(msg)
        
    def _check_separator(self, packed_chunk, pos):
        ''' Verify existence of a separator at position pos in an packed_chunk '''
        if SlimProtocol._SEPARATOR != packed_chunk[pos]:
            msg = '%r has no %r separator at pos %s' % (packed_chunk, 
                                                        SlimProtocol._SEPARATOR,
                                                        pos)
            raise UnpackingError(msg)
            
        
    def pack(self, item_list):
        ''' Pack each item in a list  '''
        packed = [self._pack_item(item) for item in item_list]
        packed.insert(0, SlimProtocol._NUMERIC_ENCODING % len(item_list))
        return '%s%s%s%s' % (SlimProtocol._START_CHUNK,
                             SlimProtocol._SEPARATOR.join(packed),
                             SlimProtocol._SEPARATOR,
                             SlimProtocol._END_CHUNK)
    
    def _pack_item(self, item): 
        ''' Pack (recursively if required) a single item in the format:  
        [iiiiii:llllll:item...]'''
        if isinstance(item, list):
            return self._pack_item(self.pack(item))
        
        str_item = item and str(item) or 'null'
        return SlimProtocol._ITEM_ENCODING % (len(str_item), 
                                              SlimProtocol._SEPARATOR, 
                                              str_item)