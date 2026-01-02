import sys
import mysql.connector
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidgetItem, QMessageBox,
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, 
    QAbstractItemView, QWidget, QHBoxLayout, QSizePolicy,
    QGridLayout, QScrollArea, QHeaderView, QComboBox,
    QFileDialog, QSpinBox, QDoubleSpinBox, QTextEdit,
    QTabWidget, QGroupBox, QRadioButton, QCheckBox,
    QDateEdit, QDateTimeEdit, QProgressBar, QStatusBar,
    QTableWidget
)
from PyQt5.QtCore import Qt, QDate, QDateTime
from PyQt5.QtGui import QPixmap, QImage
from demo import Ui_MainWindow  # Giao diện tạo từ Qt Designer
import re
import os
from datetime import datetime, timedelta
import json
from decimal import Decimal
from django.contrib.auth.hashers import check_password
from django.conf import settings
if not settings.configured:
    settings.configure(
        PASSWORD_HASHERS=[
            'django.contrib.auth.hashers.PBKDF2PasswordHasher',
            'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
            'django.contrib.auth.hashers.Argon2PasswordHasher',
            'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
        ]
    )



class PlotWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Biểu đồ thống kê (Đã trừ giảm giá - Loại bỏ đơn hàng 0 đồng)")
        self.setGeometry(100, 100, 1200, 800)
        
        # Tạo layout chính
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Tạo scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_layout.addWidget(scroll)
        
        # Widget chứa biểu đồ
        plot_widget = QWidget()
        plot_layout = QVBoxLayout()
        plot_widget.setLayout(plot_layout)
        
        self.figure = plt.figure(figsize=(12, 8))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        plot_layout.addWidget(self.canvas)
        
        scroll.setWidget(plot_widget)
        
        # Thiết lập size policy cho cửa sổ
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def plot_all_charts(self, age_data, product_data, payment_data):
        self.figure.clear()
        
        # Tạo 3 subplot
        ax1 = self.figure.add_subplot(221)  # Biểu đồ doanh thu theo tuổi
        ax2 = self.figure.add_subplot(222)  # Biểu đồ món ăn bán chạy
        ax3 = self.figure.add_subplot(223)  # Biểu đồ tròn phương thức thanh toán
        ax4 = self.figure.add_subplot(224)  # Biểu đồ cột phương thức thanh toán
        
        # === Vẽ biểu đồ doanh thu theo tuổi ===
        names = [item[0] for item in age_data]
        values = [float(item[2]) for item in age_data]
        colors = plt.cm.viridis(np.linspace(0, 1, len(values)))
        bars = ax1.bar(names, values, color=colors)
        ax1.set_title("Doanh thu theo nhóm tuổi", fontsize=12, fontweight='bold')
        ax1.set_xlabel("Nhóm tuổi", fontsize=10)
        ax1.set_ylabel("Doanh thu (K)", fontsize=10)
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}',
                    ha='center', va='bottom', fontsize=8)
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # === Vẽ biểu đồ món ăn bán chạy ===
        names = [item[0] for item in product_data]
        values = [float(item[2]) for item in product_data]  # Số lượng bán
        colors = plt.cm.viridis(np.linspace(0, 1, len(values)))
        bars = ax2.bar(names, values, color=colors)
        ax2.set_title("Số lượng món ăn bán chạy", fontsize=12, fontweight='bold')
        ax2.set_xlabel("Tên món", fontsize=10)
        ax2.set_ylabel("Số lượng", fontsize=10)
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=8)
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # === Vẽ biểu đồ tròn phương thức thanh toán ===
        labels = [item[0] for item in payment_data]
        counts = [item[1] for item in payment_data]
        colors = plt.cm.Paired(np.linspace(0, 1, len(labels)))
        wedges, texts, autotexts = ax3.pie(
            counts, labels=labels, colors=colors, autopct='%1.1f%%',
            startangle=90, pctdistance=0.8
        )
        ax3.set_title("Tỉ lệ phương thức thanh toán", fontsize=12, fontweight='bold')
        for text in texts:
            text.set_fontsize(8)
        for autotext in autotexts:
            autotext.set_fontsize(8)
        
        # === Vẽ biểu đồ cột phương thức thanh toán ===
        methods = [item[0] for item in payment_data]
        amounts = [float(item[2]) for item in payment_data]
        colors = plt.cm.viridis(np.linspace(0, 1, len(amounts)))
        bars = ax4.bar(methods, amounts, color=colors)
        ax4.set_title("Doanh thu theo phương thức thanh toán", fontsize=12, fontweight='bold')
        ax4.set_xlabel("Phương thức", fontsize=10)
        ax4.set_ylabel("Doanh thu (K)", fontsize=10)
        for bar in bars:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}',
                    ha='center', va='bottom', fontsize=8)
        plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Điều chỉnh layout
        self.figure.tight_layout()
        self.canvas.draw()

    def plot_bar_chart(self, data, title, xlabel, ylabel):
        self.figure.clear()
        
        ax = self.figure.add_subplot(111)
        names = [item[0] for item in data]
        values = [float(item[1]) for item in data]
        
        # Tạo màu gradient đẹp hơn
        colors = plt.cm.viridis(np.linspace(0, 1, len(values)))
        
        bars = ax.bar(names, values, color=colors)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        
        # Thêm giá trị trên mỗi cột
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}',
                    ha='center', va='bottom', fontsize=10)
        
        # Xoay nhãn trục x để tránh chồng lấn
        plt.xticks(rotation=45, ha='right')
        
        # Tự động điều chỉnh layout
        self.figure.tight_layout()
        
        self.canvas.draw()

    def plot_grouped_bar_chart(self, grouped_data):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        age_groups = sorted(grouped_data.keys())  # 10s, 20s, 30s, 40+
        all_districts = set()
        for group in grouped_data.values():
            all_districts.update(group.keys())
        all_districts = sorted(all_districts)

        bar_width = 0.1
        x = np.arange(len(age_groups))

        # Vẽ từng quận theo nhóm tuổi
        for i, district in enumerate(all_districts):
            values = [grouped_data[age].get(district, 0) for age in age_groups]
            ax.bar(x + i * bar_width, values, width=bar_width, label=district)

        ax.set_xlabel("Độ tuổi", fontsize=12)
        ax.set_ylabel("Số người dùng", fontsize=12)
        ax.set_title("Số người dùng theo độ tuổi và quận", fontsize=14, fontweight='bold')
        ax.set_xticks(x + bar_width * (len(all_districts) / 2 - 0.5))
        ax.set_xticklabels(age_groups)
        ax.legend(title="Quận", bbox_to_anchor=(1.05, 1), loc='upper left')
        self.figure.tight_layout()
        self.canvas.draw()

    def plot_pie_and_bar(self, count_data, total_data):
        self.figure.clear()

        # ===== Vẽ PIE CHART =====
        ax1 = self.figure.add_subplot(211)  # (2 hàng, 1 cột, plot 1)
        labels = [item[0] for item in count_data]
        counts = [item[1] for item in count_data]
        
        colors = plt.cm.Paired(np.linspace(0, 1, len(labels)))
        
        wedges, texts, autotexts = ax1.pie(
            counts, labels=labels, colors=colors, autopct='%1.1f%%',
            startangle=90, pctdistance=0.8
        )
        
        for text in texts:
            text.set_fontsize(10)
            text.set_fontweight('bold')
        for autotext in autotexts:
            autotext.set_fontsize(10)
            autotext.set_fontweight('bold')
        
        ax1.set_title("Tỉ lệ phương thức thanh toán (%)", fontsize=14, fontweight='bold')
        ax1.axis('equal')  # Hình tròn đều

        # ===== Vẽ BAR CHART =====
        ax2 = self.figure.add_subplot(212)  # (2 hàng, 1 cột, plot 2)
        methods = [item[0] for item in total_data]
        totals = [float(item[1]) for item in total_data]
        
        colors_bar = plt.cm.viridis(np.linspace(0, 1, len(totals)))
        
        bars = ax2.bar(methods, totals, color=colors_bar)
        ax2.set_title("Tổng tiền theo phương thức thanh toán", fontsize=14, fontweight='bold')
        ax2.set_xlabel("Phương thức", fontsize=12)
        ax2.set_ylabel("Tổng tiền (K)", fontsize=12)

        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                     f'{height:.2f}', ha='center', va='bottom', fontsize=10)
        
        ax2.tick_params(axis='x', rotation=45)

        self.figure.tight_layout()
        self.canvas.draw()
            
class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Admin Login")
        self.resize(300, 150)

        layout = QVBoxLayout()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password_input)

        login_button = QPushButton("Login")
        login_button.clicked.connect(self.attempt_login)
        layout.addWidget(login_button)

        self.setLayout(layout)
        self.is_authenticated = False
        self.admin_user = None

    def attempt_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='68686868',
                database='food'
            )
            cursor = conn.cursor(dictionary=True)

            # Lấy user theo username (không kiểm tra mật khẩu trong SQL)
            query = """
            SELECT * FROM home_user
            WHERE username = %s AND is_staff = TRUE
            """
            cursor.execute(query, (username,))
            user = cursor.fetchone()

            cursor.close()
            conn.close()

            # So sánh mật khẩu người dùng nhập với mật khẩu đã hash trong DB
            if user and check_password(password, user['password']):
                self.is_authenticated = True
                self.admin_user = user
                QMessageBox.information(self, "Thành công", "Đăng nhập thành công (Staff)")
                self.accept()
                # Hiển thị cửa sổ chính
            else:
                QMessageBox.warning(self, "Thất bại", "Sai mật khẩu hoặc không có quyền truy cập!")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))



class ProductDialog(QDialog):
    def __init__(self, parent=None, product_data=None):
        super().__init__(parent)
        self.setWindowTitle("Thêm/Sửa sản phẩm")
        self.setModal(True)
        self.product_data = product_data
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()

        # Group thông tin sản phẩm
        info_group = QGroupBox("Thông tin sản phẩm")
        form_layout = QGridLayout()

        # Tên sản phẩm
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Nhập tên sản phẩm...")
        form_layout.addWidget(QLabel("Tên sản phẩm:"), 0, 0)
        form_layout.addWidget(self.name_edit, 0, 1)

        # Hình ảnh
        self.image_url_edit = QLineEdit()
        self.image_url_edit.setPlaceholderText("Dán URL hình ảnh...")
        form_layout.addWidget(QLabel("URL hình ảnh:"), 1, 0)
        form_layout.addWidget(self.image_url_edit, 1, 1)

        # Preview hình ảnh
        self.image_preview = QLabel()
        self.image_preview.setFixedSize(120, 120)
        self.image_preview.setStyleSheet("border:1px solid #ccc;background:#fafafa;")
        form_layout.addWidget(self.image_preview, 1, 2, 3, 1)
        self.image_url_edit.textChanged.connect(self.update_image_preview)

        # Mô tả
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Mô tả sản phẩm...")
        form_layout.addWidget(QLabel("Mô tả:"), 2, 0)
        form_layout.addWidget(self.description_edit, 2, 1)

        # Giá
        self.price_edit = QDoubleSpinBox()
        self.price_edit.setMaximum(1000000)
        self.price_edit.setSuffix(" K")
        form_layout.addWidget(QLabel("Giá:"), 3, 0)
        form_layout.addWidget(self.price_edit, 3, 1)

        # Số lượng
        self.stock_edit = QSpinBox()
        self.stock_edit.setMaximum(1000)
        form_layout.addWidget(QLabel("Số lượng:"), 4, 0)
        form_layout.addWidget(self.stock_edit, 4, 1)

        # Danh mục
        self.category_combo = QComboBox()
        self.category_combo.addItems(['Món ăn', 'Nước uống', 'Thức ăn nhanh'])
        form_layout.addWidget(QLabel("Danh mục:"), 5, 0)
        form_layout.addWidget(self.category_combo, 5, 1)

        info_group.setLayout(form_layout)
        main_layout.addWidget(info_group)

        # Thông báo lỗi
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color:red;font-weight:bold;")
        main_layout.addWidget(self.error_label)

        # Nút
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("Lưu")
        cancel_btn = QPushButton("Hủy")
        save_btn.clicked.connect(self.validate_and_accept)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addStretch()
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)

        if self.product_data:
            self.load_product_data()
        self.name_edit.setFocus()

    def update_image_preview(self):
        url = self.image_url_edit.text().strip()
        if url:
            try:
                from urllib.request import urlopen
                from PyQt5.QtGui import QPixmap
                data = urlopen(url).read()
                pixmap = QPixmap()
                pixmap.loadFromData(data)
                self.image_preview.setPixmap(pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            except Exception:
                self.image_preview.setText("Không tải được ảnh")
        else:
            self.image_preview.clear()

    def validate_and_accept(self):
        if not self.name_edit.text().strip():
            self.error_label.setText("Tên sản phẩm không được để trống!")
            self.name_edit.setFocus()
            return
        if not self.image_url_edit.text().strip():
            self.error_label.setText("URL hình ảnh không được để trống!")
            self.image_url_edit.setFocus()
            return
        self.error_label.clear()
        self.accept()

    def load_product_data(self):
        self.name_edit.setText(self.product_data.get('name', ''))
        self.image_url_edit.setText(self.product_data.get('image_url', ''))
        self.description_edit.setText(self.product_data.get('description', ''))
        self.price_edit.setValue(float(self.product_data.get('price', 0)))
        self.stock_edit.setValue(int(self.product_data.get('stock_quantity', 0)))
        category_index = self.category_combo.findText(self.product_data.get('category', ''))
        if category_index >= 0:
            self.category_combo.setCurrentIndex(category_index)
        self.update_image_preview()

    def get_product_data(self):
        # Map tiếng Việt sang giá trị chuẩn
        category_map = {
            'Món ăn': 'food',
            'Nước uống': 'drink',
            'Thức ăn nhanh': 'fastfood'
        }
        category_vn = self.category_combo.currentText()
        category = category_map.get(category_vn, 'food')  # Mặc định là food nếu không khớp
        return {
            'name': self.name_edit.text(),
            'image_url': self.image_url_edit.text(),
            'description': self.description_edit.toPlainText(),
            'price': self.price_edit.value(),
            'stock_quantity': self.stock_edit.value(),
            'category': category
        }

class OrderDialog(QDialog):
    def __init__(self, parent=None, order_data=None):
        super().__init__(parent)
        self.setWindowTitle("Chi tiết đơn hàng")
        self.setModal(True)
        self.order_data = order_data
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()

        # Thông tin khách hàng
        self.customer_info_label = QLabel()
        self.customer_info_label.setStyleSheet("font-size:13px;font-weight:bold;color:#1976d2;")
        main_layout.addWidget(self.customer_info_label)

        # Group thông tin đơn hàng
        info_group = QGroupBox("Thông tin đơn hàng")
        info_layout = QGridLayout()
        self.order_id_label = QLabel()
        self.order_id_label.setStyleSheet("font-weight:bold;font-size:15px;")
        info_layout.addWidget(self.order_id_label, 0, 0, 1, 2)
        self.payment_status = QCheckBox("Đã thanh toán")
        self.payment_status.setStyleSheet("font-size:13px;padding:4px 0;")
        info_layout.addWidget(self.payment_status, 1, 0, 1, 2)
        self.total_amount_label = QLabel()
        self.total_amount_label.setStyleSheet("font-weight:bold;color:#1976d2;")
        info_layout.addWidget(self.total_amount_label, 2, 0, 1, 2)
        self.discount_label = QLabel()
        self.discount_label.setStyleSheet("font-weight:bold;color:#388e3c;")
        info_layout.addWidget(self.discount_label, 3, 0, 1, 2)
        self.final_amount_label = QLabel()
        self.final_amount_label.setStyleSheet("font-weight:bold;color:#d32f2f;font-size:14px;")
        info_layout.addWidget(self.final_amount_label, 4, 0, 1, 2)
        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group)

        # Group bảng sản phẩm
        items_group = QGroupBox("Sản phẩm trong đơn hàng")
        items_layout = QVBoxLayout()
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(4)
        self.items_table.setHorizontalHeaderLabels(["Sản phẩm", "Số lượng", "Đơn giá", "Thành tiền"])
        self.items_table.horizontalHeader().setStyleSheet("background:#e3f2fd;font-weight:bold;")
        self.items_table.setStyleSheet("QTableWidget {border-radius:8px;border:1px solid #bdbdbd;} QTableWidget::item {padding:6px;}")
        self.items_table.setAlternatingRowColors(True)
        self.items_table.setEditTriggers(QTableWidget.NoEditTriggers)
        items_layout.addWidget(self.items_table)
        items_group.setLayout(items_layout)
        main_layout.addWidget(items_group)

        # Nút
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("Lưu")
        save_btn.setStyleSheet("background:#1976d2;color:white;font-weight:bold;border-radius:6px;padding:6px 18px;font-size:14px;")
        cancel_btn = QPushButton("Đóng")
        cancel_btn.setStyleSheet("background:#bdbdbd;color:black;font-weight:bold;border-radius:6px;padding:6px 18px;font-size:14px;")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addStretch()
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)

        if self.order_data:
            self.load_order_data()

    def load_order_data(self):
        # Hiển thị thông tin khách hàng
        username = self.order_data.get('username', '')
        phone = self.order_data.get('phone', '')
        address = self.order_data.get('address', '')
        self.customer_info_label.setText(f"Khách: <b>{username}</b> | SĐT: <b>{phone}</b> | Địa chỉ: <b>{address}</b>")
        self.order_id_label.setText(f"Đơn hàng #{self.order_data.get('id', '')}")
        self.payment_status.setChecked(self.order_data.get('is_paid', False))
        self.total_amount_label.setText(f"Tổng tiền: {self.order_data.get('total_amount', 0):,.2f}K")
        self.discount_label.setText(f"Giảm giá: {self.order_data.get('discount', 0)}%")
        total = Decimal(str(self.order_data.get('total_amount', 0)))
        discount = Decimal(str(self.order_data.get('discount', 0)))
        final = total * (Decimal('1.00') - discount / Decimal('100'))
        self.final_amount_label.setText(f"Thành tiền: {final:,.2f}K")
        # Load items
        items = self.order_data.get('items', [])
        self.items_table.setRowCount(len(items))
        for i, item in enumerate(items):
            self.items_table.setItem(i, 0, QTableWidgetItem(item.get('product_name', '')))
            self.items_table.setItem(i, 1, QTableWidgetItem(str(item.get('quantity', 0))))
            self.items_table.setItem(i, 2, QTableWidgetItem(f"{item.get('price', 0):,.2f}K"))
            self.items_table.setItem(i, 3, QTableWidgetItem(f"{item.get('total', 0):,.2f}K"))
        self.items_table.resizeColumnsToContents()
        self.items_table.resizeRowsToContents()
        # Cột 0 (Sản phẩm) co giãn, các cột còn lại vừa đủ
        header = self.items_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

    def get_order_data(self):
        return {
            'is_paid': self.payment_status.isChecked()
        }

class UserDialog(QDialog):
    def __init__(self, parent=None, user_data=None):
        super().__init__(parent)
        self.setWindowTitle("Thông tin người dùng")
        self.setModal(True)
        self.user_data = user_data
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Username
        self.username_edit = QLineEdit()
        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.username_edit)
        
        # Email
        self.email_edit = QLineEdit()
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.email_edit)
        
        # Phone
        self.phone_edit = QLineEdit()
        layout.addWidget(QLabel("Số điện thoại:"))
        layout.addWidget(self.phone_edit)
        
        # Age
        self.age_edit = QSpinBox()
        self.age_edit.setMaximum(100)
        layout.addWidget(QLabel("Tuổi:"))
        layout.addWidget(self.age_edit)
        
        # Address
        self.address_edit = QLineEdit()
        layout.addWidget(QLabel("Địa chỉ:"))
        layout.addWidget(self.address_edit)
        
        # Membership points
        self.points_edit = QSpinBox()
        self.points_edit.setMaximum(10000)
        layout.addWidget(QLabel("Điểm thành viên:"))
        layout.addWidget(self.points_edit)
        
        # Staff status
        self.staff_checkbox = QCheckBox("Staff status")
        layout.addWidget(self.staff_checkbox)
        
        # Nút
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("Lưu")
        cancel_btn = QPushButton("Hủy")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        if self.user_data:
            self.load_user_data()

    def load_user_data(self):
        self.username_edit.setText(self.user_data.get('username', ''))
        self.email_edit.setText(self.user_data.get('email', ''))
        self.phone_edit.setText(self.user_data.get('phone', ''))
        self.age_edit.setValue(int(self.user_data.get('age', 0)))
        self.address_edit.setText(self.user_data.get('address', ''))
        self.points_edit.setValue(int(self.user_data.get('membership_points', 0)))
        self.staff_checkbox.setChecked(bool(self.user_data.get('is_staff', False)))

    def get_user_data(self):
        return {
            'username': self.username_edit.text(),
            'email': self.email_edit.text(),
            'phone': self.phone_edit.text(),
            'age': self.age_edit.value(),
            'address': self.address_edit.text(),
            'membership_points': self.points_edit.value(),
            'is_staff': self.staff_checkbox.isChecked()
        }

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Thiết lập size policy cho cửa sổ chính
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Thiết lập size policy cho table
        self.ui.tableWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.ui.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.ui.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Interactive)
        
        # Thêm status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # Thêm nút mới
        self.ui.btn_add_product = QPushButton("Thêm sản phẩm")
        self.ui.btn_edit_product = QPushButton("Sửa sản phẩm")
        self.ui.btn_delete_product = QPushButton("Xóa sản phẩm")
        self.ui.btn_edit_user = QPushButton("Sửa thông tin")
        
        # Thêm nút vào layout
        self.ui.horizontalLayout.addWidget(self.ui.btn_add_product)
        self.ui.horizontalLayout.addWidget(self.ui.btn_edit_product)
        self.ui.horizontalLayout.addWidget(self.ui.btn_delete_product)
        self.ui.horizontalLayout.addWidget(self.ui.btn_edit_user)
        
        # Kết nối sự kiện
        self.ui.btn_add_product.clicked.connect(self.add_product)
        self.ui.btn_edit_product.clicked.connect(self.edit_product)
        self.ui.btn_delete_product.clicked.connect(self.delete_product)
        self.ui.btn_edit_user.clicked.connect(self.edit_user)
        
        self.admin_user = None

        # Gắn sự kiện
        self.ui.btn_product.clicked.connect(self.show_products)
        self.ui.btn_order.clicked.connect(self.show_orders)
        self.ui.btn_order_item.clicked.connect(self.show_order_items)
        self.ui.btn_payment.clicked.connect(self.show_payments)
        self.ui.btn_product_sales.clicked.connect(self.show_revenue_by_age)
        self.ui.btn_user.clicked.connect(self.show_users)
        self.ui.actionLogin.triggered.connect(self.check_login)
        self.ui.actionLogout.triggered.connect(self.logout)
        self.ui.actionExit.triggered.connect(self.close)
        self.ui.btn_login.clicked.connect(self.toggle_login)
        self.ui.actionLogout.triggered.connect(self.logout)

        self.ui.tableWidget.itemChanged.connect(self.handle_item_changed)
        self.ui.tableWidget.itemDoubleClicked.connect(self.handle_item_double_clicked)

        self.update_login_status()
        self.setup_table_headers()
        
        # Thiết lập window state
        self.showMaximized()

    def connect_to_db(self):
        return mysql.connector.connect(
            host='localhost',
            user='root',
            password='68686868',
            database='food'
        )

    def toggle_login(self):
        if self.admin_user:
            self.logout()
        else:
            self.check_login()

    def logout(self):
        if self.admin_user:
            self.admin_user = None
            self.update_login_status()
            # Xóa dữ liệu trong bảng và header
            self.ui.tableWidget.clearContents()
            self.ui.tableWidget.setRowCount(0)
            self.ui.tableWidget.setColumnCount(0)
            self.ui.tableWidget.setHorizontalHeaderLabels([])
            self.statusBar.showMessage("")
            # Đóng tất cả các cửa sổ biểu đồ nếu đang mở
            for widget in QApplication.topLevelWidgets():
                if isinstance(widget, PlotWindow):
                    widget.close()
            QMessageBox.information(self, "Đăng xuất", "Bạn đã đăng xuất")

    def check_login(self):
        dialog = LoginDialog(self)
        if dialog.exec_() == QDialog.Accepted and dialog.is_authenticated:
            self.admin_user = dialog.admin_user
        self.update_login_status()

    def update_login_status(self):
        if self.admin_user:
            self.ui.lbl_user_info.setText(f"Đăng nhập: {self.admin_user['username']}")
            self.ui.btn_login.setText("Đăng xuất")
        else:
            self.ui.lbl_user_info.setText("Chưa đăng nhập")
            self.ui.btn_login.setText("Đăng nhập")

    def setup_table_headers(self):
        self.ui.tableWidget.setEditTriggers(QAbstractItemView.DoubleClicked)

    def show_data(self, data, headers=None):
        table = self.ui.tableWidget
        table.blockSignals(True)
        table.clear()
        if headers:
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(data))
        
        # Tính toán kích thước cột
        total_width = table.viewport().width()
        col_width = total_width // len(headers) if headers else 100
        
        for row_idx, row_data in enumerate(data):
            for col_idx, item in enumerate(row_data):
                cell = QTableWidgetItem(str(item))
                if col_idx == 0:
                    cell.setFlags(Qt.ItemIsEnabled)  # Không cho chỉnh ID
                table.setItem(row_idx, col_idx, cell)
                
                # Thiết lập kích thước cột
                if headers:
                    table.setColumnWidth(col_idx, col_width)
        
        # Tự động điều chỉnh chiều cao hàng
        table.resizeRowsToContents()
        table.blockSignals(False)

    def query_data(self, query):
        conn = self.connect_to_db()
        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data

    def show_chart(self, data, title, xlabel, ylabel):
        self.plot_window = PlotWindow()
        self.plot_window.plot_bar_chart(data, title, xlabel, ylabel)
        self.plot_window.show()

    def handle_item_changed(self, item):
        if not self.admin_user:
            return

        row = item.row()
        col = item.column()
        if col not in [2, 3]:  # Chỉ cho phép chỉnh "Giá" và "Số lượng"
            return

        product_id = self.ui.tableWidget.item(row, 0).text()
        new_value = item.text()

        try:
            new_value = float(new_value) if col == 2 else int(new_value)
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Giá trị không hợp lệ")
            self.show_products()
            return

        column_name = "price" if col == 2 else "stock_quantity"
        update_query = f"UPDATE home_product SET {column_name} = %s WHERE id = %s"

        try:
            conn = self.connect_to_db()
            cursor = conn.cursor()
            cursor.execute(update_query, (new_value, product_id))
            conn.commit()
            cursor.close()
            conn.close()
            QMessageBox.information(self, "Cập nhật", "Cập nhật thành công")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", str(e))

    def add_product(self):
        if not self.admin_user:
            QMessageBox.warning(self, "Lỗi", "Vui lòng đăng nhập với quyền admin")
            return
            
        dialog = ProductDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            product_data = dialog.get_product_data()
            try:
                conn = self.connect_to_db()
                cursor = conn.cursor()
                query = """
                INSERT INTO home_product (name, image_url, description, price, stock_quantity, category)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    product_data['name'],
                    product_data['image_url'],
                    product_data['description'],
                    product_data['price'],
                    product_data['stock_quantity'],
                    product_data['category']
                ))
                conn.commit()
                cursor.close()
                conn.close()
                QMessageBox.information(self, "Thành công", "Thêm sản phẩm thành công")
                self.show_products()
            except Exception as e:
                QMessageBox.warning(self, "Lỗi", str(e))

    def edit_product(self):
        if not self.admin_user:
            QMessageBox.warning(self, "Lỗi", "Vui lòng đăng nhập với quyền admin")
            return
            
        current_row = self.ui.tableWidget.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn sản phẩm cần sửa")
            return
            
        product_id = self.ui.tableWidget.item(current_row, 0).text()
        try:
            conn = self.connect_to_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM home_product WHERE id = %s", (product_id,))
            product_data = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if product_data:
                dialog = ProductDialog(self, product_data)
                if dialog.exec_() == QDialog.Accepted:
                    updated_data = dialog.get_product_data()
                    # Tạo lại kết nối mới để update
                    conn = self.connect_to_db()
                    cursor = conn.cursor()
                    query = """
                    UPDATE home_product 
                    SET name = %s, image_url = %s, description = %s, 
                        price = %s, stock_quantity = %s, category = %s
                    WHERE id = %s
                    """
                    cursor.execute(query, (
                        updated_data['name'],
                        updated_data['image_url'],
                        updated_data['description'],
                        updated_data['price'],
                        updated_data['stock_quantity'],
                        updated_data['category'],
                        product_id
                    ))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    QMessageBox.information(self, "Thành công", "Cập nhật sản phẩm thành công")
                    self.show_products()
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", str(e))

    def delete_product(self):
        if not self.admin_user:
            QMessageBox.warning(self, "Lỗi", "Vui lòng đăng nhập với quyền admin")
            return
            
        current_row = self.ui.tableWidget.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn sản phẩm cần xóa")
            return
            
        product_id = self.ui.tableWidget.item(current_row, 0).text()
        reply = QMessageBox.question(self, "Xác nhận", 
                                   "Bạn có chắc muốn xóa sản phẩm này?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                conn = self.connect_to_db()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM home_product WHERE id = %s", (product_id,))
                conn.commit()
                cursor.close()
                conn.close()
                QMessageBox.information(self, "Thành công", "Xóa sản phẩm thành công")
                self.show_products()
            except Exception as e:
                QMessageBox.warning(self, "Lỗi", str(e))

    def view_order_details(self):
        current_row = self.ui.tableWidget.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn đơn hàng cần xem")
            return
            
        order_id = self.ui.tableWidget.item(current_row, 0).text()
        try:
            conn = self.connect_to_db()
            cursor = conn.cursor(dictionary=True)
            
            # Lấy thông tin đơn hàng
            cursor.execute("""
                SELECT o.*, u.username, u.phone, u.address
                FROM home_order o
                JOIN home_user u ON o.user_id = u.id
                WHERE o.id = %s
            """, (order_id,))
            order_data = cursor.fetchone()
            
            if order_data:
                # Lấy chi tiết sản phẩm trong đơn hàng
                cursor.execute("""
                    SELECT oi.*, p.name as product_name, p.price
                    FROM home_orderitem oi
                    JOIN home_product p ON oi.product_id = p.id
                    WHERE oi.order_id = %s
                """, (order_id,))
                items = cursor.fetchall()
                order_data['items'] = items
                
                dialog = OrderDialog(self, order_data)
                if dialog.exec_() == QDialog.Accepted:
                    updated_data = dialog.get_order_data()
                    cursor.execute("""
                        UPDATE home_order 
                        SET is_paid = %s
                        WHERE id = %s
                    """, (updated_data['is_paid'], order_id))
                    conn.commit()
                    QMessageBox.information(self, "Thành công", "Cập nhật trạng thái đơn hàng thành công")
                    self.show_orders()
            
            cursor.close()
            conn.close()
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", str(e))

    def edit_user(self):
        if not self.admin_user:
            QMessageBox.warning(self, "Lỗi", "Vui lòng đăng nhập với quyền admin")
            return
            
        current_row = self.ui.tableWidget.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn người dùng cần sửa")
            return
            
        user_id = self.ui.tableWidget.item(current_row, 0).text()
        try:
            conn = self.connect_to_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM home_user WHERE id = %s", (user_id,))
            user_data = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user_data:
                dialog = UserDialog(self, user_data)
                if dialog.exec_() == QDialog.Accepted:
                    updated_data = dialog.get_user_data()
                    # Tạo lại kết nối mới để update
                    conn = self.connect_to_db()
                    cursor = conn.cursor()
                    query = """
                    UPDATE home_user 
                    SET username = %s, email = %s, phone = %s, 
                        age = %s, address = %s, 
                        membership_points = %s,
                        is_staff = %s
                    WHERE id = %s
                    """
                    cursor.execute(query, (
                        updated_data['username'],
                        updated_data['email'],
                        updated_data['phone'],
                        updated_data['age'],
                        updated_data['address'],
                        updated_data['membership_points'],
                        updated_data['is_staff'],
                        user_id
                    ))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    QMessageBox.information(self, "Thành công", "Cập nhật thông tin người dùng thành công")
                    self.show_users()
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", str(e))

    def handle_item_double_clicked(self, item):
        current_tab = self.ui.tabWidget.currentIndex()
        if current_tab == 0:  # Products tab
            self.edit_product()
        elif current_tab == 1:  # Orders tab
            self.view_order_details()
        elif current_tab == 2:  # Users tab
            self.edit_user()

    def show_products(self):
        query = """
        SELECT id, name, price, stock_quantity, category, 
               image_url, description 
        FROM home_product
        ORDER BY id
        """
        data = self.query_data(query)
        headers = ["ID", "Tên sản phẩm", "Giá", "Số lượng", "Danh mục", "Hình ảnh", "Mô tả"]
        self.show_data(data, headers)
        self.statusBar.showMessage(f"Tổng số sản phẩm: {len(data)}")

    def show_orders(self):
        query = """
        SELECT o.id, u.username, o.total_amount, o.discount, COUNT(oi.id) as item_count
        FROM home_order o
        JOIN home_user u ON o.user_id = u.id
        LEFT JOIN home_orderitem oi ON o.id = oi.order_id
        WHERE o.is_paid = True
        GROUP BY o.id, u.username, o.total_amount, o.discount
        ORDER BY o.id DESC
        """
        data = self.query_data(query)
        # Chuyển đổi dữ liệu để hiển thị thông tin giảm giá
        formatted_data = []
        for row in data:
            order_id, username, total_amount, discount, item_count = row
            discount_info = f"Giảm {discount}% (Đơn > 800K)" if total_amount > 800 else "Không giảm giá"
            formatted_data.append((order_id, username, total_amount, discount_info, item_count))
            
        headers = ["Mã đơn", "Khách hàng", "Tổng tiền", "Giảm giá", "Số lượng món"]
        self.show_data(formatted_data, headers)
        self.statusBar.showMessage(f"Tổng số đơn hàng đã thanh toán: {len(data)}")

    def show_users(self):
        query = """
        SELECT id, username, email, phone, age, address, membership_points
        FROM home_user
        ORDER BY id
        """
        data = self.query_data(query)
        headers = ["ID", "Username", "Email", "Số điện thoại", 
                  "Tuổi", "Địa chỉ", "Điểm thành viên"]
        self.show_data(data, headers)
        self.statusBar.showMessage(f"Tổng số người dùng: {len(data)}")

        # === Thống kê nhóm tuổi - quận ===
        age_district_data = {}
        known_districts = [
            'thủ đức', 'tân phú', 'gò vấp', 'bình thạnh', 'phú nhuận',
            'bình tân', 'tân bình'
        ]
        for user in data:
            # 0: id, 1: username, 2: email, 3: phone, 4: age, 5: address, 6: điểm thành viên
            age = user[4]
            address = (user[5] or "").strip().lower()
            if age is None:
                continue
            if age < 20:
                age_group = '10+'
            elif age < 30:
                age_group = '20+'
            elif age < 40:
                age_group = '30+'
            else:
                age_group = '40+'
            district = "không rõ"
            match = re.search(r'(quận|quan)[^\d]*(\d+)', address)
            if match:
                district = f"quận {int(match.group(2))}"
            else:
                match_text = re.search(r'(quận|quan)\s+([a-zà-ỹ\s\-]+)', address)
                if match_text:
                    raw_name = match_text.group(2).strip()
                    # Cắt tên quận nếu có các từ khóa đặc biệt phía sau
                    for stop_word in ['tp', 'tphcm', 'tỉnh', 'thành phố', ',']:
                        idx = raw_name.find(stop_word)
                        if idx != -1:
                            raw_name = raw_name[:idx].strip()
                    district = f"quận {raw_name}"
                else:
                    for name in known_districts:
                        if name in address:
                            district = f"quận {name}"
                            break
            if age_group not in age_district_data:
                age_district_data[age_group] = {}
            if district not in age_district_data[age_group]:
                age_district_data[age_group][district] = 0
            age_district_data[age_group][district] += 1

        # Vẽ biểu đồ
        self.plot_window = PlotWindow()
        self.plot_window.plot_grouped_bar_chart(age_district_data)
        self.plot_window.show()

    def show_payments(self):
        query = """
        SELECT p.id, p.payment_method, o.id as order_id, u.username, p.amount as payment_amount
        FROM home_payment p
        JOIN home_order o ON p.order_id = o.id
        JOIN home_user u ON o.user_id = u.id
        ORDER BY p.id DESC
        """
        data = self.query_data(query)
        headers = ["Mã thanh toán", "Phương thức", "Mã đơn", "Khách hàng", "Số tiền thanh toán"]
        self.show_data(data, headers)
        self.statusBar.showMessage(f"Tổng số thanh toán: {len(data)}")

    def show_revenue_by_age(self):
        # Kiểm tra tổng doanh thu từ bảng thanh toán
        total_payment_check = """
        SELECT 
            COUNT(DISTINCT o.id) as total_orders,
            SUM(oi.quantity * p.price * (1 - o.discount/100)) as total_revenue
        FROM home_order o
        JOIN home_orderitem oi ON o.id = oi.order_id
        JOIN home_product p ON oi.product_id = p.id
        WHERE o.is_paid = True AND o.total_amount > 0
        """
        total_check = self.query_data(total_payment_check)
        total_orders, total_revenue = total_check[0]
        
        # Thống kê doanh thu theo nhóm tuổi
        age_query = """
        SELECT 
            CASE 
                WHEN u.age BETWEEN 10 AND 19 THEN '10+'
                WHEN u.age BETWEEN 20 AND 29 THEN '20+'
                WHEN u.age BETWEEN 30 AND 39 THEN '30+'
                ELSE '40+'
            END AS age_group,
            COUNT(DISTINCT o.id) as order_count,
            SUM(oi.quantity * p.price * (1 - o.discount/100)) as revenue
        FROM home_order o
        JOIN home_user u ON o.user_id = u.id
        JOIN home_orderitem oi ON o.id = oi.order_id
        JOIN home_product p ON oi.product_id = p.id
        WHERE o.is_paid = True AND o.total_amount > 0
        GROUP BY age_group
        ORDER BY age_group
        """
        age_data = self.query_data(age_query)
        
        # Thống kê món ăn bán chạy
        product_query = """
        SELECT 
            p.name as product_name,
            COUNT(DISTINCT o.id) as total_orders,
            SUM(oi.quantity) as total_quantity,
            SUM(oi.quantity * p.price * (1 - o.discount/100)) as total_revenue
        FROM home_orderitem oi
        JOIN home_product p ON oi.product_id = p.id
        JOIN home_order o ON oi.order_id = o.id
        WHERE o.is_paid = True AND o.total_amount > 0
        GROUP BY p.id, p.name
        ORDER BY total_quantity DESC
        """
        product_data = self.query_data(product_query)

        # Thống kê doanh thu theo phương thức thanh toán
        payment_query = """
        SELECT 
            p.payment_method,
            COUNT(DISTINCT o.id) as payment_count,
            SUM(oi.quantity * pr.price * (1 - o.discount/100)) as total_amount
        FROM home_payment p
        JOIN home_order o ON p.order_id = o.id
        JOIN home_orderitem oi ON o.id = oi.order_id
        JOIN home_product pr ON oi.product_id = pr.id
        WHERE o.is_paid = True AND o.total_amount > 0
        GROUP BY p.payment_method
        ORDER BY total_amount DESC
        """
        payment_data = self.query_data(payment_query)
        
        # Hiển thị dữ liệu trong bảng
        all_data = []
        
        # Thêm thông tin tổng doanh thu
        all_data.append(("=== TỔNG DOANH THU TỪ BẢNG THANH TOÁN ===", "", "", ""))
        all_data.append(("Tổng số đơn hàng", "Tổng doanh thu", "", ""))
        all_data.append((f"{total_orders:,}", f"{float(total_revenue):,.2f}K", "", ""))
        all_data.append(("", "", "", ""))
        
        # Thêm tiêu đề cho thống kê theo nhóm tuổi
        all_data.append(("=== THỐNG KÊ DOANH THU THEO NHÓM TUỔI ===", "", "", ""))
        all_data.append(("Nhóm tuổi", "Số đơn hàng", "Doanh thu", ""))
        total_age_revenue = 0
        total_age_orders = 0
        for row in age_data:
            age_group, order_count, revenue = row
            total_age_revenue += float(revenue)
            total_age_orders += order_count
            all_data.append((age_group, f"{order_count:,}", f"{float(revenue):,.2f}K", ""))
        all_data.append(("TỔNG CỘNG", f"{total_age_orders:,}", f"{total_age_revenue:,.2f}K", ""))
            
        # Thêm khoảng trống
        all_data.append(("", "", "", ""))
        
        # Thêm tiêu đề cho thống kê món ăn bán chạy
        all_data.append(("=== THỐNG KÊ TẤT CẢ MÓN ĂN ===", "", "", ""))
        all_data.append(("Tên món", "Số đơn", "Số lượng", "Doanh thu"))
        total_product_revenue = 0
        total_product_orders = 0
        total_product_quantity = 0
        for row in product_data:
            name, orders, quantity, revenue = row
            total_product_revenue += float(revenue)
            total_product_orders += orders
            total_product_quantity += quantity
            all_data.append((name, f"{orders:,}", f"{quantity:,}", f"{float(revenue):,.2f}K"))
        all_data.append(("TỔNG CỘNG", f"{total_product_orders:,}", f"{total_product_quantity:,}", f"{total_product_revenue:,.2f}K"))

        # Thêm khoảng trống
        all_data.append(("", "", "", ""))
        
        # Thêm tiêu đề cho thống kê phương thức thanh toán
        all_data.append(("=== THỐNG KÊ DOANH THU THEO PHƯƠNG THỨC THANH TOÁN ===", "", "", ""))
        all_data.append(("Phương thức", "Số giao dịch", "Tổng doanh thu", ""))
        total_payment_revenue = 0
        total_payment_count = 0
        for row in payment_data:
            method, count, amount = row
            total_payment_revenue += float(amount)
            total_payment_count += count
            all_data.append((method, f"{count:,}", f"{float(amount):,.2f}K", ""))
        all_data.append(("TỔNG CỘNG", f"{total_payment_count:,}", f"{total_payment_revenue:,.2f}K", ""))
            
        headers = ["", "", "", ""]
        self.show_data(all_data, headers)
        
        # Hiển thị biểu đồ
        self.plot_window = PlotWindow()
        self.plot_window.plot_all_charts(age_data, product_data, payment_data)
        self.plot_window.show()
        
        self.statusBar.showMessage(f"Đã hiển thị thống kê doanh thu, món ăn và phương thức thanh toán")

    def show_order_items(self):
        query = """
        SELECT 
            u.username,
            u.phone,
            u.address,
            o.id as order_id,
            p.name as product_name,
            oi.quantity,
            oi.quantity * p.price as total_price,
            o.total_amount,
            o.discount
        FROM home_order o
        JOIN home_user u ON o.user_id = u.id
        JOIN home_orderitem oi ON oi.order_id = o.id
        JOIN home_product p ON p.id = oi.product_id
        WHERE o.is_paid = True
        ORDER BY o.id DESC
        """
        detail_results = self.query_data(query)
        all_data = []
        order_info = {}
        order_items = {}
        for row in detail_results:
            username, phone, address, order_id, product_name, quantity, item_price, total_amount, discount = row
            if order_id not in order_items:
                order_items[order_id] = []
                order_info[order_id] = {
                    'username': username,
                    'phone': phone,
                    'address': address,
                    'total_amount': total_amount,
                    'discount': discount
                }
            order_items[order_id].append((product_name, quantity, item_price))
        for order_id, items in order_items.items():
            info = order_info[order_id]
            username = info['username']
            phone = info['phone'] or "Không có"
            address = info['address'] or "Không có"
            total_amount = info['total_amount']
            discount = info['discount']
            all_data.append((f"👤 {username}", f"📞 {phone}", f"🏠 {address}", f"Đơn #{order_id}", ""))
            for product_name, quantity, price in items:
                all_data.append(("", product_name, quantity, f"{price:,}", ""))
            all_data.append(("", "", "Tổng đơn:", f"{total_amount:,}", ""))
            if discount and discount > 0:
                discount_amount = float(total_amount) * (float(discount) / 100)
                final_amount = float(total_amount) - discount_amount
                all_data.append(("", "", f"Giảm giá {discount}%:", f"-{discount_amount:,.2f}", ""))
                all_data.append(("", "", "Thanh toán:", f"{final_amount:,.2f}", ""))
            all_data.append(("", "", "", "", ""))
        detail_headers = ["Khách hàng", "Thông tin liên hệ", "Địa chỉ", "Mã đơn", ""]
        self.show_data(all_data, detail_headers)
        self.statusBar.showMessage(f"Tổng số đơn hàng đã thanh toán: {len(order_items)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    login_dialog = LoginDialog()
    if login_dialog.exec_() == QDialog.Accepted and login_dialog.is_authenticated:
        window = MyWindow()
        window.admin_user = login_dialog.admin_user
        window.update_login_status()  # cập nhật UI sau khi gán user
        window.show()
        sys.exit(app.exec_())
    else:
        sys.exit()  # Không tạo MyWindow nếu tắt login dialog hoặc đăng nhập sai
