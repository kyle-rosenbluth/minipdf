import sys
import subprocess
import os

cf_old = open(sys.argv[1])
crossword_file = cf_old.read()
mini_number = sys.argv[2]
tex_header = open("tex_header.txt").read()
tex_header = tex_header.replace("\\textsf{\\textbf{\\huge{Mini Meta}}}", "\\textsf{\\textbf{\\huge{Mini Meta " + mini_number + "}}}")

# Indeces variables indicate what #value to label the tiles. It does not offer any insight on to which tiles get the numbers, just what the tiles # values should be.
acrossIndeces = [[], [], [], [], [], []]
downIndeces = [[], [], [], [], [], []]

# acrossClueCount = [0] * 6
# downClueCount = [0] * 6

acrossClues = [[], [], [], [], [], []]
downClues = [[], [], [], [], [], []]
escapeChars = {"_": "\_", "&":"\&", "%": "\%", "$":"\$", "#":"\#", "{":"\{", "}":"\}", "~":"\\textasciitilde", "^":"\\textasciicircum", "\\":"\\textbackslash"}
metaClueIndeces = None
metaSolutionIndeces = None
metaClues = []
metaSolution = []
def generatePuzzle(solved):
    section = 0
    unitLength = 25 if solved else 23
    gray_cell ="""\\cellcolor{gray!25}\n"""
    puzzle_start_pre_toprow = """\\renewcommand{\\PuzzleUnitlength}{""" + str(unitLength) + """pt}\n\\begin{minipage}[t][23em][t]{\colwidth}\n\\vspace{.25em}\n\\center{\\textsf{\\textbf{"""
    puzzle_start_pre_bottomrow = """\\renewcommand{\\PuzzleUnitlength}{""" + str(unitLength) + """pt}\n\\begin{minipage}[c][23em][t]{\colwidth}\n\\vspace{1em}\n\\center{\\textsf{\\textbf{"""
    puzzle_start_post = """}}}\\vspace{0.55em}\\\\\n\\begin{Puzzle}{5}{5}\n"""
    if (solved):
        puzzle_start_post = """}}}\\vspace{0.55em}\\\\\n\\PuzzleSolution\n\\begin{Puzzle}{5}{5}\n"""


    crosswords = [gray_cell + puzzle_start_pre_toprow + "MONDAY" + puzzle_start_post,
                puzzle_start_pre_toprow + "TUESDAY" + puzzle_start_post,
                gray_cell + puzzle_start_pre_toprow + "WEDNESDAY" + puzzle_start_post,
                puzzle_start_pre_bottomrow + "THURSDAY" + puzzle_start_post,
                gray_cell + puzzle_start_pre_bottomrow + "FRIDAY" + puzzle_start_post,
                puzzle_start_pre_bottomrow + "SATURDAY" + puzzle_start_post]
    col_num = [[0 for j in range(5)] for i in range(6)]
    row_num = [[0 for j in range(5)] for i in range(6)]

    # clueIndeces is a counter array to keep count for numbering tiles. It's ending value is garbage.
    clueIndeces = [0] * 6

    downCluesFlat = []
    acrossCount = 0
    boardIdx = 0
    row = 0
    col = 0
    level = 0
    puzzleText = []
    for line in iter(crossword_file.splitlines()):
        # print(line)
        if (line == "\n" or line == ""):
            print("empty")
            # Skip empty line
            continue
        elif (line == "Across"):
            # Begin parsing across clues for all puzzles.
            section = 1
            continue
        elif line == "Down":
            print("Down?")
            # Begin parsing down clues for all puzzles
            section = 2
            continue
        elif line == "===":
            # Begin parsing meta solutions
            section = 3
        if section == 0:
            puzzleText.append(line)
        elif section == 1:
            # Across clues we can parse and place in one step. Down clues are a little tougher.
            num_clue = line.split(". ", 1)
            acrossCount += 1
            boardIdx = int(acrossCount / 5)
            if (acrossCount % 5 == 0):
                boardIdx -= 1
            print(num_clue)
            acrossClues[col + level].append(num_clue[1].replace("\n", "").translate(str.maketrans(escapeChars)))
            col += 1
            if (col == 3):
                row += 1
                col = 0
            if (row == 5):
                level = 3
                row = 0
        elif section == 2:
            num_clue = line.split(". ", 1)
            downCluesFlat.append(num_clue[1].replace("\n", "").translate(str.maketrans(escapeChars)))
        elif section == 3:
            print("yo")
    level = 0
    row = 0
    col = 0
    boardIdx = 0
    amuse_solutions = ["", "", "", "", "", ""]
    for line in puzzleText:
        if (line == "................."):
            print("NOWA")
            # Row of all black tiles means we've moved down to the Thu / Fri / Sat row
            level = 3
            row = 0
            col = 0
            continue
        boardIdx = level
        crosswords[boardIdx] += "|"
        squareIdx = -1
        for c in (line + "\n"):
            squareIdx += 1
            if (squareIdx > 0 and squareIdx % 5 == 0):
                print("newe board")
                # This means we've gone to a new board
                crosswords[boardIdx] += ".\n"
                amuse_solutions[boardIdx] += "\n"
                boardIdx += 1
                col = 0
                if boardIdx > 5 or boardIdx == 3:
                    continue
                crosswords[boardIdx] = crosswords[boardIdx] + "|"
                squareIdx = -1
                continue
            if (c == '.'):
                crosswords[boardIdx] += "* |"
                amuse_solutions[boardIdx] += "."
            else:
                if not (col_num[boardIdx][col] and row_num[boardIdx][row]):
                    clueIndeces[boardIdx] += 1
                    crosswords[boardIdx] += "[" + str(clueIndeces[boardIdx]) + "]" + c + " |"
                    amuse_solutions[boardIdx] += c
                    if not col_num[boardIdx][col]:
                        downIndeces[boardIdx].append(clueIndeces[boardIdx])
                        downClues[boardIdx].append(downCluesFlat.pop(0))
                    if not row_num[boardIdx][row]:
                        acrossIndeces[boardIdx].append(clueIndeces[boardIdx])
                    col_num[boardIdx][col] = clueIndeces[boardIdx]
                    row_num[boardIdx][row] = clueIndeces[boardIdx]
                else:
                    crosswords[boardIdx] += c + " |"
                    amuse_solutions[boardIdx] += c
            col += 1
        row += 1
    if (not solved):
        # Across
        for i in range(len(crosswords)):
            crosswords[i] += """\\end{Puzzle}\\\\\n{\\fontfamily{put}\\selectfont\n\\begin{PuzzleClues}{\\textbf{Across}}\\\\\n"""
        boardIdx = 0
        for puz in acrossClues:
            clueIdx = 0
            for clue in puz:
                clue_num = acrossIndeces[boardIdx][clueIdx]
                clue = acrossClues[boardIdx][clueIdx]
                # acrossClueCount[boardIdx] += 1
                clueIdx += 1
                crosswords[boardIdx] += """\\Clue{\\textbf{""" + str(clue_num) + """}} {} {\\raggedright{""" + clue + """}} \\\\\n"""
            boardIdx += 1

        #Down
        for i in range(len(crosswords)):
            crosswords[i] += """\\end{PuzzleClues}\n\\begin{PuzzleClues}{\\textbf{Down}} \\\\\n"""

        boardIdx = 0
        for puz in downClues:
            clueIdx = 0
            for clue in puz:
                clue_num = downIndeces[boardIdx][clueIdx]
                clue = downClues[boardIdx][clueIdx]
                clueIdx += 1
                crosswords[boardIdx] += """\\Clue{\\textbf{""" + str(clue_num) + """}} {} {\\raggedright{""" + clue + """}} \\\\\n"""
            boardIdx += 1

        for i in range(len(crosswords)):
            crosswords[i] += """\n\\end{PuzzleClues}\n}\n\\end{minipage}\n\\vspace{1em}\n"""
            if i == 2:
                crosswords[i] += """\\\\"""
            elif i != 5:
                crosswords[i] += """&\n"""
    return (crosswords,  amuse_solutions)

crosswords_unsolved, amuse_solutions = generatePuzzle(False)
document = tex_header + "\n" + ''.join(crosswords_unsolved)
document += """\\\\\n\\end{tabular}\n\\end{center}\n\\end{document}"""
# print(document)

amuse_doc = ""
for i in range(6):
    amuse_doc += amuse_solutions[i] + "\n"
    amuse_doc +=  "Across\n"
    for (clue, num) in zip(acrossClues[i], acrossIndeces[i]):
        amuse_doc  += str(num) + ". " + clue  + "\n"
    amuse_doc += "\n"
    amuse_doc +=  "Down\n"
    for (clue, num) in zip(downClues[i], downIndeces[i]):
        amuse_doc  += str(num) + ". " + clue  + "\n"
    amuse_doc += "\n---\n\n"
print(amuse_doc)

try:  
    os.mkdir("output")  
except OSError as error:  
    print(error)

fileName = "MiniMeta" +  mini_number
f = open("output/" + fileName + ".txt", "w")
f.write(amuse_doc)
f.close()

f = open("output/" + fileName + ".tex", "w")
f.write(document)
f.close()

subprocess.check_call(['pdflatex', "output/" + fileName + ".tex"])
os.rename(fileName + ".pdf", "output/" + fileName + ".pdf")