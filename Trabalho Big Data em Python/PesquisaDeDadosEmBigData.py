import tkinter as tk
from pathlib import Path
from tkinter import ttk

from tkinterdnd2 import DND_FILES, TkinterDnD

import pandas as pd


class Application(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ver o CSV") #nome do arquivo aberto, no caso o nome do windget
        self.main_frame = tk.Frame(self) #Responsavel frame principal da interface
        self.main_frame.pack(fill="both", expand="true")
        self.geometry("1600x900") #resolução da janela
        self.search_page = SearchPage(parent=self.main_frame) #Demonstra o windget da classe SearchPage responsavel pela pesquisa


class DataTable(ttk.Treeview):
    def __init__(self, parent):
        super().__init__(parent, style='Black.Treeview')
        style = ttk.Style(parent)
        style.configure('Black.Treeview', background='#373b3e', foreground='white', fieldbackground='black')

        scroll_Y = tk.Scrollbar(self, orient="vertical", command=self.yview) #barra de scroll verical
        scroll_X = tk.Scrollbar(self, orient="horizontal", command=self.xview) #barra de scroll horizontal
        self.configure(yscrollcommand=scroll_Y.set, xscrollcommand=scroll_X.set)
        scroll_Y.pack(side="right", fill="y")
        scroll_X.pack(side="bottom", fill="x")
        self.stored_dataframe = pd.DataFrame()

    def set_datatable(self, dataframe):
        self.stored_dataframe = dataframe
        self._draw_table(dataframe)

    def _draw_table(self, dataframe):
        self.delete(*self.get_children())
        columns = list(dataframe.columns)
        self.__setitem__("column", columns)
        self.__setitem__("show", "headings")

        for col in columns:
            self.heading(col, text=col)

        df_rows = dataframe.to_numpy().tolist()
        for row in df_rows:
            self.insert("", "end", values=row)
        return None

    def find_value(self, pairs):
        # pairs é um dicionário
        new_df = self.stored_dataframe
        for col, value in pairs.items():
            query_string = f"{col}.astype('str').str.contains('{value}', case=False, na=False)"
            new_df = new_df.query(query_string, engine="python")
        self._draw_table(new_df)

    def reset_table(self):
        self._draw_table(self.stored_dataframe)

class SearchPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.file_names_listbox = tk.Listbox(parent, selectmode=tk.SINGLE, background="darkgray") #Com uso da biblioteca tkinter faço a estrutura da listbox
        self.file_names_listbox.place(relheight=1, relwidth=0.25) #Tamanho do box.
        self.file_names_listbox.drop_target_register(DND_FILES) #basicamente aqui implementamos DnD no qual quando o tipo de arquivo q tem como target for soltou ele ira achar o path do arquivo
        self.file_names_listbox.dnd_bind("<<Drop>>", self.drop_inside_list_box)# Aqui bound da def drop_inside_list_box de soltar o arquivo posta na interface
        self.file_names_listbox.bind("<Double-1>", self._display_file) #Aqui bound da def _display_file de clique duplo do mouse para abrir o arquivo na interface

        self.drop_label = tk.Label(parent, text="Arraste o arquivo CSV Aqui", font=("TkDefaultFont", 14), foreground="gray") #Texto escrito onde soltar o arquivo
        self.drop_label.place(in_=self.file_names_listbox, anchor="c", relx=.5, rely=.5) #posicionamento

        self.search_entrybox = tk.Entry(parent) #Barra de pesquisa
        self.search_entrybox.place(relx=0.25, relwidth=0.75) #Tamanho da barra
        self.search_entrybox.bind("<Return>", self.search_table) #bound da def search_table

        # Treeview
        self.data_table = DataTable(parent) #implementar as funções das barras
        self.data_table.place(rely=0.05, relx=0.25, relwidth=0.75, relheight=0.95)

        self.path_map = {}

    def drop_inside_list_box(self, event): #Def para a função de arrastar e soltar basicamente aqui é utilizado a pathlib para identificar o caminho do arquivo e ler
        file_paths = self._parse_drop_files(event.data)
        current_listbox_items = set(self.file_names_listbox.get(0, "end"))
        for file_path in file_paths:
            if file_path.endswith(".csv"): #tipo do arquivo lido
                path_object = Path(file_path)
                file_name = path_object.name
                if file_name not in current_listbox_items:
                    self.file_names_listbox.insert("end", file_name)
                    self.path_map[file_name] = file_path

    def _display_file(self, event): #Def na qual configura a função do clique duplo abrir o csv
        file_name = self.file_names_listbox.get(self.file_names_listbox.curselection())
        path = self.path_map[file_name]
        df = pd.read_csv(path)
        self.data_table.set_datatable(dataframe=df)

    def _parse_drop_files(self, filename):
        size = len(filename)
        res = []  # lista de path dos arquivos
        name = ""
        idx = 0
        while idx < size:
            if filename[idx] == "{":
                j = idx + 1
                while filename[j] != "}":
                    name += filename[j]
                    j += 1
                res.append(name)
                name = ""
                idx = j
            elif filename[idx] == " " and name != "":
                res.append(name)
                name = ""
            elif filename[idx] != " ":
                name += filename[idx]
            idx += 1
        if name != "":
            res.append(name)
        return res

    def search_table(self, event): #def da barra de pesquisa
        # como pesquisar as colunas. [[column,value],column2=value2]....
        entry = self.search_entrybox.get()
        if entry == "":
            self.data_table.reset_table()
        else:
            entry_split = entry.split(",") #Separar as colunas na barra de pesquisa
            column_value_pairs = {}
            for pair in entry_split:
                pair_split = pair.split("=") #Pesquisar o valor na coluna
                if len(pair_split) == 2:
                    col = pair_split[0]
                    lookup_value = pair_split[1]
                    column_value_pairs[col] = lookup_value
            self.data_table.find_value(pairs=column_value_pairs)


if __name__ == "__main__":
    root = Application()
    root.mainloop()