---
orphan: true
---

# Python のコードからの利用

英語版は[こちら](from_python.md)です。

**QtDraw** と **PyVistaWidget** は、Python のコードから使えます。
オブジェクトを描くために、次の API が使えます。

## 元に戻す・やり直す

`QtDraw` は、`Edit` メニューと同じように、ドキュメント（オブジェクト、単位胞、範囲、MultiPie の群）の履歴を保持します。
`undo()` と `redo()` でこの履歴の中を移動し、`can_undo()` と `can_redo()` でそれができるかどうかがわかります。

```python
qtdraw.add_site(name="A")
qtdraw.add_bond(name="B")  # the same cell: one step together with the site.
qtdraw.undo()  # removes both.
```

変更は、そのあとにイベントループが回ったときに記録されます。そのため、Jupyter の一つのセルや一つの関数の中での呼び出しは、一つのステップになります。
呼び出し自身がイベントループを回す場合（例えばダイアログや `processEvents()`）は、いくつかのステップに分かれることがあります。
`PyVistaWidget` を単独で使う場合は、履歴はありません。

## ファイルとディレクトリ

`load()` と `save()` は、カレントディレクトリを変更しません。これらに与えるファイル名は、カレントディレクトリからの相対パスです。
等値面のデータファイル（例えば `add_isosurface(data="grid.dat")`）は、描画ファイルを読み込むか保存したあとはそのファイルのディレクトリからの相対パス、それより前はカレントディレクトリからの相対パスです。

## QtDraw の API

API の一覧は英語版の [Usage from Python code](from_python.md) の「API in QtDraw」を参照してください。

## PyVistaWidget の API

API の一覧は英語版の [Usage from Python code](from_python.md) の「API in PyVistaWidget」を参照してください。
