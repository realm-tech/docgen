# general libraries.
import numpy as np
import cv2 as cv
from glob import glob
from typing import List
import enum, os, yaml, shutil
from yaml import Loader

# genalog libraries.
from genalog.generation.document import DocumentGenerator
from genalog.generation.content import CompositeContent, ContentType
from genalog.degradation.degrader import Degrader, ImageState
from pdf2image import convert_from_path

from utils.file_util import get_logger, YamlDict2Mem, clear_up, create_folder
from utils.image import poses2bboxes, drawbboxes
from Warping.warper import GridWarper

from multiprocessing import Pool

with open('./config.yaml', 'r') as file:
    config = yaml.load(file, Loader=Loader)
config = YamlDict2Mem(**config)

os.environ["DUMP_BOUNDING_BOX"] = "1"
create_folder(config.output_folder)

def random_select(inp: List, count: int, logger=None):
    msg = "Input list len is: {}".format(len(inp))
    if logger: 
        logger.info(msg)
    else:
        print(msg)
    
    np.random.shuffle(inp)
    return inp[:count]

# Enum class for page sizes.
class PageSize(enum.Enum):
    A3 = 0
    A4 = 1
    A5 = 2
    LETTER = 3

logger = get_logger("genalog_extended", add_file=False)

if not config.headless_mode:
    winname = 'vis'
    cv.namedWindow(winname, cv.WINDOW_NORMAL)

# define paths.
text_path = "./texts/example.txt"
text_base_path = config.text_base_path
pdf_output_path = "./output"
absolute_path = "file://" + os.path.dirname(os.path.abspath(__file__))
absolute_path_wo = os.path.dirname(os.path.abspath(__file__))
logger.info("Absolute path: {}".format(absolute_path))
img_logo_base_path = config.img_logo_base_path 
img_sig_base_path = config.img_sig_base_path 
font_base_path = config.font_base_path

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

# define style parameters.
font_paths = random_select(glob(os.path.join(font_base_path, '*.ttf')), config.num_fonts)
font_family = [ font_path.split('.')[0] for font_path in font_paths ] 
font_paths = [ os.path.join("\"" + absolute_path, font_path + "\"") for font_path in font_paths ]

img_logos = [ os.path.join(absolute_path, logo) for logo in random_select(glob(os.path.join(img_logo_base_path, '*.png')), config.num_logos) ] 
img_signatures = [ os.path.join(absolute_path, sig) for sig in  random_select(glob(os.path.join(img_sig_base_path, '*emza*.png')), config.num_sigs) ]
print("###"*10 + "\nSample font", font_paths[0])
print("###"*10 + "\nSample logo path", img_logos[0]) 
print("###"*10 + "\nSample sig path", img_signatures[0]) 

page_size = PageSize.A5

# Grid Warper
gridWarper = GridWarper(random_area_ratio=0.13, logger=logger)

new_style_combinations = {
    "text_align": ["right"],
    "language": ["fa"],
    "absolute_path": [absolute_path],
    "font_path" : [font_paths],
    "img_logo" : img_logos,
    "img_signature" : img_signatures,
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

def clean_bboxes_output(obj, output): 
    buff = list()
    if isinstance(obj, list):
        for elem in obj: 
            if isinstance(elem, list):
                output = clean_bboxes_output(elem, output)
            elif isinstance(elem, tuple):
                output = clean_bboxes_output(elem, output)
            elif elem: 
                buff.append(elem)

    elif isinstance(obj, tuple):
        for elem in obj: 
            if isinstance(elem, list):
                output = clean_bboxes_output(elem, output)
            elif isinstance(elem, tuple):
                output = clean_bboxes_output(elem, output)
            elif elem:
                buff.append(elem)

    elif obj: 
        buff.append(obj)

    if len(buff) > 0: 
        output.append(buff)
    
    return output


def bbox2pts(bboxes: list, scale: float):
    # Filtering zero area bboxes 
    filetered_bboxes = list()
    for bbox in bboxes:
        if len(bbox) == 4: 
            filetered_bboxes.append(bbox)

    pts = np.zeros((len(filetered_bboxes), 4, 2), dtype=np.float32)

    for idx2, bbox in enumerate(filetered_bboxes): 

        for idx, elem in enumerate(bbox):
            bbox[idx] = int(bbox[idx]*scale) 

        ul = (bbox[0], bbox[1])
        ur = (bbox[0]+bbox[2], bbox[1])
        lr = (bbox[0]+bbox[2], bbox[1]+bbox[3])
        ll = (bbox[0], bbox[1]+bbox[3])
        pts[idx2] = np.array([ul, ur, lr, ll])
        #print(pts[i])
    
    return pts

def generate(worker_id: int=0):            
    # applying styles and degradation.
    iter = 0
    while True: 
        logger.info("iter no: {}".format(iter+1))
        iter+=1 

        default_generator = DocumentGenerator(template_path="./templates")
        doc_gen = default_generator.create_generator(content, ['letter.html.jinja'])
        default_generator.set_styles_to_generate(new_style_combinations)
        degrader = Degrader(DEGRADATIONS)
        
        for doc_idx, doc in enumerate(doc_gen):
            logger.info("Generating files for worker-id:{}/document index:{}/iteration :{}".format(worker_id, doc_idx, iter))

            base_output_path = os.path.join(config.output_folder, "worker_{}".format(worker_id),  f"iter_{iter}")
            os.makedirs(base_output_path, exist_ok=True)

            pdf_name = os.path.join(base_output_path, "output.pdf")
            # Store Pdf with convert_from_path function.
            
            bbox = doc.render_pdf(target=pdf_name, zoom=config.zoom)
            cleaned_bboxes = clean_bboxes_output(bbox, list())

            if config.dump_bboxes:
                output_bboxes_file_name = os.path.join(base_output_path,"{}.txt".format(doc_idx)) 
                
                #print("BBoxes file", output_bboxes_file_name)
                with open(output_bboxes_file_name, 'w') as file:
                    for entries in cleaned_bboxes:
                        line = ""
                        for entry in entries:
                            line += str(entry)
                            line += "," 
                        line = line[:-1]
                        line += "\n"
                        file.write(line)            
            
            if config.dump_html: 
                # doc.render_png(target=png_name, resolution=300)
                html_output = doc.render_html()
                with open(os.path.join(base_output_path, 'string.html'), 'w') as file :
                    file.writelines(html_output)

            #print("Bboxes len: ", len(cleaned_bboxes))

            images = convert_from_path(pdf_name, dpi=config.dpi)
            for i in range(len(images)):
                # png_name = file_name + "_" + str(i) + ".png"
                # deg_png_name = deg_file_name + "_" + str(i) + ".png"
                original_png_name = str(i) + ".png"
                original_png_path = os.path.join(base_output_path, original_png_name)
                #print(type(images[i]))
                images[i].save(original_png_path, 'PNG')

                deg_image = degrader.apply_effects(cv.imread(original_png_path, cv.IMREAD_GRAYSCALE))

                deg_image = deg_image.reshape((*deg_image.shape,1)) 
                deg_image = np.concatenate((deg_image, deg_image, deg_image), axis=2)
                
                bbox_pts = bbox2pts(cleaned_bboxes, scale=config.pdf2image_scale_factor)
                
                warped_png_path = None
                # Random Warping
                if config.warp.enabled: 
                    warped_png_path = os.path.join(base_output_path, config.warped_images_prefix + original_png_name)
                    deg_image, bbox_pts = gridWarper(deg_image, bbox_pts)
                    cv.imwrite(warped_png_path, deg_image)

                if config.dump_points: 
                    lines = list()
                    
                    if warped_png_path: 
                        bbox_pts_points_path = warped_png_path + '.txt'
                    else:                         
                        bbox_pts_points_path = os.path.join(base_output_path, "pts_{}.txt".format(doc_idx))

                    with open(bbox_pts_points_path ,'w') as pts_file:
                        line = ""
                        for pt in bbox_pts: 
                            for coords in pt:
                                for coord in coords:  
                                    line += str(coord)
                                    line += ','

                            line = line[:-1]
                            line += "\n"
                            lines.append(line)
                        pts_file.writelines(lines)

                if config.dump_visulized_bboxes:
                    bboxes_visulized_image = drawbboxes(deg_image, bbox_pts, color=(207, 227, 226))      
                    bboxes_visualized_path = os.path.join(base_output_path, config.bbox_visualized_prefix + original_png_name)
                    cv.imwrite(bboxes_visualized_path, bboxes_visulized_image)
                    #print('Bbox Visualied Degraded image written to:', bboxes_visualized_path)

                break

            break     
        

        if iter == config.iteration_per_worker: 
            break


if __name__ == '__main__': 

    worker_pool = Pool(config.worker_count)

    workers_id = [i for i in range(config.worker_count)]

    worker_pool.map(
        generate, 
        workers_id
    )
