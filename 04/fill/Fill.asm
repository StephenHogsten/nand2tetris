// Put your code here.
	@SCREEN	// 16384
	D=A			// a = d = 16384
	@i		//16// keeps track of what bit to color
	M=D
(LOOP)
	@KBD	//24576
	D=M
	@BLACK
	D;JGT		// jump to black if there's a key being pressed
	D=0			// otherwise set color to white	- SHOULD I MAKE IT ONLY FLIP IF IT NEEDS?
(POSTCOLOR)		// at this point D should contain the color we want (0s vs 1s)
	@i
	A=M			//unsure of the ordering here - will this store the M[old_a] to new_a? (if it does we need to store color because we need D)
	M=D			// color the monitor cell
	@i
	MD=M+1		// increment which bit is next
	@KBD
	D=D-A	
	@LOOP
	D;JLT		//if D < 24576 then we keep looping - we're at the keyboard bit
	@SCREEN
	D=A
	@i
	M=D			// set back to first KBD bit
	@LOOP
	1;JMP
(BLACK)
	D=-1
	@POSTCOLOR
	0;JMP
	
// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.
// 24576 is the keyboard
// 16384 is the start of the screen
//	a screen row is 32 16-bit words 
//	pixel at row r,c is word 16384 + r*32 + c/16 bit c%16