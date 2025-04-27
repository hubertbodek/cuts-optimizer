import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pulp import *
import itertools
import csv
from csv import Sniffer
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import ezdxf
from PIL import Image, ImageTk, ImageOps
import os

class CuttingOptimizerPro(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AMIR metal - Optymalizator Cięcia PRO 4.0")
        self.geometry("1400x900")
        self.profiles = []
        self.allowance = 120
        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Sekcja profili
        profile_frame = ttk.LabelFrame(main_frame, text="Zarządzanie profilami")
        profile_frame.pack(fill="x", pady=5)

        # Logo section
        try:
            logo_path = "logo.png"
            print(f"Ładowanie logo z: {os.path.abspath(logo_path)}")
            
            img = Image.open(logo_path)
            # Zachowaj proporcje obrazu
            img_width, img_height = img.size
            new_height = 50
            new_width = int((img_width / img_height) * new_height)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            self.logo = ImageTk.PhotoImage(img)
            logo_label = ttk.Label(profile_frame, image=self.logo)
            logo_label.pack(side="right", padx=10)
            print("Logo zostało pomyślnie załadowane")
        except Exception as e:
            print(f"Błąd ładowania logo: {str(e)}")

        self.profile_combobox = ttk.Combobox(profile_frame, values=[6000, 3000, 4000])
        self.profile_combobox.current(0)
        self.profile_combobox.pack(side="left", padx=5)

        self.custom_profile = ttk.Entry(profile_frame, width=10)
        self.custom_profile.pack(side="left", padx=5)

        ttk.Button(profile_frame, text="Dodaj profil", 
                 command=self.add_profile).pack(side="left", padx=5)
        ttk.Button(profile_frame, text="Usuń profil", 
                 command=self.remove_profile).pack(side="left", padx=5)

        # Sekcja elementów
        input_frame = ttk.LabelFrame(main_frame, text="Elementy do cięcia")
        input_frame.pack(fill="x", pady=5)

        ttk.Label(input_frame, text="Długość (mm):").pack(side="left")
        self.item_length = ttk.Entry(input_frame, width=10)
        self.item_length.pack(side="left", padx=5)
        
        ttk.Label(input_frame, text="Ilość:").pack(side="left")
        self.item_quantity = ttk.Entry(input_frame, width=10)
        self.item_quantity.pack(side="left", padx=5)
        
        ttk.Button(input_frame, text="Dodaj element", 
                 command=self.add_item).pack(side="left", padx=5)
        ttk.Button(input_frame, text="Import CSV", 
                 command=self.import_csv).pack(side="right", padx=5)

        # Lista elementów
        self.items_tree = ttk.Treeview(main_frame, columns=("length", "quantity"), 
                                     show="headings", height=8)
        self.items_tree.heading("length", text="Długość (mm)")
        self.items_tree.heading("quantity", text="Ilość")
        self.items_tree.column("length", width=150, anchor="center")
        self.items_tree.column("quantity", width=150, anchor="center")
        self.items_tree.pack(fill="x", padx=10, pady=5)

        # Sekcja wyników
        result_frame = ttk.LabelFrame(main_frame, text="Wyniki optymalizacji")
        result_frame.pack(fill="both", expand=True, pady=5)

        self.canvas = tk.Canvas(result_frame)
        self.canvas.pack(fill="both", expand=True)

        self.result_tree = ttk.Treeview(self.canvas, 
                                      columns=("count", "pattern", "waste", "profile"), 
                                      show="headings", height=12)
        self.result_tree.pack(fill="both", expand=True, padx=10, pady=5)

        # Panel sterowania
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(pady=10)
        
        self.allowance_var = tk.BooleanVar()
        ttk.Checkbutton(control_frame, text="Naddatek 120 mm", 
                       variable=self.allowance_var).pack(side="left", padx=5)
        
        ttk.Button(control_frame, text="Uruchom optymalizację", 
                 command=self.start_optimization).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Eksport do Excel", 
                 command=self.export_excel).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Generuj PDF", 
                 command=self.generate_pdf).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Eksport DXF", 
                 command=self.export_dxf).pack(side="left", padx=5)

    def add_item(self):
        try:
            length = float(self.item_length.get().replace(',', '.'))
            quantity = int(self.item_quantity.get())
            
            if length <= 0 or quantity <= 0:
                raise ValueError("Wartości muszą być większe od 0")
                
            self.items_tree.insert("", "end", values=(length, quantity))
            self.item_length.delete(0, "end")
            self.item_quantity.delete(0, "end")
        except Exception as e:
            messagebox.showerror("Błąd", str(e))

    def add_profile(self):
        try:
            if self.custom_profile.get():
                length = float(self.custom_profile.get().replace(',', '.'))
            else:
                length = float(self.profile_combobox.get())
            
            if length <= 0:
                raise ValueError("Nieprawidłowa długość profilu")
                
            self.profiles.append(length)
            self.custom_profile.delete(0, "end")
            messagebox.showinfo("Sukces", f"Dodano profil {length} mm")
        except Exception as e:
            messagebox.showerror("Błąd", str(e))

    def remove_profile(self):
        if self.profiles:
            removed = self.profiles.pop()
            messagebox.showinfo("Sukces", f"Usunięto profil {removed} mm")
        else:
            messagebox.showwarning("Uwaga", "Brak profili do usunięcia")

    def import_csv(self):
        path = filedialog.askopenfilename(filetypes=[("Pliki CSV", "*.csv")])
        if not path: return
        
        try:
            with open(path, newline='', encoding='utf-8') as f:
                # Sprawdź format pliku
                dialect = Sniffer().sniff(f.read(1024))
                f.seek(0)
                
                reader = csv.reader(f, dialect)
                header = Sniffer().has_header(f.read(1024))
                f.seek(0)
                
                if header:
                    next(reader)
                    
                for row_num, row in enumerate(reader, 1):
                    if len(row) < 2:
                        raise ValueError(f"Brakujące dane w wierszu {row_num}")
                    
                    # Walidacja danych
                    try:
                        length = float(row[0].replace(',', '.'))
                        quantity = int(row[1])
                    except ValueError as e:
                        raise ValueError(f"Nieprawidłowe dane w wierszu {row_num}: {row}")
                    
                    self.items_tree.insert("", "end", values=(length, quantity))
                    
        except Exception as e:
            messagebox.showerror("Błąd importu", 
                f"{str(e)}\n\nPoprawny format CSV:\nDługość [mm],Ilość\n1500,3\n2000,2")

    def generate_patterns(self, elements, max_length):
        # Poprawione rzutowanie na int
        max_counts = [int(max_length // elem) for elem in elements]
    
        # Dodatkowe zabezpieczenie przed zerem
        max_counts = [c if c > 0 else 0 for c in max_counts]
    
        patterns = []
    
        for counts in itertools.product(*[range(c+1) for c in max_counts]):
            total = sum(elem*count for elem, count in zip(elements, counts))
            if 0 < total <= max_length:
                patterns.append(tuple(counts))
        return list(set(patterns))

    def optimize_profile(self, profile_length, elements, quantities):
        available_length = profile_length - (120 if self.allowance_var.get() else 0)
    
        # Dodatkowa walidacja danych wejściowych
        if any(elem <= 0 for elem in elements):
            raise ValueError("Długości elementów muszą być większe od 0")
    
        patterns = self.generate_patterns(elements, available_length)
        
        model = LpProblem(f"Cutting_{profile_length}", LpMinimize)
        x = [LpVariable(f"x{i}", lowBound=0, cat="Integer") for i in range(len(patterns))]
        
        # Funkcja celu
        model += lpSum(x)
        
        # Ograniczenia
        for i in range(len(elements)):
            model += lpSum(pattern[i] * x[j] for j, pattern in enumerate(patterns)) >= quantities[i]
        
        model.solve(PULP_CBC_CMD(msg=False))
        return [(var.varValue, pattern) for var, pattern in zip(x, patterns) if var.varValue and var.varValue > 0]

    def start_optimization(self):
        try:
            # Pobierz dane
            elements = []
            quantities = []
            for item in self.items_tree.get_children():
                values = self.items_tree.item(item)["values"]
                elements.append(float(values[0]))
                quantities.append(int(values[1]))
            
            if not elements:
                raise ValueError("Brak elementów do optymalizacji")
            
            if not self.profiles:
                raise ValueError("Nie dodano żadnych profili")
                
            # Wyczyść wyniki
            self.result_tree.delete(*self.result_tree.get_children())
            
            # Optymalizuj dla każdego profilu
            for profile in self.profiles:
                results = self.optimize_profile(profile, elements, quantities)
                for count, pattern in results:
                    cuts = []
                    total_cut = 0
                    for i, cnt in enumerate(pattern):
                        if cnt > 0:
                            cuts.append(f"{cnt}x{elements[i]}mm")
                            total_cut += elements[i] * cnt
                    
                    waste = profile - total_cut - (120 if self.allowance_var.get() else 0)
                    self.result_tree.insert("", "end", 
                                          values=(int(count), " + ".join(cuts), waste, profile))
            
            messagebox.showinfo("Sukces", "Optymalizacja zakończona")
        except Exception as e:
            messagebox.showerror("Błąd", f"{str(e)}")

    def export_excel(self):
        path = filedialog.asksaveasfilename(defaultextension=".xlsx")
        if not path: return
        
        try:
            data = []
            for item in self.result_tree.get_children():
                data.append(self.result_tree.item(item)["values"])
            
            df = pd.DataFrame(data, columns=["Liczba", "Schemat", "Odpad", "Profil"])
            df.to_excel(path, index=False)
            messagebox.showinfo("Sukces", "Plik Excel zapisany")
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd eksportu: {str(e)}")

    def generate_pdf(self):
        path = filedialog.asksaveasfilename(defaultextension=".pdf")
        if not path: return
    
        try:
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.units import mm
        
            doc = SimpleDocTemplate(path, pagesize=A4, 
                                   leftMargin=15*mm, rightMargin=15*mm)
            styles = getSampleStyleSheet()
            story = []
        
            # Nagłówek
            story.append(Paragraph("<b>Raport optymalizacji cięcia</b>", styles["Title"]))
            story.append(Spacer(1, 12))
        
            # Tabela wyników
            data = [["Liczba", "Schemat cięcia", "Odpad [mm]", "Profil [mm]"]]
            for item in self.result_tree.get_children():
                values = self.result_tree.item(item)["values"]
                data.append([
                    str(values[0]),
                    Paragraph(values[1], styles["BodyText"]),
                    f"{float(values[2]):.1f}",
                    f"{float(values[3]):.1f}"
                ])
        
            # Automatyczne zawijanie wierszy i paginacja
            table_style = [
                ('BACKGROUND', (0,0), (-1,0), '#CCCCCC'),
                ('TEXTCOLOR', (0,0), (-1,0), 'black'),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 10),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('BACKGROUND', (0,1), (-1,-1), 'white'),
                ('GRID', (0,0), (-1,-1), 1, 'black'),
                ('WORDWRAP', (1,1), (1,-1))  # Zawijanie tekstu dla kolumny schematów
            ]
        
            from reportlab.platypus import Table
            table = Table(data, style=table_style, repeatRows=1)
            story.append(table)
            doc.build(story)
        
            messagebox.showinfo("Sukces", "Plik PDF wygenerowany poprawnie")
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd generowania PDF: {str(e)}")

    def export_dxf(self):
        path = filedialog.asksaveasfilename(defaultextension=".dxf")
        if not path: return

        try:
            doc = ezdxf.new(dxfversion='R2018')
            msp = doc.modelspace()
            self._setup_dxf_layers(doc)
            
            # Parametry przestrzenne (w mm)
            start_y = 10000  # Punkt startowy 10 metrów od dołu
            vertical_spacing = 5000  # Odstęp 5 metrów między profilami
            profile_number = 1

            for item in self.result_tree.get_children():
                values = self.result_tree.item(item)["values"]
                count = int(values[0])
                pattern = values[1]
                profile_length = float(values[3])
                elements = self._parse_pattern(pattern)

                for _ in range(count):
                    current_y = start_y - (profile_number * vertical_spacing)
                    
                    # Etykieta profilu
                    label = msp.add_text(
                        f"PROFIL {profile_number}",
                        dxfattribs={"layer": "LABELS", "height": 300}
                    )
                    label.insert = (0, current_y + 4000, 0)

                    # Główny profil
                    self._draw_profile(msp, profile_length, current_y)

                    # Elementy cięcia
                    x_offset = 0
                    for elem in elements:
                        self._draw_cut_line(msp, x_offset, current_y, elem['length'])
                        self._add_dimension(
                            msp,
                            start=(x_offset, current_y - 1000),
                            end=(x_offset + elem['length'], current_y - 1000),
                            text=f"{elem['length']}mm"
                        )
                        x_offset += elem['length']

                    # Wymiar całkowity
                    self._add_dimension(
                        msp,
                        start=(0, current_y - 2000),
                        end=(profile_length, current_y - 2000),
                        text=f"Całkowita długość: {profile_length}mm"
                    )

                    profile_number += 1

            doc.saveas(path)
            messagebox.showinfo("Sukces", "Plik DXF wygenerowany poprawnie!")

        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd eksportu DXF:\n{str(e)}")

    def _setup_dxf_layers(self, doc):
        """Tworzy warstwy i style DXF"""
        doc.layers.new("PROFILE", dxfattribs={"color": 2, "linetype": "CONTINUOUS"})
        doc.layers.new("CUTS", dxfattribs={"color": 1, "linetype": "DASHED"})
        doc.layers.new("DIMENSIONS", dxfattribs={"color": 5})
        doc.layers.new("LABELS", dxfattribs={"color": 3})

        dim_style = doc.dimstyles.new("CUSTOM_STYLE")
        dim_style.dxf.dimtxt = 50  # Wysokość tekstu
        dim_style.dxf.dimasz = 50  # Rozmiar strzałek
        dim_style.dxf.dimtad = 4    # Tekst pod linią
        dim_style.dxf.dimgap = 50  # Odstęp tekstu od linii

    def _draw_profile(self, msp, length, y_pos):
        """Rysuje główny profil"""
        msp.add_line(
            (0, y_pos),
            (length, y_pos),
            dxfattribs={"layer": "PROFILE", "lineweight": 30}
        )

    def _draw_cut_line(self, msp, x_offset, y_pos, length):
        """Rysuje linię cięcia z opisem"""
        msp.add_line(
            (x_offset, y_pos - 50),
            (x_offset, y_pos + 50),
            dxfattribs={"layer": "CUTS", "linetype": "DASHED"}
        )
        text = msp.add_text(
            f"{length}mm",
            dxfattribs={"layer": "DIMENSIONS", "height": 100}
        )
        text.insert = (x_offset + length/2, y_pos + 150, 0)

    def _add_dimension(self, msp, start, end, text):
        """Dodaje wymiar liniowy"""
        dimension = msp.add_linear_dim(
            base=(start[0], start[1]),
            p1=start,
            p2=end,
            dimstyle="CUSTOM_STYLE"
        )
        dimension.set_text(text)
        dimension.dimension_type = 1

    def _parse_pattern(self, pattern):
        """Parsuje schemat cięcia na elementy"""
        elements = []
        for part in pattern.split("+"):
            part = part.strip()
            cnt, length = part.split("x")
            length = length.replace("mm", "").strip()
            elements.extend([{
                'count': int(cnt),
                'length': float(length)
            }] * int(cnt))
        return elements

if __name__ == "__main__":
    app = CuttingOptimizerPro()
    app.mainloop()