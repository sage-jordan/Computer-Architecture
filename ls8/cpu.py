"""CPU functionality."""
## CPU class with memory, registers, and PC counter. Has methods to load a memory, call our alu to run operations, and trace which will help us debug. I will implement run()
import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # internal registers
        self.PC = 0 # program counter
        self.IR = None # instruction register (current instruction)
        self.FL = None # flags
        self.MAR = None # memory address register 
        self.MDR = None # memory data register
        # others
        self.ram = [None] * 256 # ram
        self.reg = [0] * 8 # registers
        self.running = False 
        # stack pointer
        self.sp = 7

        self.functionDict = {}
        self.functionDict[0b00000001] = self.hlt
        self.functionDict[0b10000010] = self.ldi
        self.functionDict[0b01000111] = self.prn


    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        program = [
            # From print8.ls8
            0b10000010, # LDI R0,8
            0b00000000,
            0b00001000,
            0b01000111, # PRN R0
            0b00000000,
            0b00000001, # HLT
        ]

        for instruction in program:
            self.ram[address] = instruction
            address += 1


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
            self.PC,
            #self.fl,
            #self.ie,
            self.ram_read(self.PC),
            self.ram_read(self.PC + 1),
            self.ram_read(self.PC + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, address):
        self.MAR = address
        self.MDR = self.ram[self.MAR]
        return self.MDR

    def ram_write(self, address, value):
        self.MAR = address
        self.MDR = value
        self.ram[MAR] = self.MDR

    def run(self):
        """Run the CPU."""
        self.running = True
        
        while self.running:
            # set current instruction to the current index
            self.IR = self.ram_read(self.PC) 
            print(f'Running instruction {self.IR}')
            # call function for this instruction
            self.functionDict[self.IR]()

    def hlt(self):
        print("Halting..")
        self.running = False

    def ldi(self):
        # get operands
        operand_a = self.ram_read(self.PC + 1)
        operand_b = self.ram_read(self.PC + 2)
        # load to register
        print(f"LDI: reg[{operand_a}] = {operand_b}")
        self.reg[operand_a] = operand_b
        # increment
        self.PC += 3

    def prn(self):
        # get operand
        operand_a = self.ram_read(self.PC+1)
        # print the value
        print(self.reg[operand_a])
        # increment program counter by 2
        self.PC += 2