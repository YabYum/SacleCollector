from Report import ReportGenerator
from Scorer import PID5Scorer
import sys
import json
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, \
    QScrollArea, QFrame, QLineEdit, QDialog, QFormLayout


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

        self.setWindowTitle("DSM-5人格量表 (PID-5)")
        self.setGeometry(100, 100, 900, 900)
        self.current_page = 0
        self.questions_per_page = 10

        self.layout = QVBoxLayout()
        self.questions_layout = QVBoxLayout()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area_widget = QWidget()
        self.scroll_area_widget.setLayout(self.questions_layout)
        self.scroll_area.setWidget(self.scroll_area_widget)
        self.layout.addWidget(self.scroll_area)

        self.questions = []
        self.responses = {}
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

        label_cn = QLabel(f"{question['item']}. {question['translation']}")
        label_en = QLabel(f" {question['english']}")
        question_layout.addWidget(label_cn)
        question_layout.addWidget(label_en)

        combo_box = QComboBox()
        combo_box.addItem("请选择最符合的一项", None)
        for option in question['options']:
            combo_box.addItem(str(option), option)

        combo_box.currentIndexChanged.connect(lambda _, b=combo_box, q=question['item']: self.record_response(b, q))
        question_layout.addWidget(combo_box)

        question_frame.setLayout(question_layout)
        self.questions_layout.addWidget(question_frame)

    def record_response(self, combo_box, question_item):
        self.responses[question_item] = combo_box.currentData()

    def show_next_page(self):
        self.current_page += 1
        self.show_page(self.current_page)

    def show_prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
        self.show_page(self.current_page)

    def submit_answers(self):
        print("问卷采集已完成！")
        print("Responses:", self.responses)
        raw = self.responses
        scorer = PID5Scorer(raw)
        facet_scores, domain_scores = scorer.get_scores()
        print("facet_scores:", facet_scores, "domain_scores:", domain_scores)

        # Save to JSON
        save_to_json(f"pid_{self.user_id}.json",
                     {"responses": self.responses, "facet_scores": facet_scores, "domain_scores": domain_scores})

        report_generator = ReportGenerator(self.user_id, facet_scores, domain_scores)
        report_generator.generate_pdf()

        self.close()


def main():
    app = QApplication(sys.argv)

    dialog = StartDialog()
    if dialog.exec():
        user_id = dialog.get_id()
        main_window = Survey('PID-5.json')
        main_window.user_id = user_id
        main_window.show()
        main_window.show_page(main_window.current_page)
        sys.exit(app.exec())


if __name__ == "__main__":
    main()
