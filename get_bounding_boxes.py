from pdfminer.layout import LAParams, LTChar, LTTextBox, LTTextLine
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
import re

def get_bounding_boxes(path, print_output = False ):
    fp = open(path, 'rb')
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    pages = PDFPage.get_pages(fp)

    page_words = []
    page_positions = []

    for page in pages:
        if (print_output):
            print('x1\ty1\tx2\ty2\tword\n---\t---\t---\t---\t---')
        interpreter.process_page(page)
        layout = device.get_result()

        cropbox = page.cropbox
        words = []
        positions = []
        word = ""
        height_low = 0
        height_high = 10000
        for lobj in layout:
            if isinstance(lobj, LTTextBox):
                for liobj in lobj:
                    if isinstance(liobj, LTTextLine):
                        for chobj in liobj:
                            if isinstance(chobj, LTChar):

                                if (word == "" and chobj.get_text() == ""):
                                    continue

                                words.append(chobj.get_text())
                                positions.append(chobj.bbox)

        positions, words = sortBBP(positions, words, 1, 0)        
        if (print_output):
            for index, w in enumerate(words):
                print('%d\t%d\t%d\t%d\t%s\n' % (positions[index][0], positions[index][1], positions[index][2], positions[index][3], w))

        page_words.append(words)
        page_positions.append(positions)

    return page_words, page_positions, cropbox
 
def sortBBP(positions, words, i, j):
    temp_positions = []
    temp_words = []
    positions, words = sortBB(positions, words, i)

    temp_index_position = positions[0][i]
    temp_part_positions = []
    temp_part_words = []
    for index, position in enumerate(positions):
        if (abs(position[i] - temp_index_position) < 0.3 * abs(position[3] - position[1])):
            temp_part_positions.append(position)
            temp_part_words.append(words[index])
            temp_index_position = position[i]
        elif (is_list_words(temp_part_words)):
            temp_part_positions, temp_part_words = sortBB(temp_part_positions, temp_part_words, j)
            temp_part_positions, temp_part_words = pop_multiple_spaces(temp_part_positions, temp_part_words)
            temp_part_positions, temp_part_words = concatWords(temp_part_positions, temp_part_words)
            for iindex, temp_part_position in enumerate(temp_part_positions):
                temp_positions.append(temp_part_position)
                temp_words.append(temp_part_words[iindex])

            temp_part_positions = []
            temp_part_words = []
            temp_part_positions.append(position)
            temp_part_words.append(words[index])
            temp_index_position = position[i]
        elif (len(positions) > index + 1):
            temp_part_positions = []
            temp_part_words = []
            temp_part_positions.append(position)
            temp_part_words.append(words[index])
            temp_index_position = position[i]


    if (is_list_words(temp_part_words)):
        temp_part_positions, temp_part_words = sortBB(temp_part_positions, temp_part_words, j)
        temp_part_positions, temp_part_words = pop_multiple_spaces(temp_part_positions, temp_part_words)
        temp_part_positions, temp_part_words = concatWords(temp_part_positions, temp_part_words)
        for iindex, temp_part_position in enumerate(temp_part_positions):
            temp_positions.append(temp_part_position)
            temp_words.append(temp_part_words[iindex])
    
    return temp_positions, temp_words

def sortBB(positions, words, i):
    temp_positions = []
    temp_words = []
    indices = []
    for position in positions:
        indices.append(position[i])
    
    sorted_index = sorted(range(len(indices)),key=indices.__getitem__)
    
    for i in sorted_index:
        temp_positions.append(positions[i])
        temp_words.append(words[i])

    return temp_positions, temp_words

def concatWords(positions, words):
    temp_positions = []
    temp_words = []
    temp_word = ""

    if (words[0] == " "):
        words.pop(0)
        positions.pop(0)

    start_position = positions[0]

    for index, word in enumerate(words):
        if (word == " "):
            end_position = positions[index - 1]
            temp_word = correctPersian(temp_word)
            temp_words.append(temp_word)
            temp_positions.append([start_position[0], start_position[1], end_position[2], end_position[3]])
            if (len(positions) > index + 1):
                start_position = positions[index + 1]
            temp_word = ""
        else:
            temp_word += word
    
    if (words[-1] != " "):
        end_position = positions[-1]
        temp_word = correctPersian(temp_word)
        temp_words.append(temp_word)
        temp_positions.append([start_position[0], start_position[1], end_position[2], end_position[3]])
    
    return temp_positions, temp_words

def pop_multiple_spaces(positions, words):
    count = 0
    temp_positions = []
    temp_words = []
    for i, word in enumerate(words):
        if (word == " "):
            count += 1
        else:
            count = 0

        if (count <= 1):
            temp_positions.append(positions[i])
            temp_words.append(word)

    return temp_positions, temp_words

def is_list_words(words):
    result = False
    for word in words:
        if (word != " "):
            result = True
    return result


def correctPersian(s):
    n_s = s;
    for t in re.findall(r'[\u0600-\u06FF\s]+$', s):
        n_s = re.sub(t, t[::-1], n_s)
    return n_s

# depricated functions.
def isEnglish(s):
    reg = re.compile(r'[a-zA-Z]')
    return bool(reg.match(s))

def isPersian(s):
    reg = re.compile(r'/^[\u0600-\u06FF\s]+$/')
    return bool(reg.match(s))

def isPunctuation(s):
    reg = re.compile(r'[.!?\\-]')
    return bool(reg.match(s))