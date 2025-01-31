import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplcursors

class LoadsolAnalysis:
    def __init__(self, root):
        self.root = root
        self.root.title("Load Analysis Program")

        # Initialize variables
        self.ic_thresh = 10
        self.to_thresh = 5
        self.event_window = 500
        self.body_weight = None
        self.data = None
        self.ic_events = []
        self.to_events = []
        self.plot_frame = None

        # GUI Variables
        self.movement = tk.StringVar(value="Select Movement")
        self.percent_gcp_imp = tk.DoubleVar(value=0.5)
        self.percent_gcp_pif = tk.DoubleVar(value=0.5)
        self.time_fc_imp = tk.DoubleVar(value=0.5)
        self.time_fc_pif = tk.DoubleVar(value=0.5)

        # GUI Setup
        self.setup_gui()

    def setup_gui(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        control_frame = tk.Frame(main_frame, width=300)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.plot_frame = tk.Frame(main_frame)
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(control_frame, text="Load Analysis Program", font=("Helvetica", 16)).pack(pady=10)
        tk.OptionMenu(control_frame, self.movement, "Movement 1", "Movement 3").pack(pady=5)

        tk.Scale(control_frame, variable=self.percent_gcp_imp, from_=0, to=1, resolution=0.01, orient='horizontal',
                 label="Percent GCP IMP").pack(pady=5)
        tk.Scale(control_frame, variable=self.percent_gcp_pif, from_=0, to=1, resolution=0.01, orient='horizontal',
                 label="Percent GCP PIF").pack(pady=5)
        tk.Scale(control_frame, variable=self.time_fc_imp, from_=0, to=1, resolution=0.01, orient='horizontal',
                 label="Time FC IMP").pack(pady=5)
        tk.Scale(control_frame, variable=self.time_fc_pif, from_=0, to=1, resolution=0.01, orient='horizontal',
                 label="Time FC PIF").pack(pady=5)

        tk.Label(control_frame, text="Body Weight (kg):").pack(pady=5)
        self.body_weight_entry = tk.Entry(control_frame)
        self.body_weight_entry.pack(pady=5)

        tk.Button(control_frame, text="Load Data File", command=self.load_data).pack(pady=5)
        tk.Button(control_frame, text="Normalize Data", command=self.normalize_data).pack(pady=5)
        tk.Button(control_frame, text="Plot Data", command=self.plot_data).pack(pady=5)
        tk.Button(control_frame, text="Compute", command=self.compute_callback).pack(pady=10)

    def load_data(self):
        filepath = filedialog.askopenfilename(
            title="Select Data File",
            filetypes=(("Text Files", "*.txt"), ("All Files", "*.*"))
        )
        if filepath:
            try:
                data = pd.read_csv(filepath, delimiter=r'\s+', skiprows=4, header=None,
                                   names=["Time1", "Force1", "Time2", "Force2"])

                data["TimeR"] = pd.to_numeric(data["Time1"], errors='coerce')
                data["ForceR"] = pd.to_numeric(data["Force1"], errors='coerce')
                data["TimeL"] = pd.to_numeric(data["Time2"], errors='coerce')
                data["ForceL"] = pd.to_numeric(data["Force2"], errors='coerce')

                data.dropna(how='all', subset=["Force1", "Force2"], inplace=True)
                data.fillna(-1, inplace=True)

                self.data = data[["TimeR", "ForceR", "TimeL", "ForceL"]]
                messagebox.showinfo("Success", "Data loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load data: {e}")

    def normalize_data(self):
        try:
            self.body_weight = float(self.body_weight_entry.get())
            if self.body_weight <= 0:
                raise ValueError("Body weight must be greater than zero.")
            self.data[["ForceR", "ForceL"]] = self.data[["ForceR", "ForceL"]] / self.body_weight * 100
            messagebox.showinfo("Success", "Data normalized successfully.")
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid body weight.")

    def plot_data(self):

        if self.data is None or self.data.empty:
            messagebox.showerror("Error", "No data to plot. Please load the data first.")
            return

        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        from matplotlib.figure import Figure
        fig = Figure(figsize=(12, 8))
        axs = fig.subplots(2, 1, sharex=True)

        line_r, = axs[0].plot(self.data['TimeR'], self.data['ForceR'], color='blue', label='Right foot')
        axs[0].plot(self.data['TimeR'], self.data['ForceR'], color='blue')
        axs[0].set_title('Right Foot Force')
        axs[0].set_xlabel('Time (s)')
        axs[0].set_ylabel('Force (N)')
        axs[0].grid(True)

        line_l, = axs[1].plot(self.data['TimeL'], self.data['ForceL'], color='purple', label='Left foot')
        axs[1].plot(self.data['TimeL'], self.data['ForceL'], color='purple')
        axs[1].set_title('Left Foot Force')
        axs[1].set_xlabel('Time (s)')
        axs[1].set_ylabel('Force (N)')
        axs[1].grid(True)

        mplcursors.cursor([line_r, line_l], hover=True)



        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)
        canvas.draw()
        plt.close(fig)

    def compute_callback(self):
        movement = self.movement.get()
        stance_imp = self.percent_gcp_imp.get()
        stance_pif = self.percent_gcp_pif.get()
        time_imp = self.time_fc_imp.get()
        time_pif = self.time_fc_pif.get()

        print(f"Movement: {movement}")
        print(f"Percent GCP IMP: {stance_imp}")
        print(f"Percent GCP PIF: {stance_pif}")
        print(f"Time FC IMP: {time_imp}")
        print(f"Time FC PIF: {time_pif}")


if __name__ == "__main__":
    root = tk.Tk()
    app = LoadsolAnalysis(root)
    root.mainloop()