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
        self.SP = 7
        self.reg[self.SP] = 0xF4

        self.functionDict = {}
        self.functionDict[0b00000001] = self.hlt
        self.functionDict[0b10000010] = self.ldi
        self.functionDict[0b01000111] = self.prn
        self.functionDict[0b10100010] = self.mul
        self.functionDict[0b01000101] = self.push
        self.functionDict[0b01000110] = self.pop
        self.functionDict[0b1010000] = self.call
        self.functionDict[0b00010001] = self.ret
        self.functionDict[0b10100000] = self.add


    def load(self):
        """Load a program into memory."""
        address = 0
        filename = sys.argv[1]

        with open(filename) as f:
            for line in f:
                line = line.split("#")[0].strip()
                if line == "":
                    continue
                else:
                    self.ram[address] = int(line, 2)
                    address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            print(f"In ALU Adding {self.reg[reg_a]} with {self.reg[reg_b]}")
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
            self.FL,
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
        self.ram[self.MAR] = self.MDR

    def run(self):
        """Run the CPU."""
        self.running = True
        
        while self.running:
            # set current instruction to the current index
            self.IR = self.ram_read(self.PC) 
            print(f'Running instruction {bin(self.IR)}')
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
        print(f"PRN {self.reg[operand_a]}")
        # increment program counter by 2
        self.PC += 2

    def mul(self):
        reg_a = self.ram_read(self.PC + 1)
        savedVal = self.reg[reg_a]
        reg_b = self.ram_read(self.PC + 2)
        self.reg[reg_a] *= self.reg[reg_b] 
        print(f"Multipled {reg_a}: {savedVal} with {reg_b}: {self.reg[reg_b]} => {self.reg[reg_a]}")
        self.PC += 3

    def push(self, value=None):
        operand_a = self.ram_read(self.PC + 1)
        print(f"operand_a: {operand_a}")
        # decrement stack pointer
        self.reg[self.SP] -= 1
        # copy value at given index
        if value == None:
            print("grabbing value")
            value = self.reg[operand_a]
        # save pointer
        pointer = self.reg[self.SP]
        # change value at that index
        print(f"PUSH: ram[pointer]: {self.ram[pointer]} is now {value}")
        self.ram_write(pointer, value)
        self.PC += 2
    def pop(self, operand_a=None):
        if operand_a == None:
            print("grabbing operand_a")
            operand_a = self.ram_read(self.PC + 1)
        # copy value at given index/pointer
        value = self.ram_read(self.reg[self.SP])
        # change value to given index
        print(f"POP: reg[op_a]: {self.reg[operand_a]} is now {value}")
        self.reg[operand_a] = value
        # increment stack pointer and PC
        self.reg[self.SP] += 1
        self.PC += 2

    def call(self):
        operand_a = self.ram_read(self.PC + 1)
        # push next instruction to have later
        nextInstr = self.ram_read(self.PC + 2)
        print(f"Saving next instruction {bin(nextInstr)}")
        self.push(nextInstr)
        # set PC to address stored in given reg
        print(f"Moving PC to {self.reg[operand_a]}")
        self.PC = (self.reg[operand_a])

    def ret(self):
        print(f"RET: Grabbing instruction")
        self.PC = self.pop(self.reg[self.SP])
        print(f"PC: {self.PC}")

    def add(self):
        operand_a = self.ram_read(self.PC + 1)
        operand_b = self.ram_read(self.PC + 2)
        self.alu("ADD", operand_a, operand_b)
        self.PC += 3