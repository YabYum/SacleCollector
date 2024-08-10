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
                return question['brief']
        return None
    
    def scorer(self):
        total = sum(self.num_response.values())
        obj = self.num_response["2"] + self.num_response["13"] + self.num_response["14"]
        sub = (self.num_response["1"] + self.num_response["3"] + self.num_response["4"] + self.num_response["5"] +
               self.num_response["6"] + self.num_response["7"] + self.num_response["8"] + self.num_response["9"])
        ult = self.num_response["10"] + self.num_response["11"] + self.num_response["12"]
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

        for item, answer in self.responses.items():
            pdf.drawString(column1_x, y_position, f'{self.description(item)}  :   {answer}')
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


response = {'1': '一个也没有', '2': '住处经常变动，多数时间和陌生人住在一起', '3': '相互之间从不关心，只是点头之交', '4': '遇到困难可能会稍微关心', '5': '极少', '6': '全力支持', '7': '无', '8': '极少', '9': '极少', '10': '只向关系极为密切的1-2人倾诉', '14': '3-5个', '13': '3-5个', '12': '经常参加', '11': '只靠自己，不接受别人帮助'}
num_res = {'1': 1, '2': 2, '3': 1, '4': 2, '5': 2, '6': 4, '7': 1, '8': 2, '9': 2, '10': 2, '14': 3, '13': 3, '12': 3, '11': 1}
rep = ReportGenerator(1,num_res,response,'SSRS.json')
rep.generate_pdf()
