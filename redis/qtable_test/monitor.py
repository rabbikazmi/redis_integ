import tkinter as tk
from tkinter import ttk
import redis

# Connect to Redis
r = redis.Redis(host='localhost', port=6380, decode_responses=True)

class TacticalMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("REDIS AI COMMAND CENTER")
        self.root.configure(bg="#121212")
        self.root.geometry("750x500")

        # Title
        title = tk.Label(root, text="LIVE TACTICAL AUDIT", font=("Courier", 20, "bold"), 
                         bg="#121212", fg="#00FF00")
        title.pack(pady=10)

        self.main_frame = tk.Frame(root, bg="#121212")
        self.main_frame.pack(fill="both", expand=True, padx=20)

        # 1. Canvas (The Map)
        self.canvas = tk.Canvas(self.main_frame, width=300, height=300, 
                                bg="#1e1e1e", highlightthickness=1, highlightbackground="#333")
        self.canvas.pack(side="left", padx=10)
        
        # 2. Q-Table Display
        self.tree = ttk.Treeview(self.main_frame, columns=("Action", "Score"), show='headings', height=8)
        self.tree.heading("Action", text="TACTIC")
        self.tree.heading("Score", text="Q-SCORE")
        self.tree.column("Action", width=140)
        self.tree.column("Score", width=100)
        self.tree.pack(side="right", fill="y")

        # Define the Highlight Tag
        self.tree.tag_configure('best_move', background='#006400', foreground='#00FF00') # Dark Green BG, Bright Green Text

        self.state_map = {
            "bridge_crossing": (75, 75),
            "forest_ambush": (225, 75),
            "urban_assault": (75, 225),
            "base_defense": (225, 225)
        }
        
        self.agent = self.canvas.create_oval(0, 0, 30, 30, fill="#FF3131", outline="white")
        self.draw_grid()
        self.update_loop()

    def draw_grid(self):
        self.canvas.create_line(150, 0, 150, 300, fill="#333")
        self.canvas.create_line(0, 150, 300, 150, fill="#333")
        for name, (x, y) in self.state_map.items():
            self.canvas.create_text(x, y-40, text=name.upper().replace("_"," "), 
                                    fill="#888", font=("Courier", 8, "bold"))

    def update_loop(self):
        state = r.get("active_state")
        if state in self.state_map:
            # Move Agent Graphic
            x, y = self.state_map[state]
            self.canvas.coords(self.agent, x-15, y-15, x+15, y+15)
            
            # Update Table with Best-Move Logic
            data = r.hgetall(f"q_table:{state}")
            
            # Clear old rows
            for i in self.tree.get_children(): self.tree.delete(i)
            
            if data:
                # Find the maximum Q-value in this state
                # We convert values to float to compare them correctly
                max_val = max(float(v) for v in data.values())
                
                for action, score in data.items():
                    # If this score is the maximum, apply the 'best_move' tag
                    if float(score) == max_val:
                        self.tree.insert("", "end", values=(action, score), tags=('best_move',))
                    else:
                        self.tree.insert("", "end", values=(action, score))

        self.root.after(300, self.update_loop)

# Apply Dark Styling
style = ttk.Style()
style.theme_use("default")
style.configure("Treeview", background="#1e1e1e", foreground="white", fieldbackground="#1e1e1e", borderwidth=0)
style.configure("Treeview.Heading", background="#333", foreground="white", relief="flat")

if __name__ == "__main__":
    root = tk.Tk()
    app = TacticalMonitor(root)
    root.mainloop()