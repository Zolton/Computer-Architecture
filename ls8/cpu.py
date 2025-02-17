"""CPU functionality."""

import sys
import re
#print(sys.argv[1])
# sys.argv[0] = file to run
# sys.argv[1] = file to take instructions from

# sys.exit()
filename = sys.argv[1]


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.pc = 0
        self.ram = [0] * 256
        self.equalFlag = 0
        self.greaterFlag = 0
        self.LesserFlag = 0
        

    def load(self):
        """Load a program into memory."""

        address = 0
        # Run thru given file name, line by line
        with open(filename) as f:
            for line in f:
                # Matches first 8 digits, numbers only
                regex = re.compile('([0-9]){8}')
                # Stores variables as class object
                match = regex.match(line)
                # Needed for blank lines, which Python Regex treats as NoneType
                if match:
                    # Converts class object to strings
                    match = match.group()
                    # print("Match found: ", match)
                    # Insert into RAM as an int, base 2/binary
                    self.ram[address] = int(match, 2)
                    address += 1
        #print("address is: ", address  
        self.reg[7] = address
    def ram_write(self, regLocation, value):
        self.reg[regLocation] = value
        #self.pc += 3

    def ram_read(self, regLocation):
        return self.reg[regLocation]
        # Can advance self.pc here or in run, but not both!
        #self.pc += 2
    
    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()
    


    def run(self):
        LDI = 0b10000010
        PRN = 0b01000111
        HLT = 0b00000001 
        MUL = 0b10100010
        PUSH = 0b01000101
        POP = 0b01000110
        CALL = 0b01010000
        RET = 0b00010001
        ADD = 0b10100000
        JMP = 0b01010100
        CMP = 0b10100111
        JEQ = 0b01010101
        JNE = 0b01010110
        """Run the CPU."""
        # Load the program
        self.load()
        # From ram, read instructions
        halted = True
        while halted is True:
            # Go thru RAM and read instructions
            instructions = self.ram[self.pc]
            if instructions == LDI:
                # At this reg location, insert this value
                reg_num = self.ram[self.pc + 1]
                value = self.ram[self.pc + 2]
                self.reg[reg_num] = value
                self.pc += 3
            elif instructions == PRN:
                # At this reg location, read the value
                reg_num = self.ram[self.pc + 1]
                print(self.reg[reg_num])
                self.pc += 2
            elif instructions == MUL:
                # Look at these two reg locations
                a = self.ram[self.pc + 1]
                b = self.ram[self.pc + 2]
                # Read the values at those locations and multiply
                valueOne = self.reg[a]
                valueTwo = self.reg[b]
                c = valueOne * valueTwo
                # Write the solution into a's former location
                self.reg[a] = c
                self.pc += 3
            elif instructions ==  ADD:
                # Look at these two reg locations
                a = self.ram[self.pc + 1]
                b = self.ram[self.pc + 2]
                # Read the values at those locations and multiply
                valueOne = self.reg[a]
                valueTwo = self.reg[b]
                c = valueOne + valueTwo
                # Write the solution into a's former location
                self.reg[a] = c
                self.pc += 3
            elif instructions == PUSH:
                # Where to look in registry for value
                reg_num = self.ram[self.pc + 1]
                # Value pulled from registry
                value = self.reg[reg_num]
                # Known empty spot in RAM to store value
                    # My regex loop ends up with address & self.reg[7] being an empty slot
                # current_sp = index of empty spot in RAM
                current_sp = self.reg[7]
                # Store value in empty spot in RAM
                self.ram[current_sp] = value
                # Change pointer to next empty spot in RAM
                self.reg[7] += 1
                self.pc += 2
            
            elif instructions == POP:
                # Change pointer to first filled spot in RAM
                self.reg[7] -= 1
                # Fetch the index of where in RAM to look at
                current_sp = self.reg[7]
                # Fetch current value from top of stack/location in RAM
                value = self.ram[current_sp]
                # Find out where in registry value is to be saved
                reg_num = self.ram[self.pc + 1]
                # Store value in registry
                self.reg[reg_num] = value
                # No need to change self.reg - it's been popped, so current_sp is considered empty now
                self.pc += 2
            
            elif instructions == CALL:

                # BEWARE - CALL can set the return_address itself, may need an if-statement to check for it

                # Save address in pc of where to go after CALL is done
                return_address = self.pc + 2
                # current_sp = index of known empty spot in RAM
                current_sp = self.reg[7]
                # Store return address in empty spot in RAM
                self.ram[current_sp] = return_address
                # Change pointer to next empty spot in RAM for next PUSH
                self.reg[7] += 1
                # Tell CALL where to look in RAM for instructions
                location = self.ram[self.pc + 1]
                # Fetch from registry the location of the subroutine
                subroutine = self.reg[location]
                # Jump to subroutine
                self.pc = subroutine
            
            elif instructions == RET:
                # Change pointer to first filled spot in RAM
                self.reg[7] -= 1
                # Fetch the index of where in RAM to look at
                current_sp = self.reg[7]
                # Fetch current value from top of stack/location in RAM
                # Value is known to be location of next instructions
                value = self.ram[current_sp]
                # Jump to next location for instructions to resume program
                self.pc = value
            
            elif instructions == JMP:
                # See where to look in reg
                value = self.ram[self.pc + 1]
                # Go here in registry to retrieve an address
                location = self.reg[value]
                # Jump to the location given
                self.pc = location
            
            elif instructions == CMP:
                # Where to look in registry
                locationOne = self.ram[self.pc + 1]
                locationTwo = self.ram[self.pc + 2]
                # Values to be compared
                valueOne = self.reg[locationOne]
                valueTwo = self.reg[locationTwo]
                # Decision tree
                if valueOne == valueTwo:
                    self.equalFlag = 1
                if valueOne > valueTwo:
                    self.greaterFlag = 1
                if valueOne < valueTwo:
                    self.LesserFlag = 1
                # Regardless of what the flags are set to, continue in the program
                self.pc += 3
            
            elif instructions == JEQ:
                if self.equalFlag == 1:
                    # Find where to look in registry
                    reg_num = self.ram[self.pc + 1]
                    # Retrieve value from registry
                    location = self.reg[reg_num]
                    # Jump
                    self.pc = location
                else:
                    # If not, continue on with program
                    self.pc += 2
            
            elif instructions == JNE:
                if self.equalFlag == 0:
                    # Find where to look in registry
                    reg_num = self.ram[self.pc + 1]
                    # Retrieve value from registry
                    location = self.reg[reg_num]
                    # Jump
                    self.pc = location
                else:
                    # If not, continue on with program
                    self.pc += 2

            elif instructions == HLT:
                halted = False
                self.pc += 1
            else: 
                print(f"Unknown command at {self.pc}", "Command give: ", self.reg[self.pc])
                sys.exit(1)


