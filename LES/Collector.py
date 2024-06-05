import sys
import json
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, \
    QScrollArea, QFrame, QLineEdit, QDialog, QFormLayout
from PyQt6.QtGui import QFont
from Report import ReportGenerator


def save_to_json(filename, data):
    with open(filename, 'w') as fp:
        json.dump(data, fp, indent=4)


class StartDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("输入您的ID")
        self.layout = QFormLayout()
        self.id_input = QLineEdit()
        self.layout.addRow("ID:", self.id_input)
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.layout.addRow(self.ok_button)
        self.setLayout(self.layout)

    def get_id(self):
        return self.id_input.text()


class Survey(QWidget):
    def __init__(self, filename):
        super().__init__()

        self.setWindowTitle("生活事件量表（LES）")
        self.setGeometry(200, 100, 800, 800)
        self.current_page = 0
        self.questions_per_page = 7

        self.layout = QVBoxLayout()
        self.questions_layout = QVBoxLayout()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area_widget = QWidget()
        self.scroll_area_widget.setLayout(self.questions_layout)
        self.scroll_area.setWidget(self.scroll_area_widget)
        self.layout.addWidget(self.scroll_area)

        self.questions = []
        self.responses_year = {}
        self.responses_week = {}
        self.user_id = ""

        # Load questions from the JSON file
        self.load_questions(filename)

        # Navigation buttons
        self.nav_layout = QHBoxLayout()
        self.prev_button = QPushButton('前一页')  # previous page
        self.prev_button.clicked.connect(self.show_prev_page)
        self.prev_button.setEnabled(False)
        self.nav_layout.addWidget(self.prev_button)

        self.next_button = QPushButton('下一页')  # next page
        self.next_button.clicked.connect(self.show_next_page)
        self.nav_layout.addWidget(self.next_button)

        self.submit_button = QPushButton('提交')  # submit
        self.submit_button.clicked.connect(self.submit_answers)
        self.submit_button.setEnabled(False)
        self.nav_layout.addWidget(self.submit_button)

        self.layout.addLayout(self.nav_layout)
        self.setLayout(self.layout)

    def load_questions(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
            self.questions = data['questions']

    def show_page(self, page):
        for i in reversed(range(self.questions_layout.count())):
            widget = self.questions_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        start = page * self.questions_per_page
        end = min(start + self.questions_per_page, len(self.questions))

        for question in self.questions[start:end]:
            self.add_question(question)

        self.prev_button.setEnabled(page > 0)
        self.next_button.setEnabled(end < len(self.questions))
        self.submit_button.setEnabled(end >= len(self.questions))

    def add_question(self, question):
        question_frame = QFrame()
        question_layout = QVBoxLayout()

        label_cn = QLabel(f"{question['item']}. {question['description']}")
        question_layout.addWidget(label_cn)

        # ComboBox for one year
        combo_box_year = QComboBox()
        combo_box_year.addItem("请选择一年以来最符合真实情况的一项", None)
        for option in question['options']:
            combo_box_year.addItem(str(option), option)

        combo_box_year.currentIndexChanged.connect(
            lambda _, b=combo_box_year, q=question['item']: self.record_response(b, q, "year"))
        question_layout.addWidget(combo_box_year)

        # ComboBox for one week
        combo_box_week = QComboBox()
        combo_box_week.addItem("请选择一周以来最符合真实情况的一项", None)
        for option in question['options']:
            combo_box_week.addItem(str(option), option)

        combo_box_week.currentIndexChanged.connect(
            lambda _, b=combo_box_week, q=question['item']: self.record_response(b, q, "week"))
        question_layout.addWidget(combo_box_week)

        question_frame.setLayout(question_layout)
        self.questions_layout.addWidget(question_frame)

    def record_response(self, combo_box, question_item, period):
        if period == "year":
            self.responses_year[question_item] = combo_box.currentData()
        elif period == "week":
            self.responses_week[question_item] = combo_box.currentData()

    def show_next_page(self):
        self.current_page += 1
        self.show_page(self.current_page)

    def show_prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
        self.show_page(self.current_page)

    def submit_answers(self):
        print("问卷采集已完成！")
        mapping = {"没有遇到或无影响": 0, "有轻微影响": 1, "有一定影响": 2, "有较大影响": 3, "影响非常大": 4}
        num_responses_year = {key: mapping[value] for key, value in self.responses_year.items()}
        num_responses_week = {key: mapping[value] for key, value in self.responses_week.items()}

        report = ReportGenerator(self.user_id, num_responses_year, num_responses_week, 'LES.json')
        report.generate_pdf()
        # Save to JSON
        save_to_json(f"les_{self.user_id}.json",
                     {"year": num_responses_year, "week": num_responses_week})
        self.close()


def main():
    app = QApplication(sys.argv)
    default_font = QFont('Arial', 11)
    app.setFont(default_font)
    dialog = StartDialog()
    if dialog.exec():
        user_id = dialog.get_id()
        main_window = Survey('LES.json')
        main_window.user_id = user_id
        main_window.show()
        main_window.show_page(main_window.current_page)
        sys.exit(app.exec())


if __name__ == "__main__":
    main()
