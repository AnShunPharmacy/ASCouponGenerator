from PIL import Image, ImageDraw, ImageFont, ImageFilter
import copy
import threading


#set the default image path----

default_upper_element_path = './assets/image_element/top.png'
default_back_image_path = './assets/image_element/back.png'

#------------------------------

COUPONS_POSITIONS = {
    1: (73, 73),
    2: (1374, 73),
    3: (73, 674),
    4: (1374, 674),
    5: (73, 1275),
    6: (1374, 1275)
}
PAPER_SIZE = (2738, 1936)


def get_info_text(path='assets/documents/info.txt') -> str:
    with open(path, 'r', encoding='utf-8') as file:
        return file.read()


def write_info_text(info_text)-> str:
    path = 'assets/documents/info.txt'
    with open(path, "w", encoding='utf-8') as file:
        return file.write(info_text)


def generate_coupon_image(back_image_path: str, upepr_element_path: str, info_text: str,):
    upepr_element = Image.open(upepr_element_path)
    upepr_element = upepr_element.convert('RGBA')

    output = Image.new('RGBA', upepr_element.size, (255, 255, 255, 255))

    back_image = Image.open(back_image_path)
    back_image = back_image.resize((430,430))
    mask = Image.new("L", back_image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rectangle((20, 20, 410, 410), fill=255) 
    mask_blur = mask.filter(ImageFilter.GaussianBlur(10))
    back_image = Image.composite(back_image, output, mask_blur)
    back_image = back_image.convert('RGBA') 
    
    output.paste(back_image, (640, 163), back_image)
    output.paste(upepr_element, (0, 0), upepr_element)

    font = ImageFont.truetype('assets/font/標楷體.ttf', size=30)
    drawing = ImageDraw.Draw(output)
    drawing.text((20, 328), info_text, fill='rgb(0, 0, 0)', font=font)

    return output


def coupon_add_number(coupon_image, serial_number: str):
    font = ImageFont.truetype('assets/font/標楷體.ttf', size=50)
    drawing = ImageDraw.Draw(coupon_image)
    drawing.text((485, 30), serial_number, fill='rgb(255, 0, 0)', font=font)
    return coupon_image


def generate_preview_coupon(back_image_path: str,serial_prefix:str, serial_start_number: int):
    coupon_image = generate_coupon_image(back_image_path, default_upper_element_path,  get_info_text())
    serial_number = f'NO. {serial_prefix}{str(serial_start_number).zfill(4)}'
    coupon_image = coupon_add_number(coupon_image, serial_number)
    original_size_x , original_size_y = coupon_image.size
    original_size = (original_size_x // 2, original_size_y // 2)
    coupon_image = coupon_image.resize(original_size)
    return coupon_image


def generate_paper(size: tuple):
    x_center_point_corrected = size[0] // 2 + 4
    center_line = (x_center_point_corrected, 0, x_center_point_corrected, size[1])
    gap = size[1] // 3
    y_gap_corrected = gap + 28
    y_gap2_corrected = gap * 2 - 16
    horizontal_line_1 = (0, y_gap_corrected, size[0],y_gap_corrected)
    horizontal_line_2 = (0, y_gap2_corrected, size[0], y_gap2_corrected)

    paper = Image.new('RGBA', size, (255, 255, 255, 255))
    drawing = ImageDraw.Draw(paper)
    drawing.line((0, 72, size[0], 72), fill=(50, 50, 50), width=1)
    drawing.line((0, 1875, size[0], 1875), fill=(50, 50, 50), width=1)
    drawing.line((72 ,0 , 72, size[1]), fill=(50, 50, 50), width=1)
    drawing.line((2674 ,0 , 2674, size[1]), fill=(50, 50, 50), width=1)

    drawing.line(center_line, fill=(50, 50, 50), width=1)
    drawing.line(horizontal_line_1, fill=(50, 50, 50), width=1)
    drawing.line(horizontal_line_2, fill=(50, 50, 50), width=1)

    return paper


def generate_papers(amount: int, serial_start_number: int, serial_prefix: str, back_image_path: str):
    blank_coupon = generate_coupon_image(back_image_path, default_upper_element_path, get_info_text())
    paper = generate_paper(PAPER_SIZE)
    copied_paper = copy.deepcopy(paper)

    pieces_counting = 0
    pages_counting = 0

    output = []

    for i in range(serial_start_number, serial_start_number + amount):
        serial_number = f'NO. {serial_prefix}{str(i).zfill(4)}'
        coupon = coupon_add_number(copy.deepcopy(blank_coupon), serial_number)
        copied_paper.paste(coupon, COUPONS_POSITIONS[pieces_counting + 1], coupon)
        print(f'Generate coupon: {serial_number}', end='\r')
        pieces_counting += 1

        if pieces_counting == 6:
            output.append(copied_paper)
            copied_paper = copy.deepcopy(paper)
            pieces_counting = 0
            pages_counting += 1
            print(f'Generate page: {pages_counting}', end='\r')

    if pieces_counting != 0:
        output.append(copied_paper)
        print(f'Generate page: {pages_counting}', end='\r')

    return output


def combine_papers(papers, output_path: str):
    papers[0].save(output_path, format='PDF', resolution=100, save_all=True, append_images=papers[1:])


if __name__ == '__main__':
    papers = generate_papers(6, 30, '2410', default_back_image_path )
    combine_papers(papers, 'output.pdf')
    print('Done!')
