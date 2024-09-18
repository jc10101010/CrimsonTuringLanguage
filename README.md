# TuringLang - A Programming Language for Turing Machines

TuringLang is a specialized programming language that compiles to Turing machine states. Written in Python, the TuringLang compiler helps build complex Turing machines by simplifying the process of constructing the machine's transition states. This language allows for defining arithmetic operations like addition, and it can be extended to more complex mathematical expressions such as multiplication, division, and subtraction.

TuringLang is designed with platform independence in mind. A program written in TuringLang can be executed on any Turing-complete device, making it truly universal. This README provides an overview of the language, the types of tasks you can achieve with it, and how to write and execute your own programs.

---

## Key Features
- **Universal Computation**: Programs are platform-independent and can run on any Turing-complete system.
- **Binary Representation**: Instructions and numbers are represented in binary on the tape, with specific markers for easier parsing by the Turing machine.
- **Tree Structure Execution**: Allows nested instructions to be processed, enabling complex arithmetic computations.
- **Extensibility**: TuringLang can be expanded to support custom operators.

---

## Why Use TuringLang?

TuringLang addresses several key challenges that arise when programming a Turing machine for non-trivial tasks:

- **No Memory Between States**: Turing machines have no inherent state memory, making it difficult to handle operations like nested arithmetic. TuringLang introduces a tree-based structure to handle such tasks.
- **Complex Detection**: Instructions are represented by binary numbers longer than 16 bits to avoid confusion with regular data. This requires the machine to frequently detect sequences of bits, which is streamlined in TuringLang.

---

## How TuringLang Works

TuringLang simplifies Turing machine programming by providing constructs that translate into complex state transitions. Below are the key concepts and commands in TuringLang:

### Instructions
- **Numbers**: Represented in binary format between `BINARY_START` and `BINARY_END`.
  ```plaintext
  BINARY_START 233 BINARY_END
  ```

- **Commands**: Instructions on the tape follow a tree-root structure, enabling nested operations.
  ```plaintext
  TREE_ROOT ARITHMETIC_UNIT ADDITION 4 5
  ```

### Core Commands

- **`detect`**: Finds a specific sequence on the tape.
  ```plaintext
  <start_state> detect <sequence_to_find> <direction=L/R> <next_state>
  ```

- **`sdetect`**: A variant of `detect` that does not stop at `TREE_ROOT`.
  ```plaintext
  <start_state> sdetect <sequence_to_find> <direction=L/R> <next_state>
  ```

- **`define`**: Assigns names to complex binary values, making code more readable.
  ```plaintext
  define <constant_name> <binary_value>
  ```

- **`skip`**: Moves the pointer a certain number of steps without detecting `TREE_ROOT`.
  ```plaintext
  <start_state> skip <number_of_steps> <direction=L/R> <next_state>
  ```

- **`out`**: Writes a binary sequence to the tape.
  ```plaintext
  <start_state> out <binary_sequence> <direction=L/R> <next_state>
  ```

- **`include`**: Includes code from another file.
  ```plaintext
  include <filename>
  ```

- **Turing Machine State**: Standard Turing machine state definition.
  ```plaintext
  <start_state> 1 <write_if_1> <move_if_1=L/R> <next_state_if_1> 0 <write_if_0> <move_if_0=L/R> <next_state_if_0>
  ```

---

### TuringLang Example: Adding Two Numbers
```plaintext
TuringArithmeticAdd 1 1 L AddOneToLeft.1    0 0 L AddOneToLeft.1

AddOneToLeft.1 detect bs R AddOneToLeft.2
AddOneToLeft.2 skip 15 R AddOneToLeft.3.1
AddOneToLeft.3.1 1 0 L AddOneToLeft.3.2       0 1 L nextStep.1
AddOneToLeft.3.2 1 0 L AddOneToLeft.3.3       0 1 L nextStep.1
...
AddOneToLeft.3.16 1 0 L STOP       0 1 L nextStep.1
```

---

## How to Run TuringLang

To compile and run a TuringLang program, use the `PythonTuringClasses.py` file. The program takes two inputs: the file containing TuringLang code and the initial tape.

### Example Command:
```bash
python PythonTuringClasses.py TuringText.txt <tape_input>
```

### Example Tape Input:
```plaintext
00000011111111111111111001111111111111111110101001111111111111111111100000010011000110011111111111111111111100111111111111111111010100111111111111111111110000000010001110001111111111111111111110011111111111111111111000000010011110010111111111111111111111001111111111111111111001111111111111111111001111111111111111111111000000
```

---

## Extendability: What's Next?

This project can be extended to perform more complex tasks:
- **Multiplication, Division, Subtraction**: By implementing programs for these operations, you can build complex arithmetic expressions like:
  ```plaintext
  12 * (2 / (2 - (3 + 23)))
  ```
- **Storage and Loops**: Complex loops and multiple data type variable storage can be implemented.

