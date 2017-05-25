// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
// A is a 16 bit register
	// @ either assigns a location to a name and assigns the address to A, or retrieve already assigned location and assigns the address to A
// D is a 16 bit register
// M is a 16-width RAM (infinite lenght?) but when we say M we mean the register at the location given by A

// Put your code here.
	@R0			// sets A to address for R0 (RAM[0])
	D=M			// stores the value from R0 / RAM[0] to D
	@temp		// name a new memory location and save it to A
	M=D			// save the value of R0 to @temp - this will count down by 1
	@product	// name a new location
	M=0			// set it to zero - this will count up by R0
(LOOP)
	@temp		// retrieve the address for the temp location
	MD=M-1		// decrement this count and save it to temp register D
	@DONE		// set A to the instruction memory location for DONE
	D;JLT		// jump to instruction location in A (DONE) if D < 0
	@R1			// store memory location R1 to A (contains one of the numbers to multiply)
	D=M		    // store value from memory location R1 to temp register D
	@product	// store memory location named 'product' to A
	M=D+M		// add the value of D to the memory location called 'product'
	@LOOP
	0;JMP		// go back to the start of the loop
(DONE)
	@product	// get the location for product (should now be complete)
	D=M			// store the value to temp location D
	@R2			// get the location for R2 and store to A
	M=D			// store the value from temp location D (has product) to location R2 (the goal of the program)
(END)
	@END		// infinite loop to "end it"
	0;JMP