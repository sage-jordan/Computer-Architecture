"""CPU functionality."""
## CPU class with memory, registers, and PC counter. Has methods to load a memory, call our alu to run operations, and trace which will help us debug. I will implement run()
import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.PC = 0 # program counter
        self.IR = None # current instruction
        self.FL = None # flags
        # others
        self.ram = [None] * 256 # ram
        self.reg = [0] * 8 # registers
        self.running = False 
        # stack pointer is reg[7]
        self.reg[7] = 0xF4
        # * R5 is reserved as the interrupt mask (IM)
        # * R6 is reserved as the interrupt status (IS)
        # * R7 is reserved as the stack pointer (SP)

        self.functionDict = {}
        self.functionDict[0b00000001] = self.hlt
        self.functionDict[0b10000010] = self.ldi
        self.functionDict[0b01000111] = self.prn
        self.functionDict[0b10100010] = self.mul
        self.functionDict[0b01000101] = self.push
        self.functionDict[0b01000110] = self.pop
        self.functionDict[0b1010000] = self.call
        self.functionDict[0b00010001] = self.ret
        self.functionDict[0b10100000] = "ADD"
        self.functionDict[0b10100111] = "CMP"
        self.functionDict[0b01010101] = self.jeq
        self.functionDict[0b01010110] = self.jne
        self.functionDict[0b01010100] = self.jmp

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
        op = self.functionDict[op]
        if op == "ADD":
            print(f"In ALU Adding {self.reg[reg_a]} with {self.reg[reg_b]}")
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "CMP":
            print("Running CMP")
            val1 = self.reg[reg_a]
            val2 = self.reg[reg_b]
            if val1 == val2:
                self.FL = 0b1
            elif val1 > val2:
                self.FL = 0b10
            elif val2 > val1:
                self.FL = 0b100
            print("CMP done")
            self.PC += 3
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

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def run(self):
        """Run the CPU."""
        self.running = True
        
        while self.running:
            # set current instruction to the current index
            self.IR = self.ram_read(self.PC) 
            # grab operands
            operand_a = self.ram_read(self.PC + 1)
            operand_b = self.ram_read(self.PC + 2)
            print(f'Running instruction {bin(self.IR)}')
            # checks if this is an ALU command
            is_alu_command = (self.IR >> 5) & 0b001
            if is_alu_command:
                print("running ALU")
                self.alu(self.IR, operand_a, operand_b)
            # call function for this instruction
            else:
                print("running func")
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
        print(f"\nPRN====== {self.reg[operand_a]}\n")
        # increment program counter by 2
        self.PC += 2

    def mul(self):
        # get operands
        operand_a = self.ram_read(self.PC + 1)
        operand_b = self.ram_read(self.PC + 2)
        # saved prev value to print
        savedVal = self.reg[operand_a]
        # multiply and store in first operand's memory
        self.reg[operand_a] *= self.reg[operand_b] 
        print(f"Multipled {operand_a}: {savedVal} with {operand_b}: {self.reg[operand_b]} => {self.reg[operand_a]}")
        # increment 3
        self.PC += 3

    def push(self):
        # grab operand
        operand_a = self.ram_read(self.PC + 1)
        # decrement stack pointer
        self.reg[7] -= 1
        # copy value at given index
        value = self.reg[operand_a]
        # save stack pointer
        SP = self.reg[7]
        # change value at that index
        print(f"PUSH: ram[SP]: {self.ram[SP]} is now {value}")
        self.ram[SP] = value
        # increment by 2
        self.PC += 2

    def pop(self):
        # get operand (given register to pop to)
        operand_a = self.ram_read(self.PC + 1)
        # get stack pointer
        SP = self.reg[7]
        # copy value we want
        value = self.ram_read(SP)
        # copy value to given register index
        print(f"POP: reg[op_a]: {self.reg[operand_a]} is now {value}")
        self.reg[operand_a] = value
        # increment stack pointer and PC
        self.reg[7] += 1
        self.PC += 2

    def call(self):
        operand_a = self.ram_read(self.PC + 1)
        # push next instruction to have later
        nextInstr = self.PC + 2
        print(f"Saving next instruction index {nextInstr}")
        # manual push (decrement, save pointer, change val)
        self.reg[7] -= 1
        SP = self.reg[7]
        self.ram[SP] = nextInstr
        # set PC to address stored in given reg
        print(f"Moving PC to {self.reg[operand_a]}")
        self.PC = self.reg[operand_a]

    def ret(self):
        print(f"RET: Grabbing instruction")
        SP = self.reg[7]
        value = self.ram_read(SP)
        print(f'Setting PC to {value}')
        self.PC = value

    def jeq(self):
        operand_a = self.ram_read(self.PC + 1)
        is_equal = self.FL & 1
        if is_equal:
            print(f"JEQ Jumping to {self.reg[operand_a]}")
            self.PC = self.reg[operand_a]
        else: 
            self.PC += 2

    def jne(self):
        operand_a = self.ram_read(self.PC + 1)
        if self.FL & 1 is 0:
            print(f"JNE Jumping to {self.reg[operand_a]}")
            self.PC = self.reg[operand_a]
        else: 
            self.PC += 2

    def jmp(self):
        operand_a = self.ram_read(self.PC + 1)
        print(f"JMP Jumping to {self.reg[operand_a]}")
        self.PC = self.reg[operand_a]