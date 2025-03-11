import tkinter as tk
from tkinter import ttk, messagebox
import math
import time

#Overflow = Numero máximo de páginas alcançado no bucket
#Colisão = Bucket cheio, sem espaço para adicionar mais registrosclass Page:
#nb = Número de buckets
#fr = capacidade máximo de páginas que o bucket pode ter

    def __init__(self, size):
        self.size = size
        self.data = [] #dados da página

    def add_record(self, record):
        if len(self.data) < self.size:
            self.data.append(record)
            return True
        return False

class Bucket:
    def __init__(self, fr):
        self.fr = fr
        self.pages = [] #instância da classe Page
        self.overflow_count = 0  

    def add_record(self, record, page_size):
        for page in self.pages: #Já existentes 
            if page.add_record(record):
                return True
        #Se o registro não foi adicionado em nenhuma página existente
        if len(self.pages) < self.fr: 
            new_page = Page(page_size)
            new_page.add_record(record)
            self.pages.append(new_page)
            return True #Se for sucesso a página é adicionada a lista de páginas do bucket
        self.overflow_count += 1 
        return False  

def custom_hash_function(key, nb):
    hash_value = sum(ord(char) for char in key) % nb
    return hash_value

def read_data(file_path):
    with open(file_path, 'r') as file:
        data = file.readlines()
    return [line.strip() for line in data]

def build_index(data, page_size, nb, fr):
    buckets = [Bucket(fr) for _ in range(nb)] #Cria-se uma Lista de nb buckets 
    #Cada bucket é uma instância da classe Bucket
    collisions = 0
    for record in data:
        bucket_index = custom_hash_function(record, nb)
        if not buckets[bucket_index].add_record(record, page_size):
            collisions += 1
    return buckets, collisions

def search_record(buckets, key, nb):
    bucket_index = custom_hash_function(key, nb)
    print(f"Busca chave '{key}' no bucket {bucket_index}")  # Depuração
    accesses = 0
    for page in buckets[bucket_index].pages:
        accesses += 1
        if key in page.data:
            print(f"Chave encontrada na página {page.data}")  # Depuração
            return page.data, buckets[bucket_index].pages.index(page), accesses
    return None, None, accesses

def table_scan(data, key, page_size):
    accesses = 0
    pages_read = 0
    for i in range(0, len(data), page_size):
        accesses += 1
        pages_read += 1
        if key in data[i:i + page_size]:
            return i + 1, accesses, pages_read
    return None, accesses, pages_read

class IndexApp:
    def __init__(self, root, data):
        self.root = root
        self.data = data
        self.page_size = 100
        self.fr = 10
        self.nb = None
        self.buckets = None
        self.collisions = 0
        self.overflow_count = 0
        
        self.root.title("Índice Hash Estático")
        self.root.geometry("450x350")
        self.root.resizable(False, False)
        
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(expand=True, fill="both")
        
        ttk.Label(frame, text="Tamanho da Página:").grid(row=0, column=0, sticky="w", pady=5)
        self.size_entry = ttk.Entry(frame, width=10)
        self.size_entry.grid(row=0, column=1, padx=5, pady=5)
        
        self.set_size_button = ttk.Button(frame, text="Definir", command=self.set_page_size)
        self.set_size_button.grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(frame, text="Chave para busca:").grid(row=1, column=0, sticky="w", pady=5)
        self.key_entry = ttk.Entry(frame, width=20)
        self.key_entry.grid(row=1, column=1, padx=5, pady=5)
        
        self.search_button = ttk.Button(frame, text="Buscar", command=self.search_record)
        self.search_button.grid(row=1, column=2, padx=5, pady=5)
        
        self.scan_button = ttk.Button(frame, text="Table Scan", command=self.table_scan)
        self.scan_button.grid(row=2, column=1, pady=10)
        
        self.result_label = ttk.Label(frame, text="", wraplength=400, anchor="center")
        self.result_label.grid(row=3, column=0, columnspan=3, pady=5)

        self.stats_label = ttk.Label(frame, text="", wraplength=400, anchor="center")
        self.stats_label.grid(row=4, column=0, columnspan=3, pady=5)

    def set_page_size(self):
        try:
            self.page_size = int(self.size_entry.get())
            self.nb = math.ceil(len(self.data) / self.fr)
            self.buckets, self.collisions = build_index(self.data, self.page_size, self.nb, self.fr)
            self.overflow_count = sum(bucket.overflow_count for bucket in self.buckets)
            messagebox.showinfo("Info", "Índice Construído!")
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira um tamanho de página válido.")

    def search_record(self):
        key = self.key_entry.get()
        if self.buckets:
            start_time = time.time()
            record, page_index, accesses = search_record(self.buckets, key, self.nb)
            index_time = time.time() - start_time
            
            if record:
                self.result_label.config(text=f"Registro encontrado na página {page_index}: {record}\nAcessos: {accesses}\nTempo: {index_time:.6f}s")
            else:
                self.result_label.config(text="Registro não encontrado")
            
            self.update_stats() 
        else:
            self.result_label.config(text="Defina o tamanho da página primeiro.")

    def table_scan(self):
        key = self.key_entry.get()
        if self.buckets:
            start_time = time.time()
            index, accesses, pages_read = table_scan(self.data, key, self.page_size)
            scan_time = time.time() - start_time
            
            if index is not None:
                self.result_label.config(text=f"Registro encontrado no índice {index}\nAcessos: {accesses}\nPáginas lidas: {pages_read}\nTempo: {scan_time:.6f}s")
            else:
                self.result_label.config(text="Registro não encontrado")
            
            self.update_stats()  
        else:
            self.result_label.config(text="Defina o tamanho da página primeiro.")

    def update_stats(self):
        if self.buckets:
            collision_rate = (self.collisions / len(self.data)) * 100
            overflow_rate = (self.overflow_count / len(self.data)) * 100
            self.stats_label.config(text=f"Taxa de colisões: {collision_rate:.2f}%\nTaxa de overflows: {overflow_rate:.2f}%")

if __name__ == "__main__":
    root = tk.Tk()
    data = read_data('dados.txt')
    app = IndexApp(root, data)
    root.mainloop()
