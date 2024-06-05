import io
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
    def __init__(self, user_id, facet_scores, domain_scores):
        self.user_id = user_id
        self.facet_scores = facet_scores
        self.domain_scores = domain_scores

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
        facet_label = ["快感缺乏", "焦虑", "寻求关注", "麻木", "欺骗", "抑郁", "注意分散", "怪异", "情绪稳定性", "傲慢", "敌对",
                       "冲动", "亲密回避", "不负责任", "操控", "感知失调", "持续", "情感受限", "完美主义", "冒险", "分离焦虑",
                       "顺从", "多疑", "不寻常的信念与经历", "退缩"]
        domain_label = ["负性情感", "解离", "敌意", "失抑制", "精神病性"]
        facet_chart_img = self.plot_radar_chart(list(self.facet_scores.values()), facet_label,
                                                "特质得分")
        domain_chart_img = self.plot_radar_chart(list(self.domain_scores.values()), domain_label,
                                                 "维度得分")

        pdf = canvas.Canvas(f"{self.user_id}_report.pdf", pagesize=letter)
        width, height = letter

        column1_x = 50

        pdf.setFont("NotoSansSC-b", font_size)

        title = "DSM-5 人格量表（PID-5）结果报告"
        title_width = pdf.stringWidth(title, "NotoSansSC-b", font_size + 6)
        pdf.setFont("NotoSansSC-b", font_size + 6)
        pdf.drawString((width - title_width) / 2, height - 50, title)

        pdf.setFont("NotoSansSC-b", font_size)
        y_position = height - 120
        pdf.drawString(column1_x, y_position, '特质得分:')
        pdf.setFont("NotoSansSC", font_size)
        y_position -= font_size * 3
        for facet, score in self.facet_scores.items():
            formatted_score = f"{score:.2f}"
            pdf.drawString(column1_x, y_position, f"{facet}: {formatted_score}")
            y_position -= font_size * 1.8

        pdf.setFont("NotoSansSC-b", font_size)
        y_position -= font_size * 5
        pdf.drawString(column1_x, y_position, '维度得分:')
        pdf.setFont("NotoSansSC", font_size)
        y_position -= font_size * 3
        for domain, score in self.domain_scores.items():
            formatted_score = f"{score:.2f}"
            pdf.drawString(column1_x, y_position, f"{domain}: {formatted_score}")
            y_position -= font_size * 1.6

        image_width = 300
        image_height = 300

        pdf.drawInlineImage(facet_chart_img, 270, 410, width=image_width, height=image_height)
        pdf.drawInlineImage(domain_chart_img, 270, 80, width=image_width, height=image_height)

        pdf.save()


def main():
    user_id = "12345"
    facet_scores = {
        "快感缺乏(Anhedonia)": 2.125,
        "焦虑(Anxiousness)": 1.8888888888888888,
        "寻求关注(Attention Seeking)": 1.375,
        "麻木(Callousness)": 0.42857142857142855,
        "欺骗(Deceitfulness)": 1.0,
        "抑郁(Depressivity)": 1.7142857142857142,
        "注意分散(Distractibility)": 1.5555555555555556,
        "怪异(Eccentricity)": 1.6153846153846154,
        "情绪稳定性(Emotional Lability)": 2.142857142857143,
        "傲慢(Grandiosity)": 2.0,
        "敌对(Hostility)": 1.7,
        "冲动(Impulsivity)": 1.3333333333333333,
        "亲密回避(Intimacy Avoidance)": 0.16666666666666666,
        "不负责任(Irresponsibility)": 1.2857142857142858,
        "操控(Manipulativeness)": 1.0,
        "感知失调(Perceptual Dysregulation)": 0.5,
        "持续性(Perseveration)": 0.7777777777777778,
        "情感受限(Restricted Affectivity)": 2.0,
        "完美主义(Rigid Perfectionism)": 0.8,
        "冒险(Risk Taking)": 0.8571428571428571,
        "分离焦虑(Separation Insecurity)": 1.2857142857142858,
        "顺从(Submissiveness)": 1.0,
        "多疑(Suspiciousness)": 1.4285714285714286,
        "不寻常的信念与经历(Unusual Beliefs & Experiences)": 0.75,
        "退缩(Withdrawal)": 1.9
    }
    domain_scores = {
        "负性情感（Negative Affect）": 1.7724867724867723,
        "解离（Detachment）": 1.3972222222222224,
        "敌意（Antagonism）": 1.3333333333333333,
        "失抑制（Disinhibition）": 1.3915343915343916,
        "精神病性（Psychoticism）": 0.9551282051282052
    }

    report = ReportGenerator(user_id, facet_scores, domain_scores)
    report.generate_pdf()
    print(f"Report for user {user_id} has been generated.")

if __name__ == "__main__":
    main()