import sys
import json
import redis

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QComboBox, QSpinBox, QDoubleSpinBox,
    QPushButton, QVBoxLayout, QGridLayout, QGroupBox, QLineEdit,
    QTabWidget, QMessageBox, QHBoxLayout
)
from PyQt5.QtCore import Qt

# -------- High DPI fix (Windows) --------
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

# -------- Redis connection (Docker Redis Stack) --------
r = redis.Redis(
    host="127.0.0.1",
    port=6380,
    decode_responses=True
)


class DirectFireGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Direct Fire Order System")
        self.resize(820, 950)          # allow resizing
        self.setMinimumSize(780, 900)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_order_tab(), "Create Order")
        self.tabs.addTab(self.view_order_tab(), "View Order")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

    # ================= CREATE ORDER TAB =================
    def create_order_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(12)

        # Fire Order ID
        self.fire_order_id = QSpinBox()
        self.fire_order_id.setRange(1, 1_000_000)

        id_box = QGroupBox("Fire Order Details")
        id_layout = QGridLayout()
        id_layout.addWidget(QLabel("Direct Fire Order ID"), 0, 0)
        id_layout.addWidget(self.fire_order_id, 0, 1)
        id_box.setLayout(id_layout)

        # Shooter
        self.shooter_side = QComboBox()
        self.shooter_side.addItems(["Blue", "Red"])
        self.sx = QSpinBox(); self.sy = QSpinBox()
        self.sx.setRange(-10000, 10000)
        self.sy.setRange(-10000, 10000)
        self.s_size = QSpinBox(); self.s_size.setRange(1, 100000)

        shooter_box = self.build_location_group(
            "Shooter", self.shooter_side, self.sx, self.sy, self.s_size
        )

        # Target
        self.target_side = QComboBox()
        self.target_side.addItems(["Blue", "Red"])
        self.tx = QSpinBox(); self.ty = QSpinBox()
        self.tx.setRange(-10000, 10000)
        self.ty.setRange(-10000, 10000)
        self.t_size = QSpinBox(); self.t_size.setRange(1, 100000)

        target_box = self.build_location_group(
            "Target", self.target_side, self.tx, self.ty, self.t_size
        )

        # Weapon
        self.weapon = QComboBox()
        self.weapon.addItems(["RL", "RCL", "MG"])
        self.acc = QDoubleSpinBox(); self.acc.setRange(0, 1)
        self.acc.setSingleStep(0.05)
        self.range = QSpinBox(); self.range.setRange(1, 100000)
        self.kill_prob = QDoubleSpinBox(); self.kill_prob.setRange(0, 1)
        self.kill_prob.setSingleStep(0.05)
        self.ammo = QSpinBox(); self.ammo.setRange(0, 100000)
        self.rof = QSpinBox(); self.rof.setRange(1, 10000)

        weapon_box = QGroupBox("Weapon")
        weapon_layout = QGridLayout()
        weapon_layout.setVerticalSpacing(8)
        weapon_layout.setHorizontalSpacing(10)

        weapon_layout.addWidget(QLabel("Weapon Type"), 0, 0)
        weapon_layout.addWidget(self.weapon, 0, 1)
        weapon_layout.addWidget(QLabel("Accuracy (0–1)"), 1, 0)
        weapon_layout.addWidget(self.acc, 1, 1)
        weapon_layout.addWidget(QLabel("Range (m)"), 2, 0)
        weapon_layout.addWidget(self.range, 2, 1)
        weapon_layout.addWidget(QLabel("Kill Probability"), 3, 0)
        weapon_layout.addWidget(self.kill_prob, 3, 1)
        weapon_layout.addWidget(QLabel("Ammo Count"), 4, 0)
        weapon_layout.addWidget(self.ammo, 4, 1)
        weapon_layout.addWidget(QLabel("ROF (rpm)"), 5, 0)
        weapon_layout.addWidget(self.rof, 5, 1)
        weapon_layout.setRowStretch(6, 1)

        weapon_box.setLayout(weapon_layout)

        # Duration
        self.start = QLineEdit()
        self.end = QLineEdit()
        self.start.setPlaceholderText("HH:MM")
        self.end.setPlaceholderText("HH:MM")

        duration_box = QGroupBox("Duration")
        duration_layout = QGridLayout()
        duration_layout.addWidget(QLabel("Start Time"), 0, 0)
        duration_layout.addWidget(self.start, 0, 1)
        duration_layout.addWidget(QLabel("End Time"), 1, 0)
        duration_layout.addWidget(self.end, 1, 1)
        duration_box.setLayout(duration_layout)

        # Execute button
        btn = QPushButton("EXECUTE FIRE ORDER")
        btn.setFixedHeight(40)
        btn.clicked.connect(self.save_order)

        layout.addWidget(id_box)
        layout.addWidget(shooter_box)
        layout.addWidget(target_box)
        layout.addWidget(weapon_box)
        layout.addWidget(duration_box)
        layout.addWidget(btn, alignment=Qt.AlignCenter)

        tab.setLayout(layout)
        return tab

    # ================= VIEW ORDER TAB =================
    def view_order_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)

        top_row = QHBoxLayout()
        self.view_id = QSpinBox()
        self.view_id.setRange(1, 1_000_000)
        view_btn = QPushButton("VIEW ORDER")
        view_btn.clicked.connect(self.view_order)

        top_row.addWidget(QLabel("Order ID"))
        top_row.addWidget(self.view_id)
        top_row.addWidget(view_btn)

        self.v_shooter = QLabel()
        self.v_target = QLabel()
        self.v_weapon = QLabel()
        self.v_duration = QLabel()

        for lbl in [self.v_shooter, self.v_target, self.v_weapon, self.v_duration]:
            lbl.setStyleSheet("border:1px solid gray; padding:6px;")

        layout.addLayout(top_row)
        layout.addWidget(QLabel("Shooter"))
        layout.addWidget(self.v_shooter)
        layout.addWidget(QLabel("Target"))
        layout.addWidget(self.v_target)
        layout.addWidget(QLabel("Weapon"))
        layout.addWidget(self.v_weapon)
        layout.addWidget(QLabel("Duration"))
        layout.addWidget(self.v_duration)

        tab.setLayout(layout)
        return tab

    # ================= HELPERS =================
    def build_location_group(self, title, side, x, y, size):
        box = QGroupBox(title)
        layout = QGridLayout()
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(8)

        layout.addWidget(QLabel("Side"), 0, 0)
        layout.addWidget(side, 0, 1)
        layout.addWidget(QLabel("Location (X, Y)"), 1, 0)
        layout.addWidget(x, 1, 1)
        layout.addWidget(y, 1, 2)
        layout.addWidget(QLabel("Size"), 2, 0)
        layout.addWidget(size, 2, 1)

        box.setLayout(layout)
        return box

    # ================= REDIS LOGIC =================
    def save_order(self):
        oid = self.fire_order_id.value()
        key = f"directfire:order:{oid}"

        data = {
            "Shooter": {
                "side": self.shooter_side.currentText(),
                "x": self.sx.value(),
                "y": self.sy.value(),
                "size": self.s_size.value()
            },
            "Target": {
                "side": self.target_side.currentText(),
                "x": self.tx.value(),
                "y": self.ty.value(),
                "size": self.t_size.value()
            },
            "Weapon": {
                "type": self.weapon.currentText(),
                "accuracy": self.acc.value(),
                "range": self.range.value(),
                "kill_prob": self.kill_prob.value(),
                "ammo": self.ammo.value(),
                "rof": self.rof.value()
            },
            "Duration": {
                "start": self.start.text(),
                "end": self.end.text()
            }
        }

        r.execute_command("JSON.SET", key, "$", json.dumps(data))
        QMessageBox.information(self, "Saved", f"Order {oid} saved to Redis")

    def view_order(self):
        oid = self.view_id.value()
        key = f"directfire:order:{oid}"

        result = r.execute_command("JSON.GET", key)
        if not result:
            QMessageBox.warning(self, "Error", "Order not found")
            return

        o = json.loads(result)

        self.v_shooter.setText(
            f"{o['Shooter']['side']} | ({o['Shooter']['x']}, {o['Shooter']['y']}) | Size {o['Shooter']['size']}"
        )
        self.v_target.setText(
            f"{o['Target']['side']} | ({o['Target']['x']}, {o['Target']['y']}) | Size {o['Target']['size']}"
        )
        self.v_weapon.setText(
            f"{o['Weapon']['type']} | Acc {o['Weapon']['accuracy']} | "
            f"Range {o['Weapon']['range']} | Kill {o['Weapon']['kill_prob']} | "
            f"Ammo {o['Weapon']['ammo']} | ROF {o['Weapon']['rof']}"
        )
        self.v_duration.setText(
            f"{o['Duration']['start']} → {o['Duration']['end']}"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DirectFireGUI()
    window.show()
    sys.exit(app.exec_())
