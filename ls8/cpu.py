"""CPU functionality."""
## CPU class with memory, registers, and pc counter. Has methods to load a memory, call our alu to run operations, and trace which will help us debug. I will implement run()
import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.memory = [0] * 256
        self.registers = [None] * 8
        self.pc = 0
        self.running = False

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

    def ram_read(self, MAR):
        if MAR in self.registers:
            return self.registers[MAR]
        else:
            return self.memory[MAR]

    def ram_write(self, MAR, MDR):
        if MAR > len(self.memory):
            return Exception("Not enough space")
        elif self.memory[MAR] != 0:
            print("Overwriting entry..")
            self.memory[MAR] = MDR
        else:
            self.memory[MAR] = MDR   

    def run(self):
        """Run the CPU."""
        instructionRegister = 0
        self.running = True
        
        while self.running:
            operand_a = ram_read(self.pc + 1)
            operand_b = ram_read(self.pc + 2)
            if self.memory[self.pc] == 
