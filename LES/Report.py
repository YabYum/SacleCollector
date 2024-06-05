import io
import json
import numpy as np
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image
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
    def __init__(self, user_id, num_responses_year, num_responses_week, les_path):
        self.user_id = user_id
        self.impact_year = num_responses_year
        self.impact_week = num_responses_week
        self.les_file_path = les_path
        self.les_data = self.load_les_data()
        self.categories = {'婚姻恋爱': range(1, 18), '家庭生活': range(18, 29), '工作学习': range(29, 41), '社会人际': range(41, 50)}

    def load_les_data(self):
        """Load LES data from a JSON file."""
        with open(self.les_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data

    def categorize_impacts(self, impacts):
        """Categorize impacts into the predefined categories and sum their values."""
        category_impacts = {category: 0 for category in self.categories}
        for category, indices in self.categories.items():
            category_impacts[category] = sum(impacts[str(i)] for i in indices if str(i) in impacts)
        return category_impacts

    def get_event_description(self, item_number):
        """Retrieve the event description from LES data."""
        for question in self.les_data['questions']:
            if question['item'] == str(item_number):
                return question['description']
        return None

    def scocer(self):
        category_year = self.categorize_impacts(self.impact_year)
        category_week = self.categorize_impacts(self.impact_week)
        year_impacts = {self.get_event_description(k): v for k, v in self.impact_year.items() if v != 0}
        week_impacts = {self.get_event_description(k): v for k, v in self.impact_week.items() if v != 0}
        year_total_impact = sum(year_impacts.values())
        week_total_impact = sum(week_impacts.values())
        return category_year, category_week, year_impacts, week_impacts, year_total_impact, week_total_impact

    def plot_radar_chart(self, data, labels, title):
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        data += data[:1]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.fill(angles, data, color='red', alpha=0.25)
        ax.plot(angles, data, color='red', linewidth=2)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, fontsize=12, rotation=45, fontproperties=notolight)
        plt.title(title, size=15, color='black', y=1.1, fontsize=15, fontproperties=notoregu)

        img_data = io.BytesIO()
        plt.savefig(img_data, format='PNG')
        plt.close()
        img_data.seek(0)

        img = Image.open(img_data)
        return img

    def generate_pdf(self, font_size=8):
        label = ["婚姻恋爱", "家庭生活", "工作学习", "社会人际"]
        category_year, category_week, year_impacts, week_impacts, year_total_impact, week_total_impact = self.scocer()

        year_chart_img = self.plot_radar_chart(list(category_year.values()), label, "一年以来的生活事件压力分布图")
        week_chart_img = self.plot_radar_chart(list(category_week.values()), label,"最近一周的生活事件压力分布图")

        pdf = canvas.Canvas(f"{self.user_id}_report.pdf", pagesize=letter)
        width, height = letter

        column1_x = 50

        pdf.setFont("NotoSansSC-b", font_size)

        title = "生活事件量表（LES）结果报告"
        title_width = pdf.stringWidth(title, "NotoSansSC-b", font_size + 6)
        pdf.setFont("NotoSansSC-b", font_size + 6)
        pdf.drawString((width - title_width) / 2, height - 50, title)

        pdf.setFont("NotoSansSC-b", font_size)
        y_position = height - 120
        pdf.drawString(column1_x, y_position, '一年以来对您的生活造成影响的压力事件: ')
        pdf.setFont("NotoSansSC", font_size)
        y_position -= font_size * 3
        options = self.les_data['questions'][0]['options']
        for description, impact in year_impacts.items():
            descriptive_impact = options[impact]  # Convert numerical impact to descriptive text
            pdf.drawString(column1_x, y_position, f"{description}: {descriptive_impact}")
            y_position -= font_size * 1.8

        pdf.setFont("NotoSansSC-b", font_size)
        y_position -= font_size * 1
        pdf.drawString(column1_x, y_position, f'一年以来对您的生活压力总值为: {year_total_impact}')
        pdf.setFont("NotoSansSC", font_size)
        y_position -= font_size * 3

        pdf.setFont("NotoSansSC-b", font_size)
        y_position -= font_size * 3
        pdf.drawString(column1_x, y_position, '最近一周对您的生活造成影响的压力事件:    ')
        pdf.setFont("NotoSansSC", font_size)
        y_position -= font_size * 3
        for description, impact in week_impacts.items():
            descriptive_impact = options[impact]  # Convert numerical impact to descriptive text
            pdf.drawString(column1_x, y_position, f"{description}: {descriptive_impact}")
            y_position -= font_size * 1.8

        pdf.setFont("NotoSansSC-b", font_size)
        y_position -= font_size * 1
        pdf.drawString(column1_x, y_position, f'一周以来对您的生活压力总值为:{week_total_impact}')
        pdf.setFont("NotoSansSC", font_size)
        y_position -= font_size * 3

        image_width = 300
        image_height = 300

        pdf.drawInlineImage(year_chart_img, 270, 410, width=image_width, height=image_height)
        pdf.drawInlineImage(week_chart_img, 270, 80, width=image_width, height=image_height)

        pdf.save()
