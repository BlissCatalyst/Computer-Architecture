"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0
        self.mar = 0
        self.mdr = 0
        self.fl = 0
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[7] = 0xF4
        self.running = True
        self.branchtable = {}
        self.branchtable[HLT] = self.handle_HLT
        self.branchtable[LDI] = self.handle_LDI
        self.branchtable[PRN] = self.handle_PRN
        self.branchtable[MUL] = self.handle_MUL

    def handle_HLT(self, operand_a, operand_b):
        self.running = False

    def handle_LDI(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b

    def handle_PRN(self, operand_a, operand_b):
        prn_value = self.reg[operand_a]
        print(f"REGISTER: {operand_a}, VALUE: {prn_value}")

    def handle_MUL(self, operand_a, operand_b):
        self.alu("MUL", operand_a, operand_b)

    def load(self):
        """Load a program into memory."""

        with open(sys.argv[1]) as f:
            address = 0

            for line in f:
                comment_split = line.split("#")

                num = comment_split[0].strip()

                try:
                    self.ram[address] = int(num, 2)
                    address += 1
                except ValueError:
                    pass
        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def pc_advance(self, ir):
        flag_select = ir
        flag_select = flag_select >> 6
        if flag_select == 0b01:
            self.pc += 2
        elif flag_select == 0b10:
            self.pc += 3
        elif flag_select == 0b00:
            self.pc += 1

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        while self.running:
            ir = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            self.branchtable[ir](operand_a, operand_b)

            self.pc_advance(ir)
