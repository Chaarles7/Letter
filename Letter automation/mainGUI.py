import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import Utils
import pdfOperations
import config
import fillpdf
from fillpdf import fillpdfs


class PDFSection(ttk.LabelFrame):
    def __init__(self, parent, template_fields,generated_string):
        super().__init__(parent, text="2nd Section", padding=(10, 5))
        self.generated_string = generated_string
        self.field_widgets = {}  # Dictionary to store references to combobox widgets
        self.create_fields(template_fields)
        self.add_continue_button()

    def create_fields(self, template_fields):
        for idx, (field, options) in enumerate(template_fields.items()):
            ttk.Label(self, text=f"{field}:").grid(row=idx, column=0, sticky=tk.W, pady=10)
            combobox = ttk.Combobox(self, values=options)
            combobox.grid(row=idx, column=1, pady=5, padx=5)
            self.field_widgets[field] = combobox
    
    def add_continue_button(self):
        ttk.Button(self, text="Continue", command=self.fill_pdf).grid(row=len(self.field_widgets)+1, column=0, columnspan=2, pady=20)
        
    def fill_pdf(self):
        # Get the corresponding PDF
        pdf_file = Utils.select_pdf(self.generated_string)
        if pdf_file == "Sample-Fillable-PDF":
            # For demonstration, just show a message box
            messagebox.showinfo("PDF Selected", f"The selected PDF is: {pdf_file}")
            
            fillpdfs.get_form_fields(r"C:\Users\bonsu\OneDrive\Documents\Sample-Fillable-PDF.pdf")
            
            # Populate the data_dict with selections from the second section
            data_dict = {
                'Name': self.field_widgets["Name"].get(),
                'Dropdown2': 'Choice 1',
                'Option 1': '',
                'Option 2': '',
                'Option 3': '',
                'Name of Dependent': self.field_widgets["Dropdown2"].get(),
                'Age\t of Dependent': ''
            }
            
            fillpdfs.write_fillable_pdf(r"C:\Users\bonsu\OneDrive\Documents\Sample-Fillable-PDF.pdf", 'new.pdf', data_dict)
            
            fillpdfs.flatten_pdf('new.pdf', r"C:\Users\bonsu\OneDrive\Documents\newflat.pdf")
        
class LetterAutomationGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Letter Automation System")
        self.geometry("600x600")
        
        # 1st Section with a border
        self.first_section_frame = ttk.LabelFrame(self, text="1st Section", padding=(10, 2))
        self.first_section_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # Variable to store the generated string
        self.generated_string = ""
        
        self.setup_first_section()
    
    def setup_first_section(self):
        # Dropdowns with trace to automatically generate the string on selection change
        self.doc_type_var = tk.StringVar()
        self.doc_type_var.trace_add("write", self.auto_generate_string)
        
        self.classification_var = tk.StringVar()
        self.classification_var.trace_add("write", self.auto_generate_string)
        
        # Label & Dropdown for Document Type
        ttk.Label(self.first_section_frame, text="Document Type:").grid(row=0, column=0, sticky=tk.W, pady=10)
        doc_type_options = ["letter", "message", "article"]
        self.doc_type_dropdown = ttk.Combobox(self.first_section_frame, textvariable=self.doc_type_var, values=doc_type_options)
        self.doc_type_dropdown.grid(row=0, column=1, pady=5, padx=5)
        
        # Label & Dropdown for Classification
        ttk.Label(self.first_section_frame, text="Classification:").grid(row=1, column=0, sticky=tk.W, pady=10)
        classification_options = ["public", "private", "friendsonly"]
        self.classification_dropdown = ttk.Combobox(self.first_section_frame, textvariable=self.classification_var, values=classification_options)
        self.classification_dropdown.grid(row=1, column=1, pady=5, padx=5)
        
        # Add Enclosure Label & Buttons
        ttk.Label(self.first_section_frame, text="Add Enclosure:").grid(row=2, column=0, sticky=tk.W, pady=10)
        
        self.enclosure_frame = ttk.Frame(self.first_section_frame)
        self.enclosure_frame.grid(row=2, column=1, pady=10)
        
        ttk.Button(self.enclosure_frame, text="+", command=self.add_enclosure).grid(row=0, column=0, padx=5)
        ttk.Button(self.enclosure_frame, text="-", command=self.remove_enclosure).grid(row=0, column=1, padx=5)
        
        # List to store the enclosure dropdowns and labels
        self.enclosure_dropdowns = []
        self.enclosure_labels = []
        
        # Continue button
        ttk.Button(self.first_section_frame, text="Continue ->", command=self.print_string).grid(row=6, column=0, columnspan=2, pady=20)
        
    def add_enclosure(self):
        enclosure_var = tk.StringVar()
        enclosure_var.trace_add("write", self.auto_generate_string)
        
        # Add Enclosure Classification Label
        enclosure_label = ttk.Label(self.first_section_frame, text="Enclosure Classification:")
        enclosure_label.grid(row=5 + len(self.enclosure_dropdowns)*2, column=0, sticky=tk.W, pady=5)
        self.enclosure_labels.append(enclosure_label)
        
        # Add Enclosure Dropdown
        enclosure_dropdown = ttk.Combobox(self.first_section_frame, textvariable=enclosure_var, values=["public", "private", "friendsonly"])
        enclosure_dropdown.grid(row=5 + len(self.enclosure_dropdowns)*2, column=1, pady=5, padx=5)
        self.enclosure_dropdowns.append(enclosure_dropdown)
        
        self.auto_generate_string()
        
    def remove_enclosure(self):
        if self.enclosure_dropdowns:
            self.enclosure_dropdowns[-1].destroy()
            self.enclosure_dropdowns.pop()
            
            self.enclosure_labels[-1].destroy()
            self.enclosure_labels.pop()
            
            self.auto_generate_string()

    def auto_generate_string(self, *args):
        # Dictionary for classification priority
        classification_priority = {
            "public": 1,
            "private": 2,
            "friendsonly": 3
        }
        
        doc_type = self.doc_type_var.get()
        classification = self.classification_var.get()
        
        enclosures = [dropdown.get() for dropdown in self.enclosure_dropdowns]
        
        # Check for highest priority enclosure
        highest_priority_enclosure = max(enclosures, key=lambda x: classification_priority.get(x, 0), default=None)
        
        # Form the string based on the priority of the enclosures
        if highest_priority_enclosure and classification_priority[highest_priority_enclosure] > classification_priority[classification]:
            formatted_string = f"{doc_type}-{classification}({highest_priority_enclosure})"
            for enc in enclosures:
                formatted_string += f"-{enc}"
        else:
            formatted_string = f"{doc_type}-{classification}"
            for enc in enclosures:
                formatted_string += f"-{enc}"
        
        # Update the variable storing the generated string
        self.generated_string = formatted_string

        
    def print_string(self):
        # Print the generated string to console
        print(self.generated_string)
        
        # Select the template based on the generated string
        template_fields = Utils.select_template(self.generated_string)
        
        # Display the 2nd section
        self.show_pdf_section(template_fields)

    def show_pdf_section(self, template_fields):
        if hasattr(self, "pdf_section"):
            self.pdf_section.destroy()
        
        self.pdf_section = PDFSection(self, template_fields,self.generated_string)
        self.pdf_section.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
    

app = LetterAutomationGUI()
app.mainloop()
