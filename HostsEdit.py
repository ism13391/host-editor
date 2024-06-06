import tkinter as tk
from tkinter import messagebox, Scrollbar, IntVar, Label, Frame, Entry, Button

def parse_host_line(line):
    parts = line.split()
    redirect_from = parts[0]
    redirect_to = ' '.join(parts[1:]) if len(parts) > 1 else ''
    status = "Enabled" if not line.startswith("#") else "Disabled"
    return redirect_from, redirect_to, status

def load_hosts():
    global checkboxes
    checkboxes = []
    canvas.delete("all")
    create_headers()  
    y_position = 30 
    double_hash_count = 0
    start_reading = False
    try:
        with open("/etc/hosts", "r") as file:
            for line in file:
                if '##' in line.strip():
                    double_hash_count += 1
                    if double_hash_count == 2:
                        start_reading = True
                    continue
                if start_reading:
                    line = line.strip()
                    if line:
                        chk_var = IntVar(value=not line.startswith("#"))
                        redirect_from, redirect_to, status = parse_host_line(line.lstrip('# '))
                        
                        entry_frame = Frame(canvas, bd=1, relief="solid", bg="#f0f0f0" if y_position // 30 % 2 == 0 else "#e0e0e0")
                        canvas.create_window(10, y_position, anchor='nw', window=entry_frame, width=460)
                        
                        chk = tk.Checkbutton(entry_frame, variable=chk_var, justify="center", anchor="center")
                        chk.grid(row=0, column=0, ipadx=10)
                        Label(entry_frame, text=redirect_from, width=22, justify="left", anchor="w").grid(row=0, column=1, ipadx=5, sticky='e')
                        Label(entry_frame, text=redirect_to, width=22, justify="left", anchor="w").grid(row=0, column=2, ipadx=5, sticky='e')
                        
                        y_position += 30
                        checkboxes.append((chk_var, line))
            canvas.config(scrollregion=canvas.bbox("all"))
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load hosts file: {str(e)}")

def create_headers():
    headers = ["  ","Redirect From", "Redirect To"]
    header_frame = Frame(canvas, bd=1, relief="solid", bg="#ddd")
    canvas.create_window(10, 0, anchor='nw', window=header_frame, width=460)
    for i, header in enumerate(headers):
        Label(header_frame, text=header, width=25 if i > 0 else 5, justify="left", anchor="w").grid(row=0, column=i)

def update_hosts():
    try:
        output_lines = []
        double_hash_count = 0
        start_writing = False
        with open("/etc/hosts", "r") as file:
            for line in file:
                if '##' in line.strip():
                    double_hash_count += 1
                    output_lines.append(line.strip())
                    if double_hash_count == 2:
                        start_writing = True
                    continue
                if not start_writing:
                    output_lines.append(line.strip())
        
        with open("/etc/hosts", "w") as file:
            for line in output_lines:
                file.write(line + '\n')
            for chk_var, line in checkboxes:
                if chk_var.get():
                    line = line.lstrip('# ')
                else:
                    if not line.startswith("#"):
                        line = "# " + line
                file.write(line + '\n')
        
        messagebox.showinfo("Success", "Hosts file updated successfully!")
        load_hosts()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to update hosts file: {str(e)}")

def save_new_redirect():
    new_from = new_from_entry.get().strip()
    new_to = new_to_entry.get().strip()
    if new_from and new_to:
        new_line = f"{new_from} {new_to}"
        try:
            with open("/etc/hosts", "a") as file:
                file.write(f"\n{new_line}")
            messagebox.showinfo("Success", "New redirect added successfully!")
            load_hosts()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add new redirect: {str(e)}")
    else:
        messagebox.showwarning("Warning", "Please fill both fields to add a redirect.")

app = tk.Tk()
app.title("Hosts File Editor")

window_width = 600
window_height = 600
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()
center_x = int(screen_width / 2 - window_width / 2)
center_y = int(screen_height / 2 - window_height / 2)
app.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
app.resizable(True, True)

table_frame = Frame(app)
table_frame.pack(fill="both", expand=True)


entry_frame = Frame(app)
entry_frame.pack(fill="x", pady=20)
Label(entry_frame, text="Redirect From:").pack()
new_from_entry = Entry(entry_frame, width=20)
new_from_entry.pack(pady=(0, 10))
Label(entry_frame, text="Redirect To:").pack()
new_to_entry = Entry(entry_frame, width=20)
new_to_entry.pack(pady=(0, 10))

add_button = Button(entry_frame, text="Save New Redirect", command=save_new_redirect)
add_button.pack(pady=10)

button_frame = Frame(app)
button_frame.pack(fill="x")
update_button = Button(button_frame, text="Update Hosts File", command=update_hosts)
update_button.pack(pady=20)

scrollbar = Scrollbar(table_frame)


canvas = tk.Canvas(table_frame, yscrollcommand=scrollbar.set)
canvas.pack(side="left", fill="both", expand=True)
scrollbar.config(command=canvas.yview)

create_headers()
load_hosts()

app.mainloop()
