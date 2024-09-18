import time
import sys

# Get the filename and tape content from command-line arguments
FILE_NAME = sys.argv[1]
TAPE = sys.argv[2]

def readStateFile(filename, defineDict):
        # Initialize list of states and open the file
        states = []
        file = open(filename, "r")
        for i in file.readlines():
            # Split the line into components and replace defined constants with actual values
            line = i.strip().split()
            for wordI in range(len(line)):
                if line[wordI] in list(defineDict.keys()):
                    line[wordI] = defineDict[line[wordI]]
            # Skip empty lines
            if line == []:
                pass
            # Handle 'define' to add definitions to the dictionary
            elif line[0] == "define":
                defineDict[line[1]] = line[2]
            # Handle 'include' to include another file and combine its states and definitions
            elif line[0] == "include":
                fileOut = readStateFile(line[1], defineDict)
                states = states + fileOut[0]
                defineDict = {**defineDict, **fileOut[1]}
            # Handle 'skip' command to move the tape head by multiple steps
            elif line[1] == "skip":
                if line[3] == "R":
                    n = int(line[2])
                    placeholder = line[0]
                    skipLines = []
                    for i in range(n):
                        skipLine = ( placeholder + ".SKIP." + str(i) + " 1 1 R  " + placeholder + ".SKIP." + str(i+1) + " 0 0 R " + placeholder + ".SKIP." + str(i+1)).strip().split()
                        if i == 0:
                            skipLine[0] = line[0]
                        if i + 1 == n:
                            skipLine[4] = line[4]
                            skipLine[8] = line[4]
                        skipLines.append(skipLine)
                    states = states + skipLines
                elif line[3] == "L":
                    # Similar logic for moving left
                    n = int(line[2])
                    placeholder = line[0]
                    skipLines = []
                    for i in range(n):
                        skipLine = ( placeholder + ".SKIP." + str(i) + " 1 1 L  " + placeholder + ".SKIP." + str(i+1) + " 0 0 L " + placeholder + ".SKIP." + str(i+1)).strip().split()
                        if i == 0:
                            skipLine[0] = line[0]
                        if i + 1 == n:
                            skipLine[4] = line[4]
                            skipLine[8] = line[4]
                        skipLines.append(skipLine)
                    states = states + skipLines
            # Handle 'detect' to search for a specific sequence on the tape
            elif line[1] == "detect":
                if line[3] == "R":
                    searchstring = line[2]
                    comparisonstring = "01111111111111111110"
                    end = False
                    index = 0
                    # Find the index where the sequences differ
                    while not end:
                        if index == len(searchstring) - 1 or index == len(comparisonstring) - 1:
                            end = True
                        if searchstring[index] != comparisonstring[index]:
                            end = True
                        index += 1
                    index -= 1
                    nme = line[0]
                    s = []
                    # Add in-place state when the pointer doesn't move
                    s += [("InPlace" + nme + " 0 0 L " + nme  + " 1 1 L " + nme ).split()]
                    ending = ""
                    for i in range(index):
                        # Generate states that match the sequence step by step
                        nc = comparisonstring[i] 
                        onc = str(1 - int(nc))
                        if i == 0:
                            currentLine =  nme + " "
                        else:
                            currentLine =  nme + ending + "_ "
                        currentLine +=  nc + " " +  nc + " R " + nme + ending + nc + "_ "
                        if i != 0:
                            currentLine +=  onc + " " +  onc + " R " + "InPlace" + nme
                        else:
                            currentLine +=  onc + " " +  onc + " R " + nme  
                        s += [currentLine.split()]
                        ending += nc
                    
                    # Handle cases where there is a partial match for both sequences
                    if index != len(searchstring) - 1 and index != len(comparisonstring) - 1:
                        searchChar = searchstring[index]
                        comparisonChar = comparisonstring[index]
                        currentLine = nme + ending + "_ "
                        currentLine += searchChar + " " + searchChar + " R " + nme + ending + searchChar + "_ "
                        currentLine += comparisonChar + " " + comparisonChar + " R " + nme + ending + comparisonChar + "_ "
                        s += [currentLine.split()]

                        otherending = ending
                        ending += comparisonChar
                        for i in range(index + 1, len(comparisonstring) - 1):
                            nc = comparisonstring[i] 
                            onc = str(1 - int(nc))
                            currentLine =  nme + ending + "_ "
                            currentLine +=  nc + " " +  nc + " R " + nme + ending + nc + "_ "
                            currentLine +=  onc + " " +  onc + " R " + "InPlace" + nme
                            s += [currentLine.split()]
                            ending += nc
                        # Handle the last character
                        i = len(comparisonstring) - 1
                        nc = comparisonstring[i] 
                        onc = str(1 - int(nc))
                        currentLine =  nme + ending + "_ "
                        currentLine +=  nc + " " +  nc + " R " + "InPlaceHub "
                        currentLine +=  onc + " " +  onc + " R " + "InPlace" + nme
                        s += [currentLine.split()]

                        # Handle cases for the search string if not fully matched
                        otherending += searchChar
                        for i in range(index + 1, len(searchstring) - 1):
                            nc = searchstring[i] 
                            onc = str(1 - int(nc))
                            currentLine =  nme + otherending + "_ "
                            currentLine +=  nc + " " +  nc + " R " + nme + otherending + nc + "_ "
                            currentLine +=  onc + " " +  onc + " R " + "InPlace" + nme
                            s += [currentLine.split()]
                            otherending += nc
                        # Handle the last character
                        i = len(searchstring) - 1
                        nc = searchstring[i] 
                        onc = str(1 - int(nc))
                        currentLine =  nme + otherending + "_ "
                        currentLine +=  nc + " " +  nc + " R " + line[4] + " "
                        currentLine +=  onc + " " +  onc + " R " + "InPlace" + nme
                        s += [currentLine.split()]

                    # Handle full match of both sequences
                    elif index == len(searchstring) - 1 and index == len(comparisonstring) - 1 :
                        searchChar = searchstring[index]
                        comparisonChar = comparisonstring[index]
                        currentLine = nme + ending + "_"
                        currentLine += searchChar + " " + searchChar + " R " + line[4] + " "
                        currentLine += comparisonChar + " " + comparisonChar + " R InPlaceHub"
                        s += [currentLine.split()]
                        return s
                    # Handle full match of search string
                    elif index == len(searchstring) - 1:
                        searchChar = searchstring[index]
                        comparisonChar = comparisonstring[index]
                        currentLine = nme + ending + "_ "
                        currentLine += searchChar + " " + searchChar + " R " + line[4] + " "
                        currentLine += comparisonChar + " " + comparisonChar + " R " + nme + ending + comparisonChar + "_ "
                        s += [currentLine.split()]

                        ending += comparisonChar
                        for i in range(index + 1, len(comparisonstring) - 1):
                            nc = comparisonstring[i] 
                            onc = str(1 - int(nc))
                            currentLine =  nme + ending + "_ "
                            currentLine +=  nc + " " +  nc + " R " + nme + ending + nc + "_ "
                            currentLine +=  onc + " " +  onc + " R " + "InPlace" + nme
                            s += [currentLine.split()]
                            ending += nc
                        # Handle the last character
                        i = len(comparisonstring) - 1
                        nc = comparisonstring[i] 
                        onc = str(1 - int(nc))
                        currentLine =  nme + ending + "_ "
                        currentLine +=  nc + " " +  nc + " R " + line[4] + " "
                        currentLine +=  onc + " " +  onc + " R " + "InPlace" + nme
                        s += [currentLine.split()]
                    
                    # Handle full match of comparison string
                    elif index == len(comparisonstring) - 1 :
                        searchChar = searchstring[index]
                        comparisonChar = comparisonstring[index]
                        currentLine = nme + ending + "_ "
                        currentLine += searchChar + " " + searchChar + " R " + nme + ending + searchChar + "_ "
                        currentLine += comparisonChar + " " + comparisonChar + " R InPlaceHub "
                        s += [currentLine.split()]

                        ending += searchChar
                        for i in range(index + 1, len(searchstring) - 1):
                            nc = searchstring[i] 
                            onc = str(1 - int(nc))
                            currentLine =  nme + ending + "_ "
                            currentLine +=  nc + " " +  nc + " R " + nme + ending + nc + "_ "
                            currentLine +=  onc + " " +  onc + " R " + "InPlace" + nme
                            s += [currentLine.split()]
                            ending += nc
                        # Handle the last character
                        i = len(searchstring) - 1
                        nc = searchstring[i] 
                        onc = str(1 - int(nc))
                        currentLine =  nme + ending + "_ "
                        currentLine +=  nc + " " +  nc + " R " + line[4] + " "
                        currentLine +=  onc + " " +  onc + " R " + "InPlace" + nme
                        s += [currentLine.split()]
                    states += s
                # Handle 'detect' command for leftward detection (similar logic to rightward)
                elif line[3] == "L":
                    searchstring = line[2]
                    comparisonstring = "01111111111111111110"
                    end = False
                    index = 0
                    while not end:
                        if index == len(searchstring) - 1 or index == len(comparisonstring) - 1:
                            end = True
                        if searchstring[index] != comparisonstring[index]:
                            end = True
                        index += 1
                    index -= 1
                    nme = line[0]
                    s = []
                    s += [("InPlace" + nme + " 0 0 R " + nme + " 1 1 R " + nme ).split()]
                    ending = ""
                    for i in range(index):
                        # Generate states for matching sequence step by step
                        nc = comparisonstring[i] 
                        onc = str(1 - int(nc))
                        if i == 0:
                            currentLine =  nme + " "
                        else:
                            currentLine =  nme + ending + "_ "
                        currentLine +=  nc + " " +  nc + " L " + nme + ending + nc + "_ "
                        if i != 0:
                            currentLine +=  onc + " " +  onc + " L " + "InPlace" + nme
                        else:
                            currentLine +=  onc + " " +  onc + " L " + nme  
                        s += [currentLine.split()]
                        ending += nc
                    
                    # Handle different cases based on mismatch points between search and comparison strings
                    if index != len(searchstring) - 1 and index != len(comparisonstring) - 1:
                        searchChar = searchstring[index]
                        comparisonChar = comparisonstring[index]
                        currentLine = nme + ending + "_ "
                        currentLine += searchChar + " " + searchChar + " L " + nme + ending + searchChar + "_ "
                        currentLine += comparisonChar + " " + comparisonChar + " L " + nme + ending + comparisonChar + "_ "
                        s += [currentLine.split()]

                        otherending = ending
                        ending += comparisonChar
                        for i in range(index + 1, len(comparisonstring) - 1):
                            nc = comparisonstring[i] 
                            onc = str(1 - int(nc))
                            currentLine =  nme + ending + "_ "
                            currentLine +=  nc + " " +  nc + " L " + nme + ending + nc + "_ "
                            currentLine +=  onc + " " +  onc + " L " + "InPlace" + nme
                            s += [currentLine.split()]
                            ending += nc
                        # Handle the last character
                        i = len(comparisonstring) - 1
                        nc = comparisonstring[i] 
                        onc = str(1 - int(nc))
                        currentLine =  nme + ending + "_ "
                        currentLine +=  nc + " " +  nc + " L " + " InPlaceHub "
                        currentLine +=  onc + " " +  onc + " L " + "InPlace" + nme
                        s += [currentLine.split()]

                        otherending += searchChar
                        for i in range(index + 1, len(searchstring) - 1):
                            nc = searchstring[i] 
                            onc = str(1 - int(nc))
                            currentLine =  nme + otherending + "_ "
                            currentLine +=  nc + " " +  nc + " L " + nme + otherending + nc + "_ "
                            currentLine +=  onc + " " +  onc + " L " + "InPlace" + nme
                            s += [currentLine.split()]
                            otherending += nc
                        # Handle the last character of search string
                        i = len(searchstring) - 1
                        nc = searchstring[i] 
                        onc = str(1 - int(nc))
                        currentLine =  nme + otherending + "_ "
                        currentLine +=  nc + " " +  nc + " L " + line[4] + " "
                        currentLine +=  onc + " " +  onc + " L " + "InPlace" + nme
                        s += [currentLine.split()]

                    # Full match of both strings
                    elif index == len(searchstring) - 1 and index == len(comparisonstring) - 1 :
                        searchChar = searchstring[index]
                        comparisonChar = comparisonstring[index]
                        currentLine = nme + ending + "_ "
                        currentLine += searchChar + " " + searchChar + " L " + line[4] + " "
                        currentLine += comparisonChar + " " + comparisonChar + " L InPlaceHub"
                        s += [currentLine.split()]

                        return s
                    # Full match of search string only
                    elif index == len(searchstring) - 1:
                        searchChar = searchstring[index]
                        comparisonChar = comparisonstring[index]
                        currentLine = nme + ending + "_ "
                        currentLine += searchChar + " " + searchChar + " L " + line[4] + " "
                        currentLine += comparisonChar + " " + comparisonChar + " L " + nme + ending + comparisonChar + "_ "
                        s += [currentLine.split()]

                        ending += comparisonChar
                        for i in range(index + 1, len(comparisonstring) - 1):
                            nc = comparisonstring[i] 
                            onc = str(1 - int(nc))
                            currentLine =  nme + ending + "_ "
                            currentLine +=  nc + " " +  nc + " L " + nme + ending + nc + "_ "
                            currentLine +=  onc + " " +  onc + " L " + "InPlace" + nme
                            s += [currentLine.split()]
                            ending += nc
                        # Handle the last character
                        i = len(comparisonstring) - 1
                        nc = comparisonstring[i] 
                        onc = str(1 - int(nc))
                        currentLine =  nme + ending + "_ "
                        currentLine +=  nc + " " +  nc + " L " + line[4] + " "
                        currentLine +=  onc + " " +  onc + " L " + "InPlace" + nme
                        s += [currentLine.split()]
                    
                    # Full match of comparison string only
                    elif index == len(comparisonstring) - 1 :
                        searchChar = searchstring[index]
                        comparisonChar = comparisonstring[index]
                        currentLine = nme + ending + "_ "
                        currentLine += searchChar + " " + searchChar + " L " + nme + ending + searchChar + "_ "
                        currentLine += comparisonChar + " " + comparisonChar + " L InPlaceHub"
                        s += [currentLine.split()]

                        ending += searchChar
                        for i in range(index + 1, len(searchstring) - 1):
                            nc = searchstring[i] 
                            onc = str(1 - int(nc))
                            currentLine =  nme + ending + "_ "
                            currentLine +=  nc + " " +  nc + " L " + nme + ending + nc + "_ "
                            currentLine +=  onc + " " +  onc + " L " + "InPlace" + nme
                            s += [currentLine.split()]
                            ending += nc
                        # Handle the last character of search string
                        i = len(searchstring) - 1
                        nc = searchstring[i] 
                        onc = str(1 - int(nc))
                        currentLine =  nme + ending + "_ "
                        currentLine +=  nc + " " +  nc + " L " + line[4] + " "
                        currentLine +=  onc + " " +  onc + " L " + "InPlace" + nme
                        s += [currentLine.split()]

                    states += s
            # Handle 'sdetect' command (like detect, but ignores TREE_ROOT)
            elif line[1] == "sdetect":
                if line[3] == "R":
                    nme = line[0]
                    searchword = line[2]
                    s = []
                    s += [("InPlace" + nme + " 0 0 L " + nme  + " 1 1 L " + nme ).split()]
                    ending = ""
                    for i in range(len(searchword)):
                        nc = searchword[i] 
                        onc = str(1 - int(nc))
                        if i == 0:
                            currentLine =  nme + " "
                            currentLine +=  nc + " " +  nc + " R " + nme + ending + nc + "_ "
                            currentLine +=  onc + " " +  onc + " R " + nme
                        elif i == len(searchword)-1:
                            currentLine =  nme + ending + "_ "
                            currentLine +=  nc + " " +  nc + " R " + line[4] + " "
                            currentLine +=  onc + " " +  onc + " R " + "InPlace" + nme
                        else:
                            currentLine =  nme + ending + "_ "
                            currentLine +=  nc + " " +  nc + " R " + nme + ending + nc + "_ "
                            currentLine +=  onc + " " +  onc + " R " + "InPlace" + nme
                        s += [currentLine.split()]
                        ending += nc
                    states += s
                elif line[3] == "L":
                    # Same logic for sdetect moving left
                    nme = line[0]
                    searchword = line[2]
                    s = []
                    s += [("InPlace" + nme + " 0 0 R " + nme  + " 1 1 R " + nme ).split()]
                    ending = ""
                    for i in range(len(searchword)):
                        nc = searchword[i] 
                        onc = str(1 - int(nc))
                        if i == 0:
                            currentLine =  nme + " "
                            currentLine +=  nc + " " +  nc + " L " + nme + ending + nc + "_ "
                            currentLine +=  onc + " " +  onc + " L " + nme
                        elif i == len(searchword)-1:
                            currentLine =  nme + ending + "_ "
                            currentLine +=  nc + " " +  nc + " L " + line[4] + " "
                            currentLine +=  onc + " " +  onc + " L " + "InPlace" + nme
                        else:
                            currentLine =  nme + ending + "_ "
                            currentLine +=  nc + " " +  nc + " L " + nme + ending + nc + "_ "
                            currentLine +=  onc + " " +  onc + " L " + "InPlace" + nme
                        s += [currentLine.split()]
                        ending += nc
                    states += s
            # Handle 'out' command to write values to the tape
            elif line[1] == "out":
                startState = line[0]
                endState = line[4]
                outString = line[2]
                direction = line[3]
                outStates = []
                n = len(outString)
                for digitI in range(n):
                    txt = startState + "." + str(digitI) + " 1 " + outString[digitI] + " " + direction + " " +  startState + "." + str(digitI+1) + "      0 " + outString[digitI] + " " + direction + " " + startState + "." + str(digitI+1)
                    outStates.append(txt.split())
                # Set the starting and ending states for the out command
                outStates[0][0] = startState
                outStates[n-1][4] = endState
                outStates[n-1][8] = endState
                states = states + outStates
            # Ignore comments
            elif line[1] == "comment":
                pass
            # Regular Turing machine state
            else:
                states.append(line)
        return [states, defineDict]

# Replace defined values in states with actual definitions
def replaceDefinedValues(stateFileOut, defineDict):
    for stateI in range(len(stateFileOut)):
        for wordI in range(len(stateFileOut[stateI])):
            print(stateI, " ", wordI)
            if stateFileOut[stateI][wordI] in list(defineDict.keys()):
                stateFileOut[stateFileOut[stateI][wordI]] = defineDict[stateFileOut[stateI][wordI]]
    return stateFileOut

# Turing Machine class definition
class TuringMachine():
    def __init__(self, filepath, inputTape):
        defineDict = {}
        # Read the states from the file and define the initial tape and pointers
        self.states = readStateFile(filepath, defineDict)[0]
        print(len(self.states))
        self.tape = "00000" + inputTape  + "00000"
        self.pointer = 1
        self.previousPointer = 1
        self.currentStatePointer = 0
    
    # Find the index of a state by its name
    def findState(self, stateName):
        for i in range(len(self.states)):
            if self.states[i][0] == stateName:
                return i
        return 0
    
    # Display the current state of the Turing machine
    def display(self):
        s = ""
        for i in range(len(self.tape)):
            if i == self.pointer: 
                s += "@"
            elif i == self.previousPointer:
                s += "~"
            else:
                s += " "
        print(self.states[self.currentStatePointer])
        print(s)
        print(self.tape)
        print("\n")

    # Perform one step of computation
    def step(self):
        self.previousPointer = self.pointer
        # Check if the current tape symbol matches the state transition condition
        if self.tape[self.pointer] == self.states[self.currentStatePointer][1]:
            nextValue = self.states[self.currentStatePointer][2]
            nextDirection = self.states[self.currentStatePointer][3]
            nextState = self.states[self.currentStatePointer][4]   
        else:
            nextValue = self.states[self.currentStatePointer][6]
            nextDirection = self.states[self.currentStatePointer][7]
            nextState= self.states[self.currentStatePointer][8]
        # Stop the machine if we reach the STOP state
        if nextState == "STOP":
            sys.exit()
        nextStatePointer = self.findState(nextState)
        ls = list(self.tape)
        # Update the tape with the new value and update the current state pointer
        ls[self.pointer] = nextValue
        self.tape = "".join(ls)
        self.currentStatePointer = nextStatePointer
        # Move the pointer in the specified direction
        if nextDirection == "R":
            self.pointer += 1
        elif nextDirection == "L":
            self.pointer -= 1
        self.display()
        time.sleep(0.01)

# Convert binary string into a specific format for the Turing machine
def binaryToFormat(binary):
    bs = "0111111111111111111110"
    be = "01111111111111111111110"
    binaryF = "".join(binary.split())
    return bs + binaryF + be

# Define constants used in constructing the example tape
adds = "011111111111111111101010"
ps = "0111111111111111110"
ie = "011111111111111111110"
pe = "011111111111111111111110"

# Define example binary digits
firstDigit = binaryToFormat("0000 0100 1100 0110")
secondDigit = binaryToFormat("0000 0010 0111 1001")
thirdDigit = binaryToFormat("0000 0001 0001 1100")

# Construct the example tape
EXAMPLE_TAPE =   ps + adds + firstDigit + adds + thirdDigit + secondDigit + ie + ie + pe

# Initialize the Turing machine with the provided file and tape
tm = TuringMachine(FILE_NAME, TAPE)

# Run the Turing machine for a certain number of steps
for i in range(10000000):
    tm.step()

# Print the final content of the tape
print(tm.tape)
