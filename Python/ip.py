# tcp.py -- example of building and sending a raw TCP packet
# Copyright (C) 2020  Nikita Karamov  <nick@karamoff.dev>
#
# With code from Scapy (changes documented below) 
# Copyright (C) 2019  Philippe Biondi <phil@secdev.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import array
import socket
import struct

# This part of code was adapted from the Scapy project:
# https://github.com/secdev/scapy/blob/467431faf8389f745d2c16370baf6dafc5751731/scapy/utils.py#L368-L381
#
# Changes made:
# - removed use of checksum_endian_transform function
# - restructured code without modifying it
# - renamed variables
# - added type hints
def chksum(packet: bytes) -> int:
    if len(packet) % 2 != 0:
        packet += b'\0'

    res = sum(array.array("H", packet))
    res = (res >> 16) + (res & 0xffff)
    res += res >> 16

    return (~res) & 0xffff


class TCPPacket:
    def __init__(self,
                 src_host:  str,
                 src_port:  int,
                 dst_host:  str,
                 dst_port:  int,
                 flags:     int = 0):
        self.src_host = src_host
        self.src_port = src_port
        self.dst_host = dst_host
        self.dst_port = dst_port
        self.flags = flags
        print("Src IP: %s Src port: %d Desti: %s port: %d flags: %d" % (self.src_host,self.src_port,self.dst_host,self.dst_port,self.flags))

    def build(self) -> bytes:
        packet = struct.pack(
            '!HHIIBBHHH',
            self.src_port,  # Source Port
            self.dst_port,  # Destination Port
            1567760897,              # Sequence Number
            1522462666,              # Acknoledgement Number
            5 << 4,         # Data Offset
            self.flags,     # Flags
            0,           # Window
            0,              # Checksum (initial value)
            0               # Urgent pointer
        )

        pseudo_hdr = struct.pack(
            '!4s4sHH',
            socket.inet_aton(self.src_host),    # Source Address
            socket.inet_aton(self.dst_host),    # Destination Address
            socket.IPPROTO_TCP,                 # PTCL
            len(packet)                         # TCP Length
        )

        checksum = chksum(pseudo_hdr + packet)
        print("CHK:", checksum)
        packet = packet[:16] + struct.pack('H', checksum) + packet[18:]
        #packet = str(packet).encode("utf-8")
        result = ' '.join(hex((char)) for char in packet)
        print(result)
        return packet


if __name__ == '__main__':
    dst = '192.168.2.151'

    pak = TCPPacket(
        '13.89.178.27',
        443,
        dst,
        62812,
        0b00010100  # Merry Christmas!
    )
    server= ('192.168.2.151',0)
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    
    tempString  = str(3) #"%.2f"%temperature;
    #s.sendto(tempString.encode("utf-8"),server)
    s.sendto(pak.build(), server)