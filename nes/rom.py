'''
    The rom package contains the main code for nesi. This package contains the
    NesRom class and all operations on the rom data as well as all printing of
    results.
'''

# Import standard library modules
from __future__ import print_function

import os

# Import nesi modules
import nes.mappers
import nes.settings


def nesi_information():
    '''
        Returns a string that describes the current nesi version and author
    '''

    build = nes.settings.build()

    return 'nesi {major}.{minor} by {author} ({author_email})'.format(
        major=build['major_version'],
        minor=build['minor_version'],
        author=build['author'],
        author_email=build['author_email'],
    )


def fmt_str(tag, string, seperator=' | '):
    '''
        A minor helper function. Takes in a tag and string and outputs a
        formatted string with the tag left justified and the string right
        justified.
    '''

    return tag.ljust(12) + seperator + string


class NesRom(object):
    '''
        The main work horse of nesi. The NesRom contains all rom data and
        can before analysis of the rom data.
    '''

    def __init__(self, rom_path):
        self.rom_name = os.path.basename(rom_path)

        with open(rom_path, 'rb') as fopen:
            self.rom_data = bytearray(fopen.read())

        self.rom_size = len(self.rom_data)

    def battery(self):
        '''
            Returns 'Yes' if the rom contains battery backed RAM, and returns
            'No' if it does not.
        '''

        if ((self.rom_data[6] >> 1) & 0x1) == 1:
            return 'Yes'
        else:
            return 'No'

    def fourscreen(self):
        '''
            Returns 'Yes' if the rom contains fourscreen vram, returns 'No'
            if it does not.
        '''

        if ((self.rom_data[6] >> 3) & 0x1) == 1:
            return 'Yes'
        else:
            return 'No'

    def trainer(self):
        '''
            Returns 'Yes' if the rom contains a trainer, returns 'No'
            otherwise.
        '''

        if ((self.rom_data[6] >> 2) & 0x1) == 1:
            return 'Yes'
        else:
            return 'None'

    def mapper_id(self):
        '''
            Returns the rom's mapper ID as an integer.
        '''

        return (self.rom_data[6] >> 4) | ((self.rom_data[7] >> 4) << 4)

    def mapper(self):
        '''
            Returns a string describing the rom's mapper. The string contains
            the mapper's ID and human friendly name.
        '''

        mapper = nes.mappers.find(self.mapper_id())

        return '{id} ({name})'.format(id=self.mapper_id(), name=mapper['name'])

    def examples(self):
        '''
            Returns one or more comma separated game names that use the same
            mapper as this rom. Returns 'None' if there are no known examples
            or we haven't simply added any yet.
        '''

        mapper = nes.mappers.find(self.mapper_id())

        return mapper['examples']

    def mirroring(self):
        '''
            Returns the type of mirroring the rom uses. The return can either
            be 'Vertical' or 'Horizontal'.
        '''

        if (self.rom_data[6] & 0x1) == 1:
            return 'Vertical'
        else:
            return 'Horizontal'

    def header(self):
        '''
            Returns a string describing the 16 bytes of the header.
        '''

        def fmt_hex_str(string):
            '''
                A helper function to string the '0x' portion of each hex
                number off and capitalize all hex numbers.
            '''

            return hex(string).replace('0x', '').upper()

        return ' '.join([fmt_hex_str(n) for n in self.rom_data[0:16]])

    def dirty_header(self):
        '''
            Determine if bytes 7-15 are all equal to zero
        '''

        return all(byte == 0 for byte in self.rom_data[6:17])

    def contains_magic_number(self):
        '''
            Returns 'True' if the rom contains the magic .nes number,
            which is 'NES\x1a'. Returns 'False' otherwise.
        '''

        return self.rom_data[0:4] == 'NES\x1a'

    def prg_count(self):
        '''
            Returns the amount of program data pages found in the rom. To
            get the number of bytes you can multiply the prg count by
            16kb (the size of each page).
        '''

        return '{total}kb ({count} x 16kb pages)'.format(
            count=self.rom_data[4], total=self.rom_data[4] * 16
        )

    def chr_count(self):
        '''
            Returns the amount of character data pages found in the rom. To
            get the number of bytes you can multiply the chr count by
            8kb (the size of each page).
        '''

        return '{total}kb ({count} x 8kb pages)'.format(
            count=self.rom_data[5], total=self.rom_data[5] * 8
        )

    def print_analysis(self):
        '''
            Prints our complete summary of the rom to stdout.
        '''

        print(nesi_information())
        print()

        rom = fmt_str(
            'ROM',
            '{rom_name} ({rom_size} bytes, {kbytes}kb)'.format(
                rom_name=self.rom_name,
                rom_size=self.rom_size,
                kbytes=self.rom_size / 1024
            )
        )

        print(rom)

        status = fmt_str('Status', 'Does not appear to be a valid .nes rom')

        if self.contains_magic_number():
            status = fmt_str('Status', 'Appears to be a valid .nes rom')
        else:
            # Bail out, don't parse the file if it's not valid
            print(status)
            return

        print(status)

        print(fmt_str('Header', self.header()))

        notes = fmt_str('Note(s)', 'Bytes 7-15 appear clean')

        if self.dirty_header():
            notes = fmt_str('Note(s)', 'Bytes 7-15 appear to not be clean!')

        print(notes)
        print(fmt_str('PRG', self.prg_count()))
        print(fmt_str('CHR', self.chr_count()))
        print(fmt_str('Mapper', self.mapper()))
        print(fmt_str('Example(s)', self.examples()))
        print(fmt_str('Mirroring', self.mirroring()))
        print(fmt_str('Trainer', self.trainer()))
        print(fmt_str('FourScreen', self.fourscreen()))
        print(fmt_str('Battery', self.battery()))
