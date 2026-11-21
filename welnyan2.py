# welnyan.py
# 玄関開けたらウェルカムにゃん（Tkinter版）
# 画像なし（Canvas図形のみ）／マウス操作（クリック＆ドラッグ）必須

import tkinter as tk

W = 900
H = 540

class App:
    def __init__(self, root):
        self.root = root
        root.title("玄関開けたらウェルカムにゃん")
        root.resizable(False, False)

        self.cv = tk.Canvas(root, width=W, height=H, bg="#f2efe9", highlightthickness=0)
        self.cv.pack()

        # 状態
        self.scene = "entry"   # entry / cat / ending
        self.door_open = False

        self.pet_count = 0
        self.feed_count = 0
        self.play_count = 0

        # 満足度：なでる/えさ/あそぶで増える。一定値でエンディング
        self.happy = 0

        # 順序による変化用（最後にした操作を記録）
        self.last_action = ""  # "pet"/"feed"/"play"

        # ボール（ドラッグおもちゃ）
        self.ball_drag = False
        self.ball_x = 140
        self.ball_y = 420

        # 猫の位置（固定）
        self.cat_x = 650
        self.cat_y = 330

        # Canvas item id
        self.ids = {}

        # 描画
        self.draw_entry()

        # イベント
        self.cv.bind("<Button-1>", self.on_click)
        self.cv.bind("<B1-Motion>", self.on_drag)
        self.cv.bind("<ButtonRelease-1>", self.on_release)

        # 目線追従（一定周期）
        self.root.after(50, self.tick)

    # -------------------------
    # シーン描画
    # -------------------------
    def clear_all(self):
        self.cv.delete("all")
        self.ids = {}

    def draw_entry(self):
        self.clear_all()
        self.scene = "entry"
        self.door_open = False

        # 背景（玄関っぽく）
        self.cv.create_rectangle(0, 0, W, H, fill="#f2efe9", outline="")
        self.cv.create_rectangle(0, 420, W, H, fill="#d9d1c7", outline="")  # 床
        self.cv.create_rectangle(0, 410, W, 420, fill="#b9afa3", outline="")  # 境

        # ドア（左側）
        self.ids["door"] = self.cv.create_rectangle(90, 80, 380, 420, fill="#8b5a2b", outline="#5b3a1a", width=3)
        self.ids["door_panel"] = self.cv.create_rectangle(120, 110, 350, 390, fill="#9a6a35", outline="#6a4420", width=2)
        self.ids["knob"] = self.cv.create_oval(340, 245, 365, 270, fill="#d8c48a", outline="#8a7a4a", width=2)

        # 表札
        self.cv.create_rectangle(210, 65, 330, 95, fill="#eee", outline="#777")
        self.cv.create_text(270, 80, text="WELCOME", font=("Meiryo", 14, "bold"), fill="#333")

        # 説明
        self.ids["msg"] = self.cv.create_text(
            540, 120,
            text="取っ手（丸いところ）をクリックしてドアを開けよう",
            font=("Meiryo", 18, "bold"),
            fill="#333"
        )

        self.draw_status()

    def draw_cat_scene(self):
        self.clear_all()
        self.scene = "cat"

        # 背景（玄関）
        self.cv.create_rectangle(0, 0, W, H, fill="#f2efe9", outline="")
        self.cv.create_rectangle(0, 420, W, H, fill="#d9d1c7", outline="")
        self.cv.create_rectangle(0, 410, W, 420, fill="#b9afa3", outline="")

        # 開いたドア（開いた表現：細くして左へ）
        self.cv.create_polygon(90, 80, 140, 95, 140, 420, 90, 420, fill="#8b5a2b", outline="#5b3a1a", width=3)
        self.cv.create_text(215, 120, text="ドアが開いた！", font=("Meiryo", 16, "bold"), fill="#333")

        # えさ皿
        self.ids["bowl"] = self.cv.create_oval(440, 392, 560, 432, fill="#c9d6df", outline="#607d8b", width=2)
        self.ids["food"] = self.cv.create_oval(470, 402, 530, 425, fill="#c77d2a", outline="#8a4b1a")

        self.cv.create_text(500, 372, text="えさ（クリック）", font=("Meiryo", 12), fill="#333")

        # ボール（ドラッグおもちゃ）
        self.ids["ball"] = self.cv.create_oval(self.ball_x-18, self.ball_y-18, self.ball_x+18, self.ball_y+18,
                                               fill="#ff6b6b", outline="#a33", width=2)
        self.cv.create_text(140, 454, text="ボール（ドラッグ）", font=("Meiryo", 12), fill="#333")

        # 猫を描く（図形）
        self.draw_cat(self.cat_x, self.cat_y)

        # 説明
        self.ids["msg"] = self.cv.create_text(
            540, 90,
            text="猫が来た！ 猫をクリックで「なでる」／えさをクリックで「食べる」／ボールをドラッグして猫に当てると「遊ぶ」",
            font=("Meiryo", 12),
            fill="#333",
            width=680
        )

        self.draw_status()

    def draw_ending(self, ending_text):
        self.clear_all()
        self.scene = "ending"

        self.cv.create_rectangle(0, 0, W, H, fill="#121826", outline="")
        self.cv.create_text(W//2, 140, text="END", font=("Meiryo", 44, "bold"), fill="#ffffff")
        self.cv.create_text(W//2, 230, text=ending_text, font=("Meiryo", 18, "bold"), fill="#ffffff", width=760)

        # リスタートボタン
        self.ids["restart"] = self.cv.create_rectangle(W//2-130, 330, W//2+130, 390, fill="#ffffff", outline="#dddddd", width=2)
        self.cv.create_text(W//2, 360, text="もう一回（クリック）", font=("Meiryo", 16, "bold"), fill="#222")

        # 簡易ログ
        log = "なでる:{0}回  えさ:{1}回  あそぶ:{2}回  満足度:{3}".format(
            self.pet_count, self.feed_count, self.play_count, self.happy
        )
        self.cv.create_text(W//2, 440, text=log, font=("Meiryo", 12), fill="#cbd5e1")

    # -------------------------
    # 猫描画＆更新
    # -------------------------
    def draw_cat(self, x, y):
        # 体
        self.ids["cat_body"] = self.cv.create_oval(x-90, y-40, x+90, y+70, fill="#ffd6a5", outline="#caa07a", width=2)
        # 頭
        self.ids["cat_head"] = self.cv.create_oval(x-70, y-120, x+70, y-10, fill="#ffd6a5", outline="#caa07a", width=2)
        # 耳
        self.ids["ear_l"] = self.cv.create_polygon(x-55, y-105, x-90, y-150, x-20, y-125,
                                                   fill="#ffd6a5", outline="#caa07a", width=2)
        self.ids["ear_r"] = self.cv.create_polygon(x+55, y-105, x+90, y-150, x+20, y-125,
                                                   fill="#ffd6a5", outline="#caa07a", width=2)

        # 目（白目）
        self.ids["eye_l"] = self.cv.create_oval(x-40, y-75, x-10, y-45, fill="#ffffff", outline="#333", width=2)
        self.ids["eye_r"] = self.cv.create_oval(x+10, y-75, x+40, y-45, fill="#ffffff", outline="#333", width=2)

        # 黒目（後で視線追従）
        self.ids["pupil_l"] = self.cv.create_oval(x-30, y-65, x-20, y-55, fill="#111", outline="")
        self.ids["pupil_r"] = self.cv.create_oval(x+20, y-65, x+30, y-55, fill="#111", outline="")

        # 口
        self.ids["mouth"] = self.cv.create_arc(x-20, y-50, x+20, y-20, start=200, extent=140, style="arc", outline="#333", width=2)

        # しっぽ
        self.ids["tail"] = self.cv.create_line(x+85, y+35, x+140, y+0, x+170, y+40, smooth=True, width=10, fill="#ffd6a5")

        # 猫の当たり判定（透明の大きめ矩形）
        self.ids["cat_hit"] = self.cv.create_rectangle(x-120, y-170, x+180, y+120, outline="", fill="")
        self.cv.tag_raise(self.ids["cat_hit"])  # クリック判定を上に

        # 名前
        self.cv.create_text(x, y+95, text="ねこ", font=("Meiryo", 12, "bold"), fill="#333")

    def update_pupils(self):
        # 猫がボール（ドラッグ対象）を目で追う
        if self.scene != "cat":
            return

        x = self.cat_x
        y = self.cat_y

        # 目の中心
        elx = x - 25
        erx = x + 25
        ey = y - 60

        # 目線ベクトル（ボールの位置へ）
        dx_l = self.ball_x - elx
        dy_l = self.ball_y - ey
        dx_r = self.ball_x - erx
        dy_r = self.ball_y - ey

        # 正規化っぽくして、黒目の移動量を制限
        def clamp_pupil(dx, dy):
            # 距離が大きすぎるときの抑制
            limit = 8.0
            dist = (dx*dx + dy*dy) ** 0.5
            if dist < 1e-6:
                return 0.0, 0.0
            s = limit / dist
            if s > 1.0:
                s = 1.0
            return dx * s, dy * s

        px_l, py_l = clamp_pupil(dx_l, dy_l)
        px_r, py_r = clamp_pupil(dx_r, dy_r)

        # 黒目位置更新（左）
        self.cv.coords(self.ids["pupil_l"],
                       (elx-5)+px_l, (ey-5)+py_l,
                       (elx+5)+px_l, (ey+5)+py_l)
        # 右
        self.cv.coords(self.ids["pupil_r"],
                       (erx-5)+px_r, (ey-5)+py_r,
                       (erx+5)+px_r, (ey+5)+py_r)

    # -------------------------
    # UI（ステータス表示）
    # -------------------------
    def draw_status(self):
        # 右上にステータス
        #（重ね描きでもよいが、簡単のため毎回描き直す）
        text = "なでる:{0}  えさ:{1}  あそぶ:{2}  満足度:{3}".format(
            self.pet_count, self.feed_count, self.play_count, self.happy
        )
        self.ids["status_bg"] = self.cv.create_rectangle(520, 10, 890, 50, fill="#ffffff", outline="#cccccc")
        self.ids["status"] = self.cv.create_text(705, 30, text=text, font=("Meiryo", 12), fill="#111")

    def set_message(self, s):
        if "msg" in self.ids:
            self.cv.itemconfig(self.ids["msg"], text=s)

    # -------------------------
    # 反応ロジック
    # -------------------------
    def react_pet(self):
        self.pet_count += 1

        # 順序によるボーナス：先にえさ→なでるだと喜びやすい
        add = 8
        if self.last_action == "feed":
            add = 12
        if self.pet_count >= 6:
            # なで過ぎで「飽き」要素
            add = 3

        self.happy += add
        self.last_action = "pet"

        if self.pet_count <= 2:
            self.set_message("ゴロゴロ…（気持ちよさそう）")
        elif self.pet_count <= 5:
            self.set_message("にゃ〜（もっとなでて）")
        else:
            self.set_message("……（なで過ぎかも。ちょっと離れてほしい顔）")

        # 口を少し変える（簡易表情）
        self.cv.itemconfig(self.ids["mouth"], start=210, extent=120)

    def react_feed(self):
        self.feed_count += 1

        add = 10
        # 先になでる→えさだと「ごほうび感」で少し上がる
        if self.last_action == "pet":
            add = 13
        # 食べ過ぎ抑制
        if self.feed_count >= 4:
            add = 5

        self.happy += add
        self.last_action = "feed"

        if self.feed_count == 1:
            self.set_message("もぐもぐ…（食べ始めた）")
        elif self.feed_count == 2:
            self.set_message("にゃ！（おいしい）")
        else:
            self.set_message("…げふ（食べすぎ注意）")

        # えさの色を変えて「減った」っぽく見せる（形を小さく）
        if "food" in self.ids:
            if self.feed_count == 1:
                self.cv.coords(self.ids["food"], 478, 405, 522, 422)
            elif self.feed_count == 2:
                self.cv.coords(self.ids["food"], 485, 407, 515, 421)
            else:
                self.cv.coords(self.ids["food"], 495, 410, 505, 418)

    def react_play(self):
        self.play_count += 1

        add = 9
        # えさ直後の遊びはテンション落ちる
        if self.last_action == "feed":
            add = 5
        # なでる直後の遊びは上がる（かまってくれて嬉しい）
        if self.last_action == "pet":
            add = 11

        self.happy += add
        self.last_action = "play"

        if self.play_count == 1:
            self.set_message("にゃっ！（ボールに反応した）")
        elif self.play_count == 2:
            self.set_message("シャーッ…じゃなくて、テンション上がってきた！")
        else:
            self.set_message("はぁはぁ…（遊び疲れたけど満足）")

        # 口を変える
        self.cv.itemconfig(self.ids["mouth"], start=190, extent=160)

    def check_ending(self):
        # エンディング条件：満足度が一定以上
        if self.happy >= 60:
            # エンディング分岐：えさ多め or なで多め
            if self.feed_count >= 3:
                t = "おなかいっぱいでスヤァ…\n玄関で寝始めた。あなたの勝ち。"
            elif self.pet_count >= 6:
                t = "なでられすぎて塩対応になったが、最後は膝に乗ってきた。\nツンデレ勝利。"
            else:
                t = "たくさん遊んで信頼度MAX！\n『家に入っていい？』みたいな顔をしている。"
            self.draw_ending(t)

    # -------------------------
    # イベント処理
    # -------------------------
    def on_click(self, e):
        x = e.x
        y = e.y

        if self.scene == "ending":
            # リスタートボタン
            if "restart" in self.ids:
                x1, y1, x2, y2 = self.cv.coords(self.ids["restart"])
                if x1 <= x <= x2 and y1 <= y <= y2:
                    self.reset_game()
            return

        if self.scene == "entry":
            # 取っ手をクリックしたら開く
            if "knob" in self.ids:
                x1, y1, x2, y2 = self.cv.coords(self.ids["knob"])
                if x1 <= x <= x2 and y1 <= y <= y2:
                    self.door_open = True
                    self.draw_cat_scene()
            return

        if self.scene == "cat":
            # ボールクリックならドラッグ開始
            bx1, by1, bx2, by2 = self.cv.coords(self.ids["ball"])
            if bx1 <= x <= bx2 and by1 <= y <= by2:
                self.ball_drag = True
                return

            # えさ皿クリック
            bx1, by1, bx2, by2 = self.cv.coords(self.ids["bowl"])
            if bx1 <= x <= bx2 and by1 <= y <= by2:
                self.react_feed()
                self.draw_status()
                self.check_ending()
                return

            # 猫クリック（当たり判定）
            cx1, cy1, cx2, cy2 = self.cv.coords(self.ids["cat_hit"])
            if cx1 <= x <= cx2 and cy1 <= y <= cy2:
                self.react_pet()
                self.draw_status()
                self.check_ending()
                return

    def on_drag(self, e):
        if self.scene != "cat":
            return
        if not self.ball_drag:
            return

        # ボール移動
        self.ball_x = e.x
        self.ball_y = e.y

        # 画面外に行きすぎないよう制限
        if self.ball_x < 30:
            self.ball_x = 30
        if self.ball_x > W - 30:
            self.ball_x = W - 30
        if self.ball_y < 30:
            self.ball_y = 30
        if self.ball_y > H - 30:
            self.ball_y = H - 30

        self.cv.coords(self.ids["ball"],
                       self.ball_x-18, self.ball_y-18,
                       self.ball_x+18, self.ball_y+18)

        # 猫に当たったら遊び判定（近距離）
        dx = self.ball_x - self.cat_x
        dy = self.ball_y - (self.cat_y - 60)
        d2 = dx*dx + dy*dy
        if d2 <= 90*90:
            # 連続ヒットしすぎ防止：ドラッグ中1回だけ反応させる
            # ここでは、当たったらドラッグ終了扱いにして1回にする
            self.ball_drag = False
            self.react_play()
            self.draw_status()
            self.check_ending()

    def on_release(self, e):
        self.ball_drag = False

    def tick(self):
        # 目線更新
        self.update_pupils()
        self.root.after(50, self.tick)

    def reset_game(self):
        self.pet_count = 0
        self.feed_count = 0
        self.play_count = 0
        self.happy = 0
        self.last_action = ""
        self.ball_drag = False
        self.ball_x = 140
        self.ball_y = 420
        self.draw_entry()


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
