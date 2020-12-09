import sys
import subprocess
import os

crossword_file = open(sys.argv[1])
tex_header = open(sys.argv[2]).read()

section = 0
gray_cell ="""\\cellcolor{gray!25}\n"""
puzzle_start_pre_toprow = """\\renewcommand{\\PuzzleUnitlength}{23pt}\n\\begin{minipage}[t][23em][t]{\colwidth}\n\\vspace{.25em}\n\\center{\\textsf{\\textbf{"""
puzzle_start_pre_bottomrow = """\\renewcommand{\\PuzzleUnitlength}{23pt}\n\\begin{minipage}[c][23em][t]{\colwidth}\n\\vspace{1em}\n\\center{\\textsf{\\textbf{"""
puzzle_start_post = """}}}\\vspace{0.55em}\\\\\n\\begin{Puzzle}{5}{5}\n"""


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

# Indeces variables indicate what #value to label the tiles. It does not offer any insight on to which tiles get the numbers, just what the tiles # values should be.
acrossIndeces = [[], [], [], [], [], []]
downIndeces = [[], [], [], [], [], []]

# acrossClueCount = [0] * 6
# downClueCount = [0] * 6

acrossClues = [[], [], [], [], [], []]
downCluesFlat = []
acrossCount = 0
boardIdx = 0
row = 0
col = 0
level = 0
puzzleText = []
for line in crossword_file:
    if (line == "\n"):
        # Skip empty line
        continue
    elif (line == "Across\n"):
        # Begin parsing across clues for all puzzles.
        section = 1

        continue
    elif line == "Down\n":
        # Begin parsing down clues for all puzzles
        section = 2
        continue
    if section == 0:
        puzzleText.append(line)
    elif section == 1:
        # Across clues we can parse and place in one step. Down clues are a little tougher.
        num_clue = line.split(". ", 1)
        acrossCount += 1
        boardIdx = int(acrossCount / 5)
        if (acrossCount % 5 == 0):
            boardIdx -= 1
        acrossClues[col + level].append(num_clue[1].replace("\n", "").translate(str.maketrans({"_": "\_"})))
        col += 1
        if (col == 3):
            row += 1
            col = 0
        if (row == 5):
            level = 3
            row = 0
    else:
        num_clue = line.split(". ", 1)
        downCluesFlat.append(num_clue[1].replace("\n", "").translate(str.maketrans({"_": "\_"})))
level = 0
row = 0
col = 0
boardIdx = 0
downClues = [[], [], [], [], [], []]
amuse_solutions = ["", "", "", "", "", ""]
for line in puzzleText:
    if (line == ".................\n"):
        # Row of all black tiles means we've moved down to the Thu / Fri / Sat row
        level = 3
        row = 0
        col = 0
        continue
    boardIdx = level
    crosswords[boardIdx] += "|"
    squareIdx = -1
    # print(line)
    for c in line:
        # print(c)
        squareIdx += 1
        if (squareIdx > 0 and squareIdx % 5 == 0):
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

document = tex_header + "\n" + ''.join(crosswords)
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



f = open("mini.tex", "w")
f.write(document)
f.close()

subprocess.check_call(['pdflatex', 'mini.tex'])# print(acrossClueCount)

#")