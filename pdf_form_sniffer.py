import os
import pdfrw
from reportlab.pdfgen import canvas

path = r'C:\Users\dgottesm\Desktop\{}'
form = "f8621"
FORM_TEMPLATE_PATH = path.format(form) + '.pdf'
FORM_OVERLAY_PATH = path.format(form) +'_overlay.pdf'
FORM_OUTPUT_PATH = path.format(form) + '_sniffed.pdf'

def get_pdf_info(path):
    pdf = pdfrw.PdfReader(path)
    print(pdf.keys())
    print(pdf.Info)
    print(pdf.Root.keys())
    print('PDF has {} pages'.format(len(pdf.pages)))


def sniff_pdf(input_pdf_path):

    ANNOT_KEY = '/Annots'
    ANNOT_FIELD_KEY = '/T'     #/FT says if button or field
    ANNOT_VAL_KEY = '/V'
    ANNOT_RECT_KEY = '/Rect'
    SUBTYPE_KEY = '/Subtype'
    WIDGET_SUBTYPE_KEY = '/Widget'
    CHECKBOX_ON = '1'  # could be "On", "Yes", or "1"

    button_list = []
    text_box_list = []
    template_pdf = pdfrw.PdfReader(input_pdf_path)
    for page in range(len(template_pdf.pages)):
        button_list.append('page {}'.format(page))
        text_box_list.append('page {}'.format(page))
        annotations = template_pdf.pages[page][ANNOT_KEY]
        for annotation in annotations:
            #print(annotation.keys())
            #print(annotation[ANNOT_RECT_KEY][0:2])
            #print(annotation['/Type'])
            if annotation[SUBTYPE_KEY] == WIDGET_SUBTYPE_KEY:
                if annotation[ANNOT_FIELD_KEY]:
                    key = annotation[ANNOT_FIELD_KEY][1:-1]
                    rect = str(annotation[ANNOT_RECT_KEY][0:2])

                    if annotation['/FT']=='/Btn':
                        button_list.append(annotation[ANNOT_RECT_KEY][0:2])
##                        annotation.update(pdfrw.PdfDict(AS=pdfrw.PdfName(CHECKBOX_ON)))

                    if annotation['/FT']=='/Tx':
                        #print(annotation[ANNOT_RECT_KEY][0:2],',')
                        #annotation.update(pdfrw.PdfDict(V=rect))
                        text_box_list.append(annotation[ANNOT_RECT_KEY][0:2])
    return text_box_list, button_list


def create_coordinate_overlay(text_box_list=[], button_list=[], output_path=''):
    """
    Create the data that will be overlayed on top
    of the form that we want to fill
    """
    c = canvas.Canvas(output_path)
    y_offset = 2

    text_pages   = [s for s in text_box_list if "page" in s]

    for page in range(len(text_pages)):
        c.setFontSize(14)
        if 'page {}'.format(page+1) in text_box_list:
            text_page_slice = text_box_list[text_box_list.index('page {}'.format(page)):text_box_list.index('page {}'.format(page+1))]
        else:
            text_page_slice = text_box_list[text_box_list.index('page {}'.format(page)):-1]
        for box in text_page_slice:
            if type(box) is list:
                c.drawString(float(box[0]), float(box[1])+y_offset, '{} {}'.format(box[0], box[1]))

        c.setFontSize(6)
        if 'page {}'.format(page+1) in button_list:
            button_slice = button_list[button_list.index('page {}'.format(page)):button_list.index('page {}'.format(page+1))]
        else:
            button_slice = button_list[button_list.index('page {}'.format(page)):-1]
        for box in button_slice:
            if type(box) is list:
                c.drawString(float(box[0]), float(box[1])+y_offset, '{} {}'.format(box[0], box[1]))

        c.showPage()

    c.save()

def merge_pdfs(form_pdf, overlay_pdf, output):
    """
    Merge the specified fillable form PDF with the
    overlay PDF and save the output
    """
    form = pdfrw.PdfReader(form_pdf)
    olay = pdfrw.PdfReader(overlay_pdf)

    for form_page, overlay_page in zip(form.pages, olay.pages):
        merge_obj = pdfrw.PageMerge()
        overlay = merge_obj.add(overlay_page)[0]
        pdfrw.PageMerge(form_page).add(overlay).render()

    writer = pdfrw.PdfWriter()
    writer.write(output, form)


def main():
    get_pdf_info(FORM_TEMPLATE_PATH)
    text_box_list, button_list = sniff_pdf(FORM_TEMPLATE_PATH)
    create_coordinate_overlay(text_box_list, button_list,FORM_OVERLAY_PATH)
    merge_pdfs(FORM_TEMPLATE_PATH,
               FORM_OVERLAY_PATH,
               FORM_OUTPUT_PATH)

    os.system(r"start chrome {}".format(FORM_OUTPUT_PATH))
    os.system(r"start chrome {}".format(FORM_OVERLAY_PATH))


main()