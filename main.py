import tkinter as tk
import pandas as pd
import numpy as np
import os
import glob
import seaborn as sns
from tkinter import ttk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
# グローバル変数を指定 ###########################################################
WIDTH = 1397
WEIGHT = 786
WIDTH2, WEIGHT2 = 984, 1332
START_YEAR, END_YEAR = 0, 0
PERIOD = 0
PRICE = 0
Ry = 0
EX1 = 0
EX2 = 0
PATH1 = ''
PATH2 = ''
PATH1_name = ''
PATH2_name = ''
# ##############################################################################
# ウインドウを作成
# ##############################################################################
root = tk.Tk()
root.title('HOPPOCHAN_FINANCE')
root.geometry("1397x786")
root.configure(background="black")
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)


# ##############################################################################
# ENTRY_PAGE
# ##############################################################################
class EntryPage(tk.Frame):
    def __init__(self, master, *pargs):
        tk.Frame.__init__(self, master, *pargs)
        # 画像読み込み
        self.image = Image.open("./pic/TOP/FINANCE_HOPPOCHAN.png")
        self.img_copy = self.image.copy()
        self.background_image = ImageTk.PhotoImage(self.image)
        # ボタン作成
        self.background = tk.Button(self, image=self.background_image,
                                    command=btn_click, background='#212782')
        # ボタン配置
        self.background.pack(fill=tk.BOTH, expand=tk.YES)
        # 画像サイズ修正
        self.background.bind('<Configure>', self._resize_image)

    def _resize_image(self, event):
        global WIDTH, WEIGHT
        ratio = (WEIGHT/WIDTH)
        new_width = event.width
        new_height = int(new_width*ratio)
        self.image = self.img_copy.resize((new_width, new_height))
        self.background_image = ImageTk.PhotoImage(self.image)
        self.background.configure(image=self.background_image)


# ##############################################################################
# Start_Page
# ##############################################################################
class StartPage(tk.Frame):
    def __init__(self, master, *pargs):
        # フレーム生成
        tk.Frame.__init__(self, master, *pargs)
        # フレームのグリッド修正
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        # 画像ファイル
        self.image = Image.open("./pic/TOP/aruku4.png")
        self.img_copy = self.image.copy()
        self.background_image = ImageTk.PhotoImage(self.image)
        # 画像背景を作成
        self.background = tk.Label(self, image=self.background_image,
                                   bg='white')
        # 各種ボタンを作成
        first_button = ttk.Button(self, text="株価比較")
        second_button = ttk.Button(self, text="積み立てシミュレーション")
        third_button = ttk.Button(self, text=" 相関ヒートマップ作成")
        # ボタンのコマンドを押したときのイベントを作成
        first_button["command"] = lambda: self.event_generate("<<Page_CP>>")
        second_button["command"] = lambda: self.event_generate("<<Page_RS>>")
        third_button["command"] = lambda: self.event_generate("<<Page_CR>>")
        # startpageのラベルを生成・配置
        tk.Label(self, text="Start Page", font=("", 30)).grid(row=0, column=0,
                                                              columnspan=3)
        # ボタンを配置
        first_button.grid(row=0, column=0, sticky=(tk.SE))
        second_button.grid(row=0, column=1, sticky=(tk.SE))
        third_button.grid(row=0, column=2, sticky=(tk.SE))
        self.background.grid(row=0, column=3, sticky=(tk.SE))

        # イベントが起きた時の処理
        self.bind("<<Page_RS>>", lambda _: toReserve_simu())
        self.bind("<<Page_CP>>", lambda _: comparison_play())
        self.bind("<<Page_CR>>", lambda _: correlation_play())
        # self.bind("<<Page_Exit>>", lambda _: root.quit())
        self.background.bind('<Configure>', self._resize_image)

    def _resize_image(self, event):
        global WIDTH2, WEIGHT2
        ratio = (WIDTH2/WEIGHT2)
        new_height = event.height
        new_width = int(new_height*ratio)
        self.image = self.img_copy.resize((new_width, new_height))
        self.background_image = ImageTk.PhotoImage(self.image)
        self.background.configure(image=self.background_image)


# ##############################################################################
# ReserveSimulation
# ##############################################################################
class ReserveSimulation(tk.Frame):
    def __init__(self, master, *pargs):
        tk.Frame.__init__(self, master, *pargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.make_canves()

    def make_canves(self):
        self.canvas = tk.Canvas(self, width=200, height=100, bg="white")
        fig = Figure()
        self.ax = fig.add_subplot(1, 1, 1)
        # matplotlibの描画領域とウィジェット(Frame)の関連付け
        self.fig_canvas = FigureCanvasTkAgg(fig, self.canvas)
        # matplotlibのツールバーを作成
        self.toolbar = NavigationToolbar2Tk(self.fig_canvas, self.canvas)
        # matplotlibのグラフをフレームに配置
        self.fig_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas.grid(row=0, column=0, sticky="nsew")

    def button_click(self):
        global PEIOD, Ry, PRICE
        self.canvas.destroy()
        self.make_canves()
        # 年利→月利
        rm = (1.0 + Ry) ** (1/12) - 1
        # 積み立て金額
        y = 0
        x_list = []
        y_list = []
        y2_list = []
        for n in range(PERIOD):
            # y = x * (1+rm) ** (n)
            y = self.cal(PRICE, y, rm)
            y2 = PRICE*(n+1)
            y_list.append(y)
            y2_list.append(y2)
            x_list.append(n)
        # グラフの描画
        # self.ax.set_xlim([0, 100])
        self.ax.plot(x_list, y_list, label='Investment profit')
        self.ax.plot(x_list, y2_list, label='Reserve amount')
        self.ax.set_xlabel('period[month]')
        self.ax.set_ylabel('asset')
        self.ax.legend()
        # 表示
        self.fig_canvas.draw()

    def cal(self, x, y, rm):
        y = (x + y) * (1+rm)
        return y


# ##############################################################################
# ReserveSupport(right)
# ##############################################################################
class ReserveSimulation2(tk.Frame):
    def __init__(self, master, *pargs):
        tk.Frame.__init__(self, master, *pargs)
        tumitate_num = []
        self.label_main = tk.Label(self, text="積み立てシミュレーション",
                                   font=("", 10, 'bold', 'roman', 'underline'))
        button = tk.Button(self, text="Draw Graph", command=self.simu_play)
        # 積み立て金額の項目
        self.label1 = tk.Label(self, text='積み立て金額')
        for i in range(50):
            tumitate_num.append(i)
        v1 = tk.StringVar(value=tumitate_num)
        self.lb1 = tk.Listbox(self, listvariable=v1, height=5)
        scrollbar1 = ttk.Scrollbar(self, orient=tk.VERTICAL,
                                   command=self.lb1.yview)
        self.lb1['yscrollcommand'] = scrollbar1.set
        # 年利の項目
        self.label2 = tk.Label(self, text='年利')
        nenri_num = []
        for i in range(30):
            nenri_num.append(i)
        v2 = tk.StringVar(value=nenri_num)
        self.lb2 = tk.Listbox(self, listvariable=v2, height=5)
        scrollbar2 = ttk.Scrollbar(self, orient=tk.VERTICAL,
                                   command=self.lb2.yview)
        self.lb2['yscrollcommand'] = scrollbar2.set
        # 期間の項目
        self.label3 = tk.Label(self, text='期間[年]')
        period_num = []
        for i in range(80):
            period_num.append(i)
        v3 = tk.StringVar(value=period_num)
        self.lb3 = tk.Listbox(self, listvariable=v3, height=5)
        scrollbar3 = ttk.Scrollbar(self, orient=tk.VERTICAL,
                                   command=self.lb3.yview)
        self.lb3['yscrollcommand'] = scrollbar3.set
        self.lb1.bind("<<ListboxSelect>>", self.show_selected)
        self.lb2.bind("<<ListboxSelect>>", self.show_selected)
        self.lb3.bind("<<ListboxSelect>>", self.show_selected)
        # 選択した項目を表示
        global PERIOD, PRICE, Ry
        self.label4 = tk.Label(self, text='積み立て金額[月]:' + str(PRICE))
        self.label5 = tk.Label(self, text='年利[%]:' + str(Ry))
        self.label6 = tk.Label(self, text='期間[年]:' + str(PERIOD))
        self.label7 = tk.Label(self, text='')
        # 配置
        self.label_main.grid(row=0, column=0, sticky=(tk.E), pady=20)
        self.label1.grid(row=1, column=0, sticky=(tk.N, tk.S), pady=20)
        scrollbar1.grid(row=1, column=1, sticky=(tk.N, tk.S), pady=20)
        self.lb1.grid(row=1, column=2, sticky=(tk.N, tk.S), pady=20)
        self.label2.grid(row=2, column=0, sticky=(tk.N, tk.S), pady=20)
        scrollbar2.grid(row=2, column=1, sticky=(tk.N, tk.S), pady=20)
        self.lb2.grid(row=2, column=2, sticky=(tk.N, tk.S), pady=20)
        self.label3.grid(row=3, column=0, sticky=(tk.N, tk.S), pady=20)
        scrollbar3.grid(row=3, column=1, sticky=(tk.N, tk.S), pady=20)
        self.lb3.grid(row=3, column=2, sticky=(tk.N, tk.S), pady=20)
        self.label7.grid(row=4, column=1, pady=60)
        self.label4.grid(row=5, column=0, sticky=(tk.SE), pady=10)
        self.label5.grid(row=6, column=0, sticky=(tk.SE), pady=10)
        self.label6.grid(row=7, column=0, sticky=(tk.SE), pady=10)
        button.grid(row=8, column=0, sticky=(tk.SE), pady=10)

    def show_selected(self, event):
        global PERIOD, PRICE, Ry
        # 積み立て金額
        n1 = self.lb1.curselection()
        # 年利
        n2 = self.lb2.curselection()
        # 期間
        n3 = self.lb3.curselection()
        if len(n1) > 0:
            PRICE = int(n1[0])
            self.label4.configure(text='積み立て金額[月]:' + str(PRICE))
        elif len(n2) > 0:
            Ry = float(n2[0] * 0.01)
            self.label5.configure(text='年利[%]:' + str(Ry*100))
        else:
            PERIOD = int(n3[0]*12)
            self.label6.configure(text='期間[年]:' + str(int(PERIOD/12)))

    def simu_play(self):
        app2.button_click()


# ##############################################################################
# Comparison_Stock
# ##############################################################################
class Comparison(tk.Frame):
    def __init__(self, master, *pargs):
        tk.Frame.__init__(self, master, *pargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.make_canves()

    def make_canves(self):
        self.canvas = tk.Canvas(self, width=200, height=100, bg="white")
        fig = Figure()
        self.ax = fig.add_subplot(1, 1, 1)
        # matplotlibの描画領域とウィジェット(Frame)の関連付け
        self.fig_canvas = FigureCanvasTkAgg(fig, self.canvas)
        # matplotlibのツールバーを作成
        self.toolbar = NavigationToolbar2Tk(self.fig_canvas, self.canvas)
        # matplotlibのグラフをフレームに配置
        self.fig_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas.grid(row=0, column=0, sticky="nsew")

    def button_click(self):
        global PATH1, PATH2, START_YEAR, END_YEAR, EX1, EX2
        self.canvas.destroy()
        self.make_canves()
        # 為替換算
        self.df1 = self.dfmaker(PATH1, PATH1_name, EX1)
        self.df2 = self.dfmaker(PATH2, PATH2_name, EX2)
        self.ax.plot('date', PATH1_name, data=self.df1, label=PATH1_name)
        self.ax.plot('date', PATH2_name, data=self.df2, label=PATH2_name)
        self.ax.set_xlabel('period[month]')
        self.ax.set_ylabel('asset')
        self.ax.legend()
        # 表示
        self.fig_canvas.draw()

    def dfmaker(self, path, path_name, ex):
        start_date = "01-07"
        end_date = "12-23"
        start = str(START_YEAR) + "-" + start_date
        end = str(END_YEAR) + "-" + end_date
        df = pd.read_csv(path, index_col=['Date'], parse_dates=['Date'])
        df2 = df[start:end]
        if ex == 0:
            df_select = df2.iloc[0, 0]
            df2[path_name] = (((df['Open']-df_select)/df_select)+1) * 100
            df2['date'] = df2.index
        elif ex == 1:
            df_ex = pd.read_csv("./exchange/JPY=X.csv", index_col=['Date'], parse_dates=['Date'])
            df2["Open2"] = df["Open"].round(3) * df_ex["Open"].round(3)
            df_select = df2.iloc[0, 6]
            df2[path_name] = (((df2['Open2']-df_select)/df_select)+1) * 100
            df2['date'] = df2.index
        elif ex == 2:
            df_ex = pd.read_csv("./exchange/JPY=X.csv", index_col=['Date'], parse_dates=['Date'])
            df2["Open2"] = df["Open"].round(3) * (1/df_ex["Open"].round(3))
            df_select = df.iloc[0, 6]
            df2[path_name] = (((df['Open2']-df_select)/df_select)+1) * 100
            df2['date'] = df2.index
        df3 = df2[['date', path_name]]
        return df3


# ##############################################################################
# Comparison_Stock_support
# ##############################################################################
class Comparison2(tk.Frame):
    def __init__(self, master, *pargs):
        tk.Frame.__init__(self, master, *pargs)
        self.label_main = tk.Label(self, text="株価比較",
                                   font=("", 10, 'bold', 'roman', 'underline'))
        button = tk.Button(self, text="Draw Graph", command=self.simu_play)
        # 開始年 ##############################################################
        self.label_start = tk.Label(self, text='開始年')
        start_year_num = []
        for i in range(30):
            start_year_num.append(1992 + i)
        sv_start = tk.StringVar(value=start_year_num)
        self.lb_start = tk.Listbox(self, listvariable=sv_start, height=3)
        scrollbar_start = ttk.Scrollbar(self, orient=tk.VERTICAL,
                                        command=self.lb_start.yview)
        self.lb_start['yscrollcommand'] = scrollbar_start.set
        # 終了年 ###############################################################
        self.label_end = tk.Label(self, text='終了年')
        end_year_num = []
        for i in range(30):
            end_year_num.append(2021-i)
        sv_end = tk.StringVar(value=end_year_num)
        self.lb_end = tk.Listbox(self, listvariable=sv_end, height=3)
        scrollbar_end = ttk.Scrollbar(self, orient=tk.VERTICAL,
                                      command=self.lb_end.yview)
        self.lb_end['yscrollcommand'] = scrollbar_end.set
        # data_comparison からデータを読み込み ###################################
        self.data_path_list = glob.glob('./comparison_data/*')
        self.data_name_list = []
        for i in range(len(self.data_path_list)):
            self.data_name_list.append(os.path.basename(self.data_path_list[i]))
        # PATH1 ###############################################################
        self.label_path1 = tk.Label(self, text='比較ファイル1')
        vs_path1 = tk.StringVar(value=self.data_name_list)
        self.lb_path1 = tk.Listbox(self, listvariable=vs_path1, height=2)
        scrollbar_path1 = ttk.Scrollbar(self, orient=tk.VERTICAL,
                                        command=self.lb_path1.yview)
        self.lb_path1['yscrollcommand'] = scrollbar_path1.set
        # PATH2 ###############################################################
        self.label_path2 = tk.Label(self, text='比較ファイル2')
        vs_path2 = tk.StringVar(value=self.data_name_list)
        self.lb_path2 = tk.Listbox(self, listvariable=vs_path2, height=2)
        scrollbar_path2 = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.lb_path2['yscrollcommand'] = scrollbar_path2.set
        # 為替を判断するボックスを作成 ###########################################
        self.ex_list = ['円→円', 'ドル→円', '円→ドル']
        # ex1 #################################################################
        self.label_ex1 = tk.Label(self, text='為替1')
        vs_ex1 = tk.StringVar(value=self.ex_list)
        self.lb_ex1 = tk.Listbox(self, listvariable=vs_ex1, height=2)
        scrollbar_ex1 = ttk.Scrollbar(self, orient=tk.VERTICAL,
                                      command=self.lb_ex1.yview)
        self.lb_ex1['yscrollcommand'] = scrollbar_ex1.set
        # ex2 ###############################################################
        self.label_ex2 = tk.Label(self, text='為替2')
        vs_ex2 = tk.StringVar(value=self.ex_list)
        self.lb_ex2 = tk.Listbox(self, listvariable=vs_ex2, height=2)
        scrollbar_ex2 = ttk.Scrollbar(self, orient=tk.VERTICAL,
                                      command=self.lb_ex2.yview)
        self.lb_ex2['yscrollcommand'] = scrollbar_ex2.set
        # イベント時に実行する関数を指定##########################################
        self.lb_start.bind("<<ListboxSelect>>", self.Selected)
        self.lb_end.bind("<<ListboxSelect>>", self.Selected)
        self.lb_path1.bind("<<ListboxSelect>>", self.Selected)
        self.lb_path2.bind("<<ListboxSelect>>", self.Selected)
        self.lb_ex1.bind("<<ListboxSelect>>", self.Selected)
        self.lb_ex2.bind("<<ListboxSelect>>", self.Selected)
        # 入力文字を表示 ########################################################
        self.label4 = tk.Label(self, text='開始年:' + str(START_YEAR))
        self.label5 = tk.Label(self, text='終了年:' + str(END_YEAR))
        self.label6 = tk.Label(self, text='PATH1:' + str(PATH1))
        self.label7 = tk.Label(self, text='PATH2:' + str(PATH2))
        self.label8 = tk.Label(self, text='為替1:' + str(EX1))
        self.label9 = tk.Label(self, text='為替2:' + str(EX2))
        self.blank = tk.Label(self, text='')
        # 配置 #################################################################
        self.label_main.grid(row=0, column=0, sticky=(tk.E), pady=20)
        # start
        self.label_start.grid(row=1, column=0, sticky=(tk.N, tk.S), pady=10)
        scrollbar_start.grid(row=1, column=1, sticky=(tk.N, tk.S), pady=10)
        self.lb_start.grid(row=1, column=2, sticky=(tk.N, tk.S), pady=10)
        # end
        self.label_end.grid(row=2, column=0, sticky=(tk.N, tk.S), pady=10)
        scrollbar_end.grid(row=2, column=1, sticky=(tk.N, tk.S), pady=10)
        self.lb_end.grid(row=2, column=2, sticky=(tk.N, tk.S), pady=10)
        # path1
        self.label_path1.grid(row=3, column=0, sticky=(tk.N, tk.S), pady=10)
        scrollbar_path1.grid(row=3, column=1, sticky=(tk.N, tk.S), pady=10)
        self.lb_path1.grid(row=3, column=2, sticky=(tk.N, tk.S), pady=10)
        # path2
        self.label_path2.grid(row=4, column=0, sticky=(tk.N, tk.S), pady=10)
        scrollbar_path2.grid(row=4, column=1, sticky=(tk.N, tk.S), pady=10)
        self.lb_path2.grid(row=4, column=2, sticky=(tk.N, tk.S), pady=10)
        # ex1
        self.label_ex1.grid(row=5, column=0, sticky=(tk.N, tk.S), pady=10)
        scrollbar_ex1.grid(row=5, column=1, sticky=(tk.N, tk.S), pady=10)
        self.lb_ex1.grid(row=5, column=2, sticky=(tk.N, tk.S), pady=10)
        # ex2
        self.label_ex2.grid(row=6, column=0, sticky=(tk.N, tk.S), pady=10)
        scrollbar_ex2.grid(row=6, column=1, sticky=(tk.N, tk.S), pady=10)
        self.lb_ex2.grid(row=6, column=2, sticky=(tk.N, tk.S), pady=10)
        # 入力文字
        self.blank.grid(row=7, column=0, sticky=(tk.N, tk.S), pady=10)
        self.label4.grid(row=8, column=2, sticky=(tk.N, tk.S), pady=5)
        self.label5.grid(row=9, column=2, sticky=(tk.N, tk.S), pady=5)
        self.label6.grid(row=10, column=2, sticky=(tk.N, tk.S), pady=5)
        self.label7.grid(row=11, column=2, sticky=(tk.N, tk.S), pady=5)
        self.label8.grid(row=12, column=2, sticky=(tk.N, tk.S), pady=5)
        self.label9.grid(row=13, column=2, sticky=(tk.N, tk.S), pady=5)
        # botton
        button.grid(row=14, column=0, sticky=(tk.SE), pady=10)

    def Selected(self, event):
        global START_YEAR, END_YEAR, PATH1, PATH2, PATH1_name, PATH2_name, EX1, EX2
        n1 = self.lb_start.curselection()
        n2 = self.lb_end.curselection()
        n3 = self.lb_path1.curselection()
        n4 = self.lb_path2.curselection()
        n5 = self.lb_ex1.curselection()
        n6 = self.lb_ex2.curselection()
        if (len(n1) > 0):
            START_YEAR = int(n1[0]) + 1992
            self.label4.configure(text='開始年:' + str(START_YEAR))
        elif (len(n2) > 0):
            END_YEAR = 2021 - int(n2[0])
            self.label5.configure(text='終了年:' + str(END_YEAR))
        elif (len(n3) > 0):
            PATH1_name = self.data_name_list[int(n3[0])]
            PATH1 = self.data_path_list[int(n3[0])]
            self.label6.configure(text='PATH1:' + str(PATH1_name))
        elif (len(n4) > 0):
            PATH2_name = self.data_name_list[int(n4[0])]
            PATH2 = self.data_path_list[int(n4[0])]
            self.label7.configure(text='PATH2:' + str(PATH2_name))
        elif (len(n5) > 0):
            EX1 = int(n5[0])
            ex1_name = self.ex_list[EX1]
            self.label8.configure(text='PATH2:' + str(ex1_name))
        elif (len(n6) > 0):
            EX2 = int(n6[0])
            ex2_name = self.ex_list[EX2]
            self.label9.configure(text='PATH2:' + str(ex2_name))

    def simu_play(self):
        app5.button_click()


# ##############################################################################
# HeatmapPage
# ##############################################################################
class HeatmapPage(tk.Frame):
    def __init__(self, master, *pargs):
        tk.Frame.__init__(self, master, *pargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.make_canves()

    def make_canves(self):
        # self.arr_2d = np.arange(-8, 8).reshape((4, 4))
        # self.corr_df = pd.DataFrame(data=self.arr_2d, index=['a', 'b', 'c', 'd'], columns=['A', 'B', 'C', 'D'])
        self.canvas = tk.Canvas(self, width=200, height=100, bg="white")
        # fig = Figure()
        fig, self.ax = plt.subplots(figsize=(8, 8))
        # matplotlibの描画領域とウィジェット(Frame)の関連付け
        self.fig_canvas = FigureCanvasTkAgg(fig, self.canvas)
        # matplotlibのツールバーを作成
        self.toolbar = NavigationToolbar2Tk(self.fig_canvas, self.canvas)
        # matplotlibのグラフをフレームに配置
        self.fig_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas.grid(row=0, column=0, sticky="nsew")

    def button_click(self):
        global START_YEAR, END_YEAR
        self.canvas.destroy()
        self.make_canves()
        self.path_list = glob.glob('./comparison_data/*')
        self.name_list = []
        self.df_list = []
        for i in range(len(self.path_list)):
            self.name_list.append(os.path.basename(self.path_list[i]))
        for i in range(len(self.name_list)):
            self.df_list.append(self.dfmaker(self.path_list[i], self.name_list[i]))
        for i in range(len(self.name_list)-1):
            self.df_list[0] = pd.merge(self.df_list[0], self.df_list[i+1])
            print(self.df_list[0])
        self.corr_df = self.df_list[0].corr()
        sns.heatmap(data=self.corr_df, cmap="RdBu_r", annot=True, fmt=".2f",
                    vmax=1, vmin=-1, square=True)
        # 表示
        self.fig_canvas.draw()

    def dfmaker(self, path, path_name):
        global START_YEAR, END_YEAR
        start_date = "01-10"
        end_date = "12-18"
        df = pd.read_csv(path, index_col=['Date'], parse_dates=['Date'])
        start = str(START_YEAR) + "-" + start_date
        end = str(END_YEAR) + "-" + end_date
        df2 = df[start:end]
        if '.T.csv' in path_name:
            ex = 0
        else:
            ex = 1
            print('else')
        if ex == 0:
            df2['open3'] = df['Open']
        elif ex == 1:
            df_ex = pd.read_csv("./exchange/JPY=X.csv", index_col=['Date'], parse_dates=['Date'])
            df2["Open2"] = df["Open"].round(3) * df_ex["Open"].round(3)
            df2['open3'] = df2['Open2']
        elif ex == 2:
            df_ex = pd.read_csv("./exchange/JPY=X.csv", index_col=['Date'], parse_dates=['Date'])
            df2["Open2"] = df["Open"].round(3) * (1/df_ex["Open"].round(3))
            df2['open3'] = df2['Open2']
        df2['date'] = df2.index
        df3 = df2[['date', 'open3']]
        df3['log'] = np.log(df3['open3'])
        df3[path_name] = df3['log'].diff(1)
        df4 = df3[['date', path_name]]
        return df4


# ##############################################################################
# HeatmapPage_support
# ##############################################################################
class HeatmapPage2(tk.Frame):
    def __init__(self, master, *pargs):
        global PATH_LIST, NAME_LIST
        tk.Frame.__init__(self, master, *pargs)
        self.label_main = tk.Label(self, text="株相関",
                                   font=("", 10, 'bold', 'roman', 'underline'))
        button = tk.Button(self, text="Draw Graph", command=self.simu_play)
        # 開始年 ##############################################################
        self.label_start = tk.Label(self, text='開始年')
        start_year_num = []
        for i in range(30):
            start_year_num.append(1992 + i)
        sv_start = tk.StringVar(value=start_year_num)
        self.lb_start = tk.Listbox(self, listvariable=sv_start, height=3)
        scrollbar_start = ttk.Scrollbar(self, orient=tk.VERTICAL,
                                        command=self.lb_start.yview)
        self.lb_start['yscrollcommand'] = scrollbar_start.set
        # 終了年 ###############################################################
        self.label_end = tk.Label(self, text='終了年')
        end_year_num = []
        for i in range(30):
            end_year_num.append(2021-i)
        sv_end = tk.StringVar(value=end_year_num)
        self.lb_end = tk.Listbox(self, listvariable=sv_end, height=3)
        scrollbar_end = ttk.Scrollbar(self, orient=tk.VERTICAL,
                                      command=self.lb_end.yview)
        self.lb_end['yscrollcommand'] = scrollbar_end.set
        # イベント時に実行する関数を指定##########################################
        self.lb_start.bind("<<ListboxSelect>>", self.Selected)
        self.lb_end.bind("<<ListboxSelect>>", self.Selected)
        # 入力文字を表示 ########################################################
        self.label4 = tk.Label(self, text='開始年:' + str(START_YEAR))
        self.label5 = tk.Label(self, text='終了年:' + str(END_YEAR))
        self.blank = tk.Label(self, text='')
        # 配置 #################################################################
        self.label_main.grid(row=0, column=0, sticky=(tk.E), pady=20)
        # start
        self.label_start.grid(row=1, column=0, sticky=(tk.N, tk.S), pady=10)
        scrollbar_start.grid(row=1, column=1, sticky=(tk.N, tk.S), pady=10)
        self.lb_start.grid(row=1, column=2, sticky=(tk.N, tk.S), pady=10)
        # end
        self.label_end.grid(row=2, column=0, sticky=(tk.N, tk.S), pady=10)
        scrollbar_end.grid(row=2, column=1, sticky=(tk.N, tk.S), pady=10)
        self.lb_end.grid(row=2, column=2, sticky=(tk.N, tk.S), pady=10)
        # 入力文字
        self.blank.grid(row=7, column=0, sticky=(tk.N, tk.S), pady=10)
        self.label4.grid(row=8, column=2, sticky=(tk.N, tk.S), pady=5)
        self.label5.grid(row=9, column=2, sticky=(tk.N, tk.S), pady=5)
        # botton
        button.grid(row=14, column=0, sticky=(tk.SE), pady=10)

    def Selected(self, event):
        global START_YEAR, END_YEAR
        n1 = self.lb_start.curselection()
        n2 = self.lb_end.curselection()
        if (len(n1) > 0):
            START_YEAR = int(n1[0]) + 1992
            self.label4.configure(text='開始年:' + str(START_YEAR))
        elif (len(n2) > 0):
            END_YEAR = 2021 - int(n2[0])
            self.label5.configure(text='終了年:' + str(END_YEAR))

    def simu_play(self):
        app7.button_click()


def btn_click():
    app4.tkraise()


def toReserve_simu():
    app4.grid_forget()
    app4.destroy()
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    app2.grid(row=0, column=0, sticky="nsew")
    app2.tkraise()
    app3.grid(row=0, column=1, sticky="nsew")
    app3.tkraise()


def comparison_play():
    print('clicked')
    app6 = Comparison2(root)
    app4.grid_forget()
    app4.destroy()
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    app5.grid(row=0, column=0, sticky="nsew")
    app6.grid(row=0, column=1, sticky="nsew")
    app5.tkraise()


def correlation_play():
    app8 = HeatmapPage2(root)
    app4.grid_forget()
    app4.destroy()
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    app7.grid(row=0, column=0, sticky="nsew")
    app8.grid(row=0, column=1, sticky="nsew")
    app7.tkraise()


app1 = EntryPage(root)
app1.grid(row=0, column=0, sticky="nsew")
app2 = ReserveSimulation(root)
app3 = ReserveSimulation2(root)
app4 = StartPage(root)
app4.grid(row=0, column=0, sticky="nsew")
app5 = Comparison(root)
app7 = HeatmapPage(root)

app1.tkraise()
root.mainloop()
