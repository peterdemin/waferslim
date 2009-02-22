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

class SlimConstants(object):
    ''' Mixin class for constants '''
    _VERSION = 'Slim -- V0.0\n'
    _START_CHUNK = '['
    _END_CHUNK = ']'
    _SEPARATOR = ':'
    _SEPARATOR_LENGTH = len(_SEPARATOR)
    _NUMERIC_LENGTH = 6
    _NUMERIC_BLOCK_LENGTH = _NUMERIC_LENGTH + _SEPARATOR_LENGTH
    _NUMERIC_ENCODING = '%%0%sd' % _NUMERIC_LENGTH
    _ITEM_ENCODING = _NUMERIC_ENCODING + '%s%s'
    _DISCONNECT = 'bye'

class SlimProtocol(SlimConstants):
    ''' Responsible for packing / unpacking chunked-up data that conforms 
    to the protocol spec '''
    
    def unpack(self, packed_string):
        ''' Unpack a chunked-up packed_string into a list '''
        if isinstance(packed_string, str) \
        or isinstance(packed_string, unicode):
            chunks = []
            self._unpack_chunk(packed_string, chunks)
            return chunks
        raise TypeError('%r is not a string' % packed_string)
        
    def _unpack_chunk(self, packed_chunk, chunks):
        ''' Unpack a packed chunk, recursively if required '''
        self._check_chunk(packed_chunk)
        pos = 1
        chunk_len = int(packed_chunk[pos:pos + SlimConstants._NUMERIC_LENGTH])
        self._check_separator(packed_chunk, pos + SlimConstants._NUMERIC_LENGTH)
        pos += SlimConstants._NUMERIC_BLOCK_LENGTH 
        
        for i in range(0, chunk_len):
            item_len = int(packed_chunk[pos:pos + SlimConstants._NUMERIC_LENGTH])
            self._check_separator(packed_chunk, pos + SlimConstants._NUMERIC_LENGTH)
            pos += SlimConstants._NUMERIC_BLOCK_LENGTH 
        
            item = packed_chunk[pos:pos + item_len]
            self._check_separator(packed_chunk, pos + item_len)
            pos += (item_len + SlimConstants._SEPARATOR_LENGTH)
            
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
        if possible_chunk.startswith(SlimConstants._START_CHUNK):
            if possible_chunk.endswith(SlimConstants._END_CHUNK):
                return True
            elif raise_on_failure: 
                msg = '%r has no trailing %r' % (possible_chunk, 
                                                 SlimConstants._END_CHUNK)
            else:
                return False
        elif raise_on_failure: 
            msg = '%r has no leading %r' % (possible_chunk, 
                                            SlimConstants._START_CHUNK)
        else:
            return False
        raise UnpackingError(msg)
        
    def _check_separator(self, packed_chunk, pos):
        ''' Verify existence of separator at position pos in a packed_chunk '''
        if SlimConstants._SEPARATOR != packed_chunk[pos]:
            msg = '%r has no %r separator at pos %s' % \
                (packed_chunk, SlimConstants._SEPARATOR, pos)
            raise UnpackingError(msg)
        
    def pack(self, item_list):
        ''' Pack each item from a list into the chunked-up format '''
        packed = [self._pack_item(item) for item in item_list]
        packed.insert(0, SlimConstants._NUMERIC_ENCODING % len(item_list))
        return '%s%s%s%s' % (SlimConstants._START_CHUNK,
                             SlimConstants._SEPARATOR.join(packed),
                             SlimConstants._SEPARATOR,
                             SlimConstants._END_CHUNK)
    
    def _pack_item(self, item): 
        ''' Pack (recursively if required) a single item in the format:  
        [iiiiii:llllll:item...]'''
        if isinstance(item, list):
            return self._pack_item(self.pack(item))
        
        str_item = item and str(item) or 'null'
        return SlimConstants._ITEM_ENCODING % (len(str_item), 
                                              SlimConstants._SEPARATOR, 
                                              str_item)
        
class RequestResponder(SlimConstants):
    ''' Mixin class for responding to Slim requests.
    Logic mostly reverse engineered from Java test classes especially 
    fitnesse.responders.run.slimResponder.SlimTestSystemTest '''

    def respond_to(self, request, byte_encoding='utf-8'):
        ''' Entry point for mixin: respond to a Slim protocol request.
        Basic format of every interaction is:
        - every request requires an initial ACK with the Slim Version
        - messages can then be received and responses sent, in a loop
        - receiving a 'bye' message will terminate the loop 
        '''
        ack_bytes = self._send_ack(request, byte_encoding)
        
        received, sent = self._process_messages(request, byte_encoding)
        
        return received, sent + ack_bytes
    
    def _send_ack(self, request, byte_encoding):
        ''' Acknowledge the request by sending the Slim Version '''
        response = SlimConstants._VERSION.encode(byte_encoding)
        self.debug('Send Ack')
        return request.send(response)
    
    def _process_messages(self, request, byte_encoding):
        ''' Receive messages from the request and send responses.
        Each message starts with a numeric header (number of digits defined
        in SlimConstants._NUMERIC_LENGTH) which contains the byte length
        of the message contents. The message contents can then be read
        and acted on.'''
        received, sent = 0, 0
        
        while True:
            message_length, bytes_received = \
                self._get_message_length(request, byte_encoding)
            received += bytes_received
            data = request.recv(message_length).decode(byte_encoding)
            self.debug('Recv message: %r' % data)
            received += message_length
            
            if SlimConstants._DISCONNECT == data:
                break
            else:
                SlimProtocol().unpack(data)
                msg = '000009:[000000:]'
                response = msg.encode(byte_encoding)
                sent += request.send(response)
                self.debug('Send response: %r' % msg)
        
        return received, sent
    
    def _get_message_length(self, request, byte_encoding):
        ''' Get the length of the message from an initial numeric header '''
        header_format = (SlimConstants._NUMERIC_ENCODING % 0) + \
                        SlimConstants._SEPARATOR 
        byte_size = len(header_format.encode(byte_encoding))
        data = request.recv(byte_size).decode(byte_encoding)
        length = int(data[0:SlimConstants._NUMERIC_LENGTH])
        return length, byte_size
        
    def debug(self, msg):
        ''' log a debug msg '''
        pass