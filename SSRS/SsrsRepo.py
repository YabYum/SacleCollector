import io
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from matplotlib.font_manager import FontProperties


# set Chinese fonts manually
font_path_regular = 'font/NotoSansSC-Regular.ttf'
font_path_bold = 'font/NotoSansSC-Bold.ttf'
font_path_light = 'font/NotoSansSC-Light.ttf'
pdfmetrics.registerFont(TTFont('NotoSansSC', font_path_regular))
pdfmetrics.registerFont(TTFont('NotoSansSC-b', font_path_bold))
notoregu = FontProperties(fname=font_path_regular)
notolight = FontProperties(fname=font_path_light)

class ReportGenerator:
    def __init__(self, user_id, num_responses, responses, ssrs_path):
        self.user_id = user_id
        self.num_response = num_responses
        self.responses = responses
        self.file_path = ssrs_path
        self.data = self.load_data()
        
    def load_data(self):

        with open(self.file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data

    def description(self, item_number):
        """Retrieve the event description from data."""
        for question in self.data['questions']:
            if question['item'] == str(item_number):
                return question['description']
        return None
    
    def scorer(self):
        for i in range(13):
            total = self.num_response[i].value
        obj = self.num_response[1].value + self.num_response[12].value + self.num_response[13].value
        sub = self.num_response[0].value + self.num_response[2].value + self.num_response[3].value + self.num_response[4].value + self.num_response[5].value + self.num_response[6].value + self.num_response[7].value + self.num_response[8].value
        ult = self.num_response[9].value + self.num_response[10].value + self.num_response[11].value
        return total, obj, sub, ult

    def generate_pdf(self, font_size=8):
        
        total, obj, sub, ult = self.scorer()

        pdf = canvas.Canvas(f"{self.user_id}_report.pdf", pagesize=letter)
        width, height = letter

        column1_x = 50

        pdf.setFont("NotoSansSC-b", font_size)

        title = "社会支持评定量表（SSRS）结果报告"
        title_width = pdf.stringWidth(title, "NotoSansSC-b", font_size + 6)
        pdf.setFont("NotoSansSC-b", font_size + 6)
        pdf.drawString((width - title_width) / 2, height - 50, title)

        pdf.setFont("NotoSansSC-b", font_size)
        y_position = height - 120
        pdf.drawString(column1_x, y_position, '您的回答: ')
        pdf.setFont("NotoSansSC", font_size)
        y_position -= font_size * 3
            
        for item, answer in self.responses:
            pdf.drawString(column1_x, y_position, f'{self.description(item)}, : , {answer}')
            y_position -= font_size * 1.8

        pdf.setFont("NotoSansSC-b", font_size)
        y_position -= font_size * 1
        pdf.drawString(column1_x, y_position, f'您的社会支持总分为: {total} （最高56分）')
        y_position -= font_size * 3
        pdf.drawString(column1_x, y_position, f'您的客观支持分为: {obj} （最高12分）')
        y_position -= font_size * 3
        pdf.drawString(column1_x, y_position, f'您的主观支持分为: {sub} （最高32分）')
        y_position -= font_size * 3
        pdf.drawString(column1_x, y_position, f'您对支持的利用度为: {ult} （最高12分）')
        y_position -= font_size * 6
        pdf.drawString(column1_x, y_position, "客观支持是指客观可见的支持，如物质支持、社会网络、以及团体关系的存在和参与等")
        y_position -= font_size * 3
        pdf.drawString(column1_x, y_position, "主观支持是指个体在社会中受尊重、被支持、被理解的情感体验")
        y_position -= font_size * 3
        pdf.drawString(column1_x, y_position, "对社会支持的利用度是指个体对可获取的社会支持的利用意愿")


        
        pdf.save()
