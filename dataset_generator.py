# general libraries.
import numpy as np
import cv2 as cv
import fitz, enum, os, yaml

from glob import glob
from typing import List

# genalog libraries.
from genalog.generation.document import DocumentGenerator
from genalog.generation.content import CompositeContent, ContentType
from genalog.degradation.degrader import Degrader, ImageState
# pdf2img library.
from pdf2image import convert_from_path
# custom made library to extract bounding boxes from PDF.
from get_bounding_boxes import get_bounding_boxes as GetBoundingBoxes

from utils.file_util import get_logger, YamlDict2Mem
from utils.image import poses2bboxes, drawbboxes

from Warping.warper import GridWarper

with open('./config.yaml', 'r') as file:
    config = yaml.load(file)
config = YamlDict2Mem(**config)
print(config)

def random_select(inp: List, count: int, logger=None):
    msg = "Input list len is: {}".format(len(inp))
    if logger: 
        logger.info(msg)
    else:
        print(msg)
    
    np.random.shuffle(inp)
    return inp[:count]

np.random.seed(37)

# Enum class for page sizes.
class PageSize(enum.Enum):
    A3 = 0
    A4 = 1
    A5 = 2
    LETTER = 3

logger = get_logger("genalog_extended", add_file=False)

winname = 'vis'
cv.namedWindow(winname, cv.WINDOW_NORMAL)

# define paths.
text_path = "./texts/example.txt"
text_base_path = "./texts"
pdf_output_path = "./output"
absolute_path = "file://" + os.path.dirname(os.path.abspath(__file__))
logger.info("Absolute path: {}".format(absolute_path))
img_logo_base_path = "./img_logos/"
img_sig_base_path = "./img_sigs/"
font_base_path = "./fonts/"

all_fonts = glob(os.path.join(font_base_path, '/*.ttf'))

BASE_OUTPUT_PATH= "output"
os.makedirs(BASE_OUTPUT_PATH, exist_ok=True)

with open(os.path.join(text_base_path, 'crawler.txt'), 'r') as file:
    text_dataset = file.readlines()

letter_addressee_name = [i for i in text_dataset if len(i)<30]
letter_addressee_name = random_select(letter_addressee_name, config.num_addressee_name)

letter_addressee_title = [i for i in text_dataset if len(i)<40]
letter_addressee_title = random_select(letter_addressee_title, config.num_addressee_title)

paragraphs = [i for i in text_dataset if len(i.split()) > 30 and len(i.split()) < 50 ]
logger.info("Paragraph number is {}".format(len(paragraphs)))

content_types = [ContentType.PARAGRAPH] * len(paragraphs)
content = CompositeContent(paragraphs, content_types)
default_generator = DocumentGenerator(template_path="./templates")
doc_gen = default_generator.create_generator(content, ['letter.html.jinja'])

# define style parameters.
font_paths = random_select(glob(os.path.join(font_base_path, '*.ttf')), config.num_fonts)
font_family = [ font_path.split('.')[0] for font_path in font_paths ] 
img_logos = [ os.path.join(absolute_path, logo) for logo in random_select(glob(os.path.join(img_logo_base_path, '*.png')), config.num_logos) ] 
img_signatures = [ os.path.join(absolute_path, sig) for sig in  random_select(glob(os.path.join(img_sig_base_path, '*emza*.png')), config.num_sigs) ]
print("###"*10 + "\nSample logo path", img_logos[0]) 
print("###"*10 + "\nSample sig path", img_signatures[0]) 

page_size = PageSize.A5

# Grid Warper
gridWarper = GridWarper(random_area_ratio=0.13, logger=logger)

new_style_combinations = {
    "hyphenate": [False],
    "font_size": ["11px"],
    "font_family": [font_family],
    "text_align": ["right"],
    "language": ["fa"],

    "absolute_path": [absolute_path],
    "font_path" : [font_paths],
    "img_logo" : [img_logos],
    "img_signature" : [img_signatures],
    "page_size" : [2], #[0, 1, 2, 3] A5

    # address properties
    "letter_addressee_name": letter_addressee_name,
    "letter_addressee_title": letter_addressee_title,
    #"add_trans_rot": [ str(i)+"deg" for i in np.arange(-2, 2.5, 0.5) ],
    #"add_trans_skew": [ str(i)+"deg" for i in np.arange(-1, 1.5, 0.5) ],

    # section properties
    #"sec_trans_skewy": [ str(i)+"deg" for i in np.arange(-1, 1.5, 0.5) ],
    "sec_text_align": [ "center", "left", "right", "justify" ]
}

# define degeradation parameters.
DEGRADATIONS = [
    ("morphology", {"operation": "open", "kernel_shape":(3,3), "kernel_type":"plus"}),
    ("morphology", {"operation": "close", "kernel_shape":(5,1), "kernel_type":"ones"}),
    ("salt", {"amount": 0.01}),
    ("overlay", {
        "src": ImageState.ORIGINAL_STATE,
        "background": ImageState.CURRENT_STATE,
    }),
    ("bleed_through", {
        "src": ImageState.CURRENT_STATE,
        "background": ImageState.ORIGINAL_STATE,
        "alpha": 0.95,
        "offset_x": -1,
        "offset_y": -3,
    }),
    ("pepper", {"amount": 0.005}),
    ("blur", {"radius": 1}),
    ("salt", {"amount": 0.005}),
]

# applying styles and degradation.
default_generator.set_styles_to_generate(new_style_combinations)
degrader = Degrader(DEGRADATIONS)

for idx, doc in enumerate(doc_gen):
    logger.info("Generating files for {}".format(idx))

    base_output_path = os.path.join(pdf_output_path,str(idx))
    os.makedirs(base_output_path, exist_ok=True)

    file_name = os.path.join(base_output_path, "{}".format(str(idx))) 
    deg_file_name = os.path.join(base_output_path, "{}".format(str(idx)))

    pdf_name = file_name + ".pdf"
    # Store Pdf with convert_from_path function.
    
    doc.render_pdf(target=pdf_name, zoom=config.zoom)
    # doc.render_png(target=png_name, resolution=300)
    
    # getting bounding boxes.
    words, positions, cropbox = GetBoundingBoxes(pdf_name, print_output=False)
    page_height = cropbox[3]

    wbboxes = poses2bboxes(positions, page_height, config.zoom)    

    images = convert_from_path(pdf_name, dpi=config.dpi)
    for i in range(len(images)):
        png_name = file_name + "_" + str(i) + ".png"
        deg_png_name = deg_file_name + "_" + str(i) + ".png"

        # Save pages as images in the pdf.
        images[i].save(png_name, 'PNG')
        deg_image = degrader.apply_effects(cv.imread(png_name, cv.IMREAD_GRAYSCALE))

        deg_image = deg_image.reshape((*deg_image.shape,1)) 
        deg_image = np.concatenate((deg_image, deg_image, deg_image), axis=2)
        # Random Warping
        if config.warp.enabled: 
            deg_image, wbboxes = gridWarper(deg_image, wbboxes)
        

        deg_image = drawbboxes(deg_image, wbboxes, color=(207, 227, 226))
        cv.imshow(winname, deg_image)
        cv.waitKey(0)        

        cv.imwrite(deg_png_name, deg_image)



# words, positions = GetBoundingBoxes(pdf_name, True)

# # correction parameters for expand/collapse bounding boxes.
# alpha = 1
# beta = 1
# for i in range(len(positions)):
#     for j in range(len(positions[i])):
#         positions[i][j][1] *= alpha
#         positions[i][j][3] *= beta
    
# # generating bounding boxes.
# doc = fitz.open(pdf_name)
# for index, page in enumerate(doc):
#     for position in positions[index]:
#         # For every page, draw a rectangle on coordinates
#         page.draw_rect([min(position[0], position[2]),  min(position[1], position[3]), max(position[0], position[2]), max(position[1], position[3])],  color = (0, 1, 0), width = 2)

# # Save pdf
# doc.save(file_name + "_bbox" + ".pdf")