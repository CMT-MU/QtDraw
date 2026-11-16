---
orphan: true
---

# ユーザーガイド

英語版は[こちら](user_guide.md)です。

QtDraw を使った MultiPie の実践的なチュートリアルは [Tutorial via QtDraw](tutorial_multipie_qtdraw.pdf) にあります。

このガイドでは、**QtDraw** の図がどう作られているかを説明します。図の構成、データ表にある各オブジェクト、MultiPie を使った描画、Python コードからの使い方です。
メニュー、マウス、キーの操作は [はじめに](getting_started_ja.md) に、すべてのメソッドは [Python のコードからの利用](from_python_ja.md) にまとめてあります。

## 1. 全体像

### 図の構成

図は次の3つからなり、まとめて `.qtdw` ファイルに保存されます。

| 部分 | 内容 | 変更する場所 |
| --- | --- | --- |
| オブジェクト | サイト、ボンド、ベクトル、軌道など（19種類） | `DataSet` ウィンドウ（データ表） |
| 単位胞 | 結晶系、`a`、`b`、`c`、`alpha`、`beta`、`gamma`、原点 | 右側のパネル |
| 表示 | 範囲、繰り返し、クリップ、視線方向、軸と単位胞の表示 | 右側のパネル、`View` メニュー |

物質のファイル（`.cif`、`.vesta`、`.xsf`）も開けます。サイトとボンド（`.xsf` ならグリッドデータも）の図に変換されます。

### オブジェクトの位置

どのオブジェクトも `position` + `cell` の位置に置かれます。

- `position`：単位胞の**分数座標**で表した点。例：`[1/2,1/2,0]`
- `cell`：格子並進 `[n1,n2,n3]`。基本の単位胞なら `[0,0,0]`

オブジェクトの向き（ボンドやベクトルなど）は、分数座標でもデカルト座標でも与えられます。どちらにするかは `cartesian` 列で選びます。

### 範囲、繰り返し、クリップ

- `range`（`lower`、`upper`）：描く範囲。分数座標で与えます。
- `repeat`：すべてのオブジェクトを、範囲内のすべての格子並進の位置にも描きます。
- `clip`：範囲の外にはみ出た部分を切り取ります。
- `non-repeat`（`View` メニュー）：繰り返して描いたオブジェクトを、基本の単位胞のオブジェクトに戻します。

たとえば、立方晶の単位胞に置いた2つのサイトを 2 × 2 × 1 の範囲に繰り返すには：

```python
from qtdraw import QtDraw

win = QtDraw()
win.add_site(position="[0,0,0]", color="red")
win.add_site(position="[1/2,1/2,1/2]", color="blue")
win.set_range(lower="[0,0,0]", upper="[2,2,1]")
win.set_repeat(True)
```

## 2. データ表

### DataSet ウィンドウ

`e` キーか `DataSet` ボタンで `DataSet` ウィンドウが開きます。オブジェクトの種類ごとに、タブに分かれた表があります。

- `name` が同じオブジェクトは1つのグループになります。`name` のチェックボックスで、グループの表示と非表示を切り替えます。
- セルをダブルクリックすると編集できます。読み取れない値は受け付けません。
- 右クリックで行の挿入、コピー、削除ができます。
- 描画領域でオブジェクトを右クリックすると、その行を開く、隠す、削除することができます。

### 値の書き方

| 種類 | 例 | 注意 |
| --- | --- | --- |
| ベクトル | `[1/2,0,0]`、`[sqrt(3)/2,1/2,0]` | 数値または式 |
| 多項式 | `x*y`、`3z**2-r**2` | `x`、`y`、`z`、`r`（= $\sqrt{x^2+y^2+z^2}$）の式 |
| 色 | `red`、`darkseagreen` | 色の名前 |
| カラーマップ | `coolwarm`、`Wistia` | 軌道、ストリーム、等値面では、カラーマップも使えます |
| チェック | オン / オフ | 例：`cartesian`、`arrow1` |
| LaTeX | `$\alpha_1$` | ラベル、キャプション、2D テキストで使えます。MathJax で描かれます |

### すべてのオブジェクトに共通の列

| 列 | 意味 | 既定値 |
| --- | --- | --- |
| `name` | グループの名前。チェックボックスでグループの表示を切り替える | `untitled` |
| `label` | ラベルの文字列。チェックボックスでラベルを表示する | `label`（非表示） |
| `margin` | オブジェクトとラベルの間隔（ピクセル） | `3` |
| `position` | 分数座標での位置 | `[0,0,0]` |
| `cell` | 格子並進 | `[0,0,0]` |
| `opacity` | 0（透明）から 1 まで | `1.0` |

Python では、これらはすべての `add_*` メソッドのキーワード引数です。例：`win.add_site(name="Cu", label="Cu1", position="[0,0,0]")`。
以下、各オブジェクトに固有の列を説明します。

### 点と矢印

**site**：球。

| 列 | 意味 |
| --- | --- |
| `size` | 半径 |
| `color` | 色 |

```python
win.add_site(position="[1/2,0,0]", size=0.2, color="red")
```

**bond**：円柱。`position` は**中心**で、`direction` は一方の端から他方の端へのベクトルです。

| 列 | 意味 |
| --- | --- |
| `direction` | 始点（tail）から終点（head）へのベクトル |
| `width` | 半径 |
| `color`、`color2` | 始点側と終点側の半分の色 |
| `cartesian` | `direction` をデカルト座標で与えるか（オフなら分数座標） |

```python
win.add_bond(position="[1/2,0,0]", direction="[1,0,0]", color="red", color2="blue")
```

**vector**：`position` を通る矢印。

| 列 | 意味 |
| --- | --- |
| `direction` | 矢印の向き |
| `length` | 長さ。負の値なら \|`length`\| × `direction` のノルムを長さにする |
| `width` | 太さ |
| `offset` | 根元の位置。長さを単位にする（`-0.43` なら、矢印の中心がほぼ `position` に来る） |
| `color` | 色 |
| `cartesian` | `direction` をデカルト座標で与えるか（既定はオン） |
| `shaft R`、`tip R`、`tip length` | 矢印の形。`width` と `length` に対する比 |

```python
win.add_vector(position="[0,0,0]", direction="[1,1,0]", length=0.8, color="green")
```

**line**：`position` から `position` + `direction` までの線（または矢印）。

| 列 | 意味 |
| --- | --- |
| `direction` | 始点から終点へのベクトル |
| `width` | 太さ |
| `arrow1`、`arrow2` | 始点と終点の矢じり |
| `tip R`、`tip length` | 矢じりの形 |
| `color` | 色 |
| `cartesian` | `direction` をデカルト座標で与えるか |

```python
win.add_line(position="[0,0,0]", direction="[1,0,0]", arrow2=True)
```

### 球面上の関数

**orbital**：多項式 $f(x,y,z)$ に対する曲面 $r(\theta,\phi) \propto |f|$。色は別の多項式で付けられます。

| 列 | 意味 |
| --- | --- |
| `shape` | 形を決める多項式 $f$ |
| `surface` | 色を決める多項式（空なら `shape` と同じ） |
| `size` | 最大の半径。負の値なら、半径を \|`size`\| 倍する |
| `range` | $\theta$ と $\phi$ の範囲（度）。`[[0,180],[0,360]]` |
| `color` | 色、または `surface` の値に対するカラーマップ |

```python
win.add_orbital(position="[0,0,0]", shape="x*y", size=0.5, color="coolwarm")
```

**stream**：曲面の上に描いたベクトル場の矢印。

| 列 | 意味 |
| --- | --- |
| `shape` | 矢印を置く曲面の多項式（`1` なら球） |
| `vector` | ベクトル場の多項式 `[vx,vy,vz]` |
| `size` | 曲面の大きさ。負の値なら形を規格化する |
| `range` | $\theta$ と $\phi$ の範囲（度） |
| `division` | $\theta$ 方向と $\phi$ 方向の矢印の数 |
| `length`、`width`、`offset` | 各矢印の大きさ |
| `abs_scale` | 各矢印をベクトルの大きさに比例させるか |
| `color`、`component` | 色、または成分（`x`、`y`、`z`、`abs`）に対するカラーマップ |
| `shaft R`、`tip R`、`tip length` | 矢印の形 |

```python
win.add_stream(position="[0,0,0]", vector="[-y,x,0]", color="coolwarm", component="abs")
```

### 図形

**plane**：`position` を中心とする長方形。

| 列 | 意味 |
| --- | --- |
| `normal` | 法線ベクトル |
| `x_size`、`y_size` | 辺の長さ |
| `color` | 色 |
| `grid`、`grid_color`、`width` | 面上の格子線、その色と太さ |
| `cartesian` | `normal` をデカルト座標で与えるか |

```python
win.add_plane(position="[1/2,1/2,0]", normal="[0,0,1]", x_size=2, y_size=2, opacity=0.3)
```

**circle**：`position` を中心とする円板。

| 列 | 意味 |
| --- | --- |
| `normal` | 法線ベクトル |
| `size` | 半径 |
| `color` | 色 |
| `edge`、`edge_color`、`width` | 縁、縁の色と太さ |
| `cartesian` | `normal` をデカルト座標で与えるか |

```python
win.add_circle(position="[0,0,0]", normal="[1,0,0]", size=0.3)
```

**torus**：輪。

| 列 | 意味 |
| --- | --- |
| `normal` | 輪の軸 |
| `size` | 輪の半径 |
| `width` | 管の半径 |
| `color` | 色 |
| `cartesian` | `normal` をデカルト座標で与えるか |

```python
win.add_torus(position="[0,0,0]", size=0.5, width=0.1)
```

**ellipsoid**：`position` を中心とする楕円体。

| 列 | 意味 |
| --- | --- |
| `normal` | `z_size` の軸の向き |
| `x_size`、`y_size`、`z_size` | 3つの軸の方向の半径 |
| `color` | 色 |
| `cartesian` | `normal` をデカルト座標で与えるか |

```python
win.add_ellipsoid(position="[0,0,0]", x_size=0.5, y_size=0.3, z_size=0.2)
```

**toroid**：超楕円の輪。たとえば角の丸い四角の輪。

| 列 | 意味 |
| --- | --- |
| `normal` | 輪の軸 |
| `size`、`width` | 輪の半径と管の半径 |
| `x_scale`、`y_scale`、`z_scale` | 3つの軸の方向の拡大率 |
| `ring_shape`、`tube_shape` | 輪と管の形の指数（1 で丸、小さいほど四角、大きいほど尖る） |
| `color` | 色 |
| `cartesian` | `normal` をデカルト座標で与えるか |

```python
win.add_toroid(position="[0,0,0]", size=0.5, width=0.15, ring_shape=0.3)
```

**box**：`position` を1つの角とする平行六面体。

| 列 | 意味 |
| --- | --- |
| `a1`、`a2`、`a3` | 辺のベクトル |
| `color` | 色 |
| `edge`、`edge_color`、`width` | 辺、辺の色と太さ |
| `wireframe` | 辺だけを描くか |
| `cartesian` | 辺のベクトルをデカルト座標で与えるか（オフなら分数座標） |

```python
win.add_box(position="[0,0,0]", a1="[1,0,0]", a2="[0,1,0]", a3="[0,0,1/2]", opacity=0.3)
```

**polygon**：頂点と面で与える多面体。

| 列 | 意味 |
| --- | --- |
| `point` | 頂点。`position` からの相対位置 |
| `connectivity` | 面。各面は頂点の番号（0 から）のリスト |
| `color`、`edge`、`edge_color`、`width`、`wireframe` | box と同じ |
| `cartesian` | `point` をデカルト座標で与えるか（オフなら分数座標） |

```python
win.add_polygon(point="[[0,0,0],[1,0,0],[0,1,0],[0,0,1]]", connectivity="[[0,1,2],[0,1,3],[0,2,3],[1,2,3]]")
```

### 曲線

**spline**：点を滑らかに結ぶ曲線。

| 列 | 意味 |
| --- | --- |
| `point` | 曲線が通る点。`position` からの相対位置 |
| `width` | 太さ |
| `n_interp` | 補間する点の数 |
| `closed` | 閉じた曲線にするか |
| `natural` | 自然な端の条件にするか |
| `arrow1`、`arrow2`、`tip R`、`tip length` | 始点と終点の矢じり |
| `color` | 色 |
| `cartesian` | `point` をデカルト座標で与えるか |

```python
win.add_spline(point="[[0,0,0],[1,0,1],[0,1,2]]", arrow2=True)
```

**spline_t**：パラメータ `t` の関数で与える曲線。

| 列 | 意味 |
| --- | --- |
| `point` | `t` の関数 `[x(t),y(t),z(t)]` |
| `t_range` | `[t0,t1,dt]` |
| その他 | spline と同じ |

```python
win.add_spline_t(point="[cos(2 pi t), sin(2 pi t), t/2]", t_range="[0,2,0.02]")
```

### 文字

**text3d**：図の中に置く立体の文字。

| 列 | 意味 |
| --- | --- |
| `text` | 文字列 |
| `size` | 高さ |
| `view` | 文字を読む向き |
| `depth` | 厚み |
| `offset` | `position` からのずれ |
| `color` | 色 |

```python
win.add_text3d(position="[0,0,1]", text="Cu", size=0.3)
```

**caption**：複数の位置に置く文字。画面上の大きさは一定です。

| 列 | 意味 |
| --- | --- |
| `position` | キャプションごとの位置 `[[x1,y1,z1],[x2,y2,z2],...]` |
| `caption` | キャプション `[A,B,...]` |
| `size`、`bold`、`color` | 文字の大きさ、太字、色 |

```python
win.add_caption(position="[[0,0,0],[1,0,0]]", caption="[A,B]")
```

**text2d**：ウィンドウに固定した文字。たとえば題名。

| 列 | 意味 |
| --- | --- |
| `position` | ウィンドウ内の位置 `[x,y,0]`。`x` と `y` は 0 から 1 |
| `caption` | 文字列（LaTeX は `$...$`） |
| `size`、`color`、`font` | 文字の大きさ、色、フォント |

```python
win.add_text2d(caption=r"$E = \hbar\omega$", position="[0.05,0.9,0]", size=12)
```

### データ

**isosurface**：グリッドデータの等値面。たとえば `.xsf` ファイルの電荷密度。

| 列 | 意味 |
| --- | --- |
| `data` | グリッドデータのファイル（`.xsf`、または QtDraw が書いた辞書のファイル）。図のファイルからの相対パス |
| `value` | 等値面の値 `[v1,v2,...]` |
| `surface` | 面の色に使う別のデータの名前（空なら単色） |
| `color` | 色、または `surface` のデータに対するカラーマップ |
| `color_range` | カラーマップの範囲 |

```python
win.add_isosurface(data="Si.xsf", value="[0.05]", color="skyblue", opacity=0.5)
```

## 3. MultiPie を使った描画

[MultiPie](https://github.com/CMT-MU/MultiPie) は、点群と空間群（磁気群も含む）の対称操作と、対称性に適合した多極子基底（SAMB）を与えます。
これを使うと QtDraw は、対称性で等価なオブジェクトをまとめて描いたり、SAMB を描いたりできます。
QtDraw は MultiPie Ver.2（2.5 以降）と Ver.3 のどちらでも動きます。MultiPie がないときは、`MultiPie` ボタンがインストールを提案します。

### MultiPie ダイアログ

`MultiPie` ボタンでダイアログが開きます。
上部で、群の種類（PG、SG、MPG、MSG）、結晶系、群の名前を選びます。QtDraw の単位胞は、群の結晶系に合わせて変わります。
`Info.` のボタンで、対称操作、指標表、Wyckoff サイトとボンド、積表を表示できます。
ダイアログには3つのタブがあります。

| タブ | すること |
| --- | --- |
| **Group Info.** | 既約表現と調和関数の分解、調和関数、Wyckoff サイトとボンドの検索と描画、原子多極子、応答テンソル |
| **Object Drawing** | 代表のサイト、ボンド、ベクトル、軌道と等価なものをまとめて描く |
| **Basis Drawing** | サイト、ボンド、ベクトル、軌道のクラスターの SAMB を一覧にし、その1つ、線形結合、または複数の単位胞にわたる変調（空間群のみ）を描く |

描かれるのは普通のオブジェクトなので、ほかのオブジェクトと同じようにデータ表で編集できます。

### サイト、ボンド、ベクトル、軌道の与え方

| 対象 | 形式 | 例 |
| --- | --- | --- |
| サイト | `[x,y,z]` | `[1/3,2/3,0]` |
| ボンド | `[x0,y0,z0];[x1,y1,z1]`（始点;終点）、`[X,Y,Z]@[x,y,z]`（ベクトル@中心）、`[x0,y0,z0]:[X,Y,Z]`（始点:ベクトル） | `[2/3,1/3,0];[1/3,2/3,0]` |
| ベクトル | `[X,Y,Z] # サイトまたはボンド` | `[0,0,1] # [1/3,2/3,0]` |
| 軌道 | `多項式 # サイトまたはボンド` | `x*y # [0,0,0]` |

### Python から

群はタグで指定します。例：`D6h`（点群）、`D6h^1`（空間群）、`MPG:1.1.1`、`MSG:123.345`（磁気群）。
`mp_*` メソッドで、ダイアログと同じことができます。

```python
from qtdraw import QtDraw

win = QtDraw()
win.mp_set_group("D6h^1")  # graphene.
win.mp_add_site("[1/3,2/3,0]")  # equivalent sites.
win.mp_add_bond("[2/3,1/3,0];[1/3,2/3,0]")  # equivalent bonds.

lst = win.mp_site_samb_list("[1/3,2/3,0]")  # SAMBs of the site cluster.
print(lst)
win.mp_add_site_samb(lst[1])  # draw one of them.
```

ベクトルと軌道の SAMB は、タグ（例：`Q01`）、タグの線形結合（例：`Q02+G01`）、または変調で描きます。

```python
lst = win.mp_vector_samb_list("[1/3,2/3,0]", "M")  # magnetic-dipole SAMBs, {type: [tags]}.
win.mp_add_vector_samb("M01")
win.mp_add_vector_samb_modulation("[[M01, 1, [1/2,0,0], cos]] : [2,2,1]")  # [[tag, coefficient, k, cos/sin]] : cells.
```

変調には空間群の格子並進が必要です。点群で使うと、警告を出して無視されます。
ほかの例：[グラフェン](examples/mp_graphene.ipynb)、[Te](examples/mp_Te.ipynb)、[すべての mp_* メソッド](examples/multipie.ipynb)。

## 4. Python コードからの使い方

### 3つの使い方

| 使い方 | 用途 |
| --- | --- |
| `QtDraw()` | QtDraw のウィンドウ。スクリプトや Jupyter ノートブックから描く |
| `PyVistaWidget()` | 描画領域だけ。たとえば自分の Qt アプリケーションに組み込む |
| `create_qtdraw_file(filename, callback)` | ウィンドウを出さずに `.qtdw` ファイルを書く（バックグラウンドの処理） |

`add_*` の引数はデータ表の列と同じで、文字列か数値で与えます。省いた引数（または `None`）には既定値が使われます。

### スクリプト

```python
from qtdraw import QtDraw

win = QtDraw()
win.set_crystal("hexagonal")
win.set_unit_cell({"a": 2.46, "c": 6.7})
win.add_site(position="[1/3,2/3,0]", size=0.2, label="C1")
win.add_site(position="[2/3,1/3,0]", size=0.2, label="C2")
win.add_bond(position="[1/2,1/2,0]", direction="[1/3,-1/3,0]")  # C1-C2.
win.set_view([0, 0, 1])  # view along c.
win.save("graphene.qtdw")
win.pyvista_widget.save_screenshot("graphene.png")  # the drawing area of the window.
win.exec()  # in a script, show the window until it is closed (not needed in Jupyter).
```

### ウィンドウを出さずに

```python
from qtdraw import create_qtdraw_file


def draw(widget):
    for i in range(8):
        widget.add_site(position=f"[{i/8},0,0]", size=0.05)


create_qtdraw_file(filename="chain.qtdw", callback=draw)
```

### よく使うメソッド

| メソッド | すること |
| --- | --- |
| `set_crystal`、`set_unit_cell`、`set_origin` | 単位胞 |
| `set_range`、`set_repeat`、`set_clip`、`set_nonrepeat` | 範囲、繰り返し、クリップ |
| `set_view`、`set_parallel_projection`、`set_axis`、`set_cell`、`set_grid` | 表示 |
| `set_model` | モデルの名前 |
| `load`、`save` | ファイル |
| `save_screenshot` | 図の画像（`.png`、`.pdf`、`.svg` など）。`PyVistaWidget` のメソッドなので、`QtDraw` からは `win.pyvista_widget.save_screenshot(...)` |
| `clear_data` | すべてのオブジェクトを消す |
| `update_preference` | 設定。例：`update_preference("label", "default_check", True)` でラベルを表示する |
| `undo`、`redo` | 履歴（`QtDraw` のみ） |

すべてのメソッドは [Python のコードからの利用](from_python_ja.md) に、ほかの例は [例](example_ja.md) にあります。
